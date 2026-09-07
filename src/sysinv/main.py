from .helpers import run_command
from .platform_info import detect_platform
from .software import detect_software


def main():
    print(run_command(["system_profiler", "SPApplicationsDataType", "-json"]))


main()
