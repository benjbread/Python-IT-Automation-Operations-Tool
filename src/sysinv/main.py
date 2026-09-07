from .platform_info import detect_platform
from .software import detect_software


def main():
    detect_software(detect_platform())


main()
