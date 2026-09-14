from pycaw.pycaw import AudioUtilities


def get_volume_interface():
    """
    Get Windows master audio volume interface.
    Compatible with newer pycaw versions.
    """

    devices = AudioUtilities.GetSpeakers()

    # New pycaw API
    if hasattr(devices, "EndpointVolume"):
        return devices.EndpointVolume

    # Older pycaw API fallback
    if hasattr(devices, "Activate"):
        from pycaw.pycaw import IAudioEndpointVolume
        from comtypes import CLSCTX_ALL

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        return interface.QueryInterface(
            IAudioEndpointVolume
        )

    raise RuntimeError(
        "Unable to access Windows audio volume interface."
    )


def get_volume():
    """
    Get current system volume and mute status.
    """

    try:
        volume = get_volume_interface()

        current = volume.GetMasterVolumeLevelScalar()
        muted = volume.GetMute()

        return {
            "success": True,
            "volume": f"{round(current * 100)}%",
            "muted": bool(muted),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def set_volume(level: int):
    """
    Set computer master volume.
    Level must be between 0 and 100.
    """

    try:
        level = max(0, min(100, int(level)))

        volume = get_volume_interface()

        volume.SetMasterVolumeLevelScalar(
            level / 100.0,
            None
        )

        return {
            "success": True,
            "volume": f"{level}%",
            "message": f"Volume set to {level}%.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def increase_volume(amount: int = 10):
    """
    Increase computer volume.
    """

    try:
        amount = max(1, int(amount))

        volume = get_volume_interface()

        current_level = (
            volume.GetMasterVolumeLevelScalar() * 100
        )

        new_level = min(
            100,
            round(current_level) + amount
        )

        volume.SetMasterVolumeLevelScalar(
            new_level / 100.0,
            None
        )

        return {
            "success": True,
            "volume": f"{new_level}%",
            "message": f"Volume increased to {new_level}%.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def decrease_volume(amount: int = 10):
    """
    Decrease computer volume.
    """

    try:
        amount = max(1, int(amount))

        volume = get_volume_interface()

        current_level = (
            volume.GetMasterVolumeLevelScalar() * 100
        )

        new_level = max(
            0,
            round(current_level) - amount
        )

        volume.SetMasterVolumeLevelScalar(
            new_level / 100.0,
            None
        )

        return {
            "success": True,
            "volume": f"{new_level}%",
            "message": f"Volume decreased to {new_level}%.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def mute_volume():
    """
    Mute computer volume.
    """

    try:
        volume = get_volume_interface()

        volume.SetMute(1, None)

        return {
            "success": True,
            "muted": True,
            "message": "Computer muted.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def unmute_volume():
    """
    Unmute computer volume.
    """

    try:
        volume = get_volume_interface()

        volume.SetMute(0, None)

        return {
            "success": True,
            "muted": False,
            "message": "Computer unmuted.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }