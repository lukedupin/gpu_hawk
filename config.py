def config():
    return {
        "cards": ["card0"],
        "update_rate": 5,
        "fan": {
            "enable": "/sys/class/drm/CARD/device/hwmon/hwmon3/pwm1_enable",
            "control": "/sys/class/drm/CARD/device/hwmon/hwmon3/pwm1",
            "start": 0.2,
            "step": 0.01,
            "alert": 0.80,
            "range": (0.2, 0.95),
            "hw_range": (0, 255),
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