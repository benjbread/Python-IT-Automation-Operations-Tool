import platform
import subprocess


def run_command(command_list: list[str]) -> dict:
    try:
        result = subprocess.run(
            command_list, capture_output=True, text=True, check=True, timeout=60
        )
        result_dict = {"success": True, "data_or_reason": result.stdout}
        return result_dict
    except subprocess.CalledProcessError as err:
        result_dict = {
            "success": False,
            "data_or_reason": f"{err.cmd} failed: {err.stderr}",
        }
        return result_dict
    except subprocess.TimeoutExpired as err:
        result_dict = {
            "success": False,
            "data_or_reason": f"Process timed out after: {err.timeout} seconds",
        }
        return result_dict


def detect_platform() -> str:
    return platform.system()


def detect_software(OS: str) -> dict:
    # Create empty list that will hold dict of name, version, and publisher for each installed software
    software_list: list[dict] = []

    # Create empty result dict that will hold wether it was a success (bool) and the data_or_reason and be returned
    result_dict: dict = {}

    # If the platform (OS) is Windows
    if OS == "Windows":
        import winreg as wrg

        index: int = 0
        opened_uninstall = wrg.OpenKey(
            wrg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        )

        try:
            while True:
                software_info: dict = {}
                program_index = wrg.EnumKey(opened_uninstall, index)
                opened_program_subkey = wrg.OpenKey(opened_uninstall, program_index)

                try:
                    software_info["name"] = (
                        wrg.QueryValueEx(opened_program_subkey, "DisplayName")
                    )[0]
                except OSError:
                    software_info["name"] = "Missing Name"

                try:
                    software_info["version"] = (
                        wrg.QueryValueEx(opened_program_subkey, "DisplayVersion")
                    )[0]
                except OSError:
                    software_info["version"] = "Missing Version"

                try:
                    software_info["publisher"] = (
                        wrg.QueryValueEx(opened_program_subkey, "Publisher")
                    )[0]
                except OSError:
                    software_info["publisher"] = "Missing Publisher"

                finally:
                    software_list.append(software_info)
                    wrg.CloseKey(opened_program_subkey)
                    index += 1

        except OSError:
            wrg.CloseKey(opened_uninstall)
            if len(software_list) == 0:
                result_dict["success"] = False
                result_dict["data_or_reason"] = "No Software discovered"
            else:
                result_dict["success"] = True
                result_dict["data_or_reason"] = software_list
            return result_dict
    # Otherwise, if the platform (OS) is Linux
    elif OS == "Linux":
        # Create a dict from run_command
        command_dict: dict = run_command(
            ["dpkg-query", "-W", "-f=${Package}\t${Version}\t${Maintainer}\n"]
        )

        if command_dict["success"]:
            # Create list from the data_or_reason key of command_dict split by newlines
            data_list: list = command_dict["data_or_reason"].split("\n")

            # For each list in the data_list split it into a new list of name, version, and publisher
            # Then create a software info dict from the items in the list which is appended to the software list
            for data in data_list:
                if len(data) >= 1:
                    software = data.split("\t")
                    software_info = {}
                    software_info["name"] = software[0]

                    try:
                        software_info["version"] = software[1]
                    except IndexError:
                        software_info["version"] = "Error Retrieving"

                    try:
                        software_info["publisher"] = software[2]
                    except IndexError:
                        software_info["publisher"] = "Error Retrieving"

                    software_list.append(software_info)

            result_dict["success"] = True
            result_dict["data_or_reason"] = software_list
            return result_dict
        else:
            result_dict["success"] = False
            result_dict["data_or_reason"] = command_dict["data_or_reason"]
            return result_dict
    # If the platform (OS) is Darwin (macOS)
    elif OS == "Darwin":
        import json

        command_dict = run_command(
            ["system_profiler", "SPApplicationsDataType", "-json"]
        )
        if command_dict["success"]:
            json_data = json.loads(command_dict["data_or_reason"])
            json_list = json_data.get("SPApplicationsDataType")

            for software in json_list:
                software_dict: dict = {}
                software_dict["name"] = software.get("_name")
                software_dict["version"] = software.get("version")
                software_dict["publisher"] = software.get("obtained_from")
                software_list.append(software_dict)

            result_dict["success"] = True
            result_dict["data_or_reason"] = software_list
            return result_dict
        else:
            result_dict["success"] = False
            result_dict["data_or_reason"] = command_dict["data_or_reason"]
            return result_dict
    # Else the OS isnt supported yet
    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS net yet implemented"
        return result_dict


def main():
    print(detect_software(detect_platform()))


main()
