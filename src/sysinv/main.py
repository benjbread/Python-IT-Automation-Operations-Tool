from .platform_info import detect_platform
from .services import detect_services
from .software import detect_software


def main():
    print(detect_services(detect_platform()))


main()
