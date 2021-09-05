import datetime, calendar, math, zipfile, os, re, pytz, smtplib, pickle, pytz, base64
from django.conf import settings
from django.utils.timezone import utc

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException

from tzwhere import tzwhere

from email.mime.text import MIMEText


def sendSms( body, to ):
    try:
        client = Client( settings.TWILIO_SMS['ACCOUNT_SID'],
                         settings.TWILIO_SMS['AUTH_TOKEN'] )

        message = client.messages.create(body=body, to=to,
                                         from_=settings.TWILIO_SMS['PHONE_NUMBER'])

    except TwilioException as e:
        print(e)
        return None

    except TwilioRestException as e:
        print(e)
        return None

    return message.sid


def sendEmail( to_email, subject, body ):
    message = Mail(
        from_email=settings.SEND_GRID['FROM_EMAIL'],
        to_emails=to_email,
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(settings.SEND_GRID['API_KEY'])
        response = sg.send(message)
        #print(response.status_code)
        #print(response.body)
        #print(response.headers)
    except Exception as e:
        print(e.message)
        return None

    return response

def sendGmail( recipient, sender, subject, body ):
    scopes = ['https://www.googleapis.com/auth/gmail.send']
    pickle_filename = settings.BASE_DIR +'/pysite/gmail_token.pickle'
    secret_filename = settings.BASE_DIR +'/pysite/gmail_secret.json'

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists(pickle_filename):
        with open( pickle_filename, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        request_token = True
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                request_token = False
            except RefreshError:
                print("Refresh error")

        # Request a new token
        if request_token:
            flow = InstalledAppFlow.from_client_secrets_file( secret_filename, scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(pickle_filename, 'wb') as token:
            pickle.dump(creds, token)

    # Create my service
    service = build('gmail', 'v1', credentials=creds)

    # Create my simple mime type
    message = MIMEText(body)
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject

    # Base 64 encode
    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    gmail_msg = {'raw': b64_string}

    # Send out the message
    result = (service.users().messages().send(userId='me', body=gmail_msg).execute())
    return True


def xlist( ary ):
    return list(ary) if ary is not None else []


def xtuple( tup ):
    return tuple(tup) if tup is not None else tuple()


def xstr( s, none='' ):
    return str(s) if s is not None else none


def xint( s, none=0, undefined=None ):
    try:
      if s == "undefined":
        return undefined
      return int(s) if s is not None and s != 'NaN' else none
    except ValueError:
        #Floating points and trailing letters wont fool me!!!
        m = re.search('^[-+]?[0-9]+', s)
        if m:
            return int(m.group(0))

        #can't go any further
        return none
    except TypeError:
        return none


def xfloat( s, none=0.0, undefined=None ):
    try:
        if s == "undefined":
            return undefined
        f = float(s) if s is not None and s != 'NaN' else none
        if math.isnan(f):
            return none
        return f
    except ValueError:
        #trailing letters wont fool me!!!
        m = re.search('^[-+]?[0-9]*\.?[0-9]+', s )
        if m:
            return float(m.group(0))

        #Can't go any further
        return none
    except TypeError:
        return none


def xbool( s, none=False, undefined=False ):
    #Are we string? try to figure out what that means
    if isinstance( s, str ):
        s = s.lower()
        if s == 'true':
            return True
        elif s == 'none' or s == 'null':
            return none
        elif s == 'undefined':
            return undefined
        else:
            return False

    #Special case none
    elif s is None:
        return none
    else:
        return bool(s)

def xlen( x, none=0 ):
    return len(x) if x is not None else none

# Cap a value between the given bounds
def cap( val, high, low=None ):
    if not low:
        low = -high
    if val > high:
        val = high
    elif val < low:
        val = low

    return val


# Careful, this is SUPER SLOW
def calculateTimezone( lat, lng ):
    return tzwhere.tzwhere().tzNameAt( lat, lng )


# Provide a timezone
def toTimezone( tz=None ):
    timezone = utc
    if tz is not None:
        try:
            timezone = pytz.timezone(str(tz))
        except pytz.UnknownTimeZoneError:
            pass

    return timezone


# Return the hour differnce between two timezones
def tzToTz( to_tz, from_tz=None ): # None means UTC
    return round((unixNow(None, to_tz) - unixNow(None, from_tz)) / 3600000) # Hours


# Get the current time
def timeNow( ms=None, tz=None ):
    # Give the user their info
    ts = datetime.datetime.now( toTimezone(tz) )
    if ms:
        return ts + datetime.timedelta(milliseconds=xint(ms))
    else:
        return ts


# Return the single day value
def yearDay( dt ):
    return (dt.year - 2000) * 400 + dt.timetuple().tm_yday


# Convert a time to different timezone
def timeToTz( ts, tz ):
    return ts + datetime.timedelta(hours=tzToTz( tz )) - datetime.timedelta(hours=tzToTz("UTC", ts.tzinfo))


# Convert a time into epoch format
def timeToUnix( ts ):
    #print("%d == %d" % (int(ts.timestamp() * 1000.0), int(calendar.timegm( ts.timetuple()) * 1000)))

    return int(ts.timestamp() * 1000.0) if ts else 0
    #return (float(calendar.timegm( ts.timetuple())) * 1000.0) if ts else 0


# convert date to string readable
def dateToStr( date ):
    if date is None:
        return "0-0-0"
    return "%d-%d-%d" % (date.month, date.day, date.year)


# Current time in epoch format
def unixNow( ms=None, tz=None ):
    return timeToUnix( timeNow( ms, tz ) )


# Convert a time to different timezone
def unixToTz( unix, tz, from_tz="UTC" ):
    return unix + (tzToTz( tz ) - tzToTz("UTC", from_tz)) * 3600000


# Convert an epoch format into time
def unixToTime( ms, tz=None ):
    timezone = toTimezone(tz)
    return datetime.datetime.fromtimestamp( xfloat(ms) / 1000.0 ).replace(tzinfo=timezone)


# Check if a timestamp is in range
def timeInRange( ts, ms_range, center_ts=None ):
    if ts is None:
        return False

    return unixInRange( timeToUnix(ts), ms_range, center_ts )


# True if one date is within range of another
def unixInRange( unix_ts, ms_range, center_ts=None ):
    unix_ts = xint( unix_ts )
    if center_ts is None:
        center_ts = unixNow()

    return unix_ts < center_ts + ms_range and unix_ts > center_ts - ms_range


def deltaToSeconds( d, digits=None ):
    ts = d.days * 86400000.0 + float(d.seconds) + float(d.microseconds / 1000.0)
    if digits:
        return round( math.fabs( ts ), digits )
    else:
        return math.fabs( ts )


# Day of year to date
def doyToDate( doy ):
    return datetime.datetime( int(doy / 400) + 2000, 1, 1 ) + datetime.timedelta( (doy % 400) - 1 )


def humanDate( date=None, add_sec=0, force_hours=False, force_full=False ):
    if date is None:
        date = timeNow()

    if isinstance( date, datetime.datetime ):
        return date.strftime( "%m/%d/%Y %I:%M:%S%p" )
    elif isinstance( date, datetime.timedelta ):
        date = int( deltaToSeconds( date ))

    # Return the delta
    date = int(date) + add_sec
    if date >= 3600 or force_full:
        return "%d:%02d:%02d" % (int(date / 3600), int((date / 60) % 60), int(date % 60))
    elif date >= 60:
        if force_hours:
            return "00:%02d:%02d" % (int((date / 60) % 60), int(date % 60))
        else:
            return "%d:%02d" % (int((date / 60) % 60), int(date % 60))
    elif date > 1:
        return "%d seconds" % int(date % 60)
    elif date == 1:
        return "%d second" % int(date % 60)
    else:
        return '0'


def getDayOfWeekOffset( ts, day ):
    for offset in range(7):
        if ts.replace(day=(offset + 1)).weekday() == day:
            return offset

    return None
