from .helpers import run_command
from .platform_info import detect_platform
from .software import detect_software


def main():
    print(detect_software("Darwin"))


main()
