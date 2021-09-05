def config():
    return {
        "cards": ["card0"],
        "fan": {
            "enable": "/sys/class/drm/CARD/device/hwmon/hwmon3/pwm1_enable",
            "control": "/sys/class/drm/CARD/device/hwmon/hwmon3/pwm1",
            "alert": 0.80,
            "stop": 0.95,
            "range": (0, 255)
        },
        "temps": [
            {
                "name": "GPU",
                "path": "/sys/class/drm/CARD/device/hwmon/hwmon3/temp2_input",
                "target": 60.0,
                "limit": 80.0,
            },
            {
                "name": "VRAM",
                "path": "/sys/class/drm/CARD/device/hwmon/hwmon3/temp3_input",
                "target": 80.0,
                "limit": 95.0,
            },
        ]
    }