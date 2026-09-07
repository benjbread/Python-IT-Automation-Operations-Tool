import platform


# Function to get the platform (OS) for machine running program
def detect_platform() -> str:
    return platform.system()
