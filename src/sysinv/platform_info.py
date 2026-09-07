import platform


def detect_platform() -> str:
    return platform.system()
