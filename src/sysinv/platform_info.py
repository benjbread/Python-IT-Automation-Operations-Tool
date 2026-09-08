import platform


# Function to get the platform (OS) for the machine running program
# platform.system() returns canonical OS names like Windows, Linux, Darwin
def detect_platform() -> str:
    return platform.system()
