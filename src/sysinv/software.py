from .helpers import run_command


# Returns a dict of whether function succeeded and the data_or_reason
def detect_software(OS: str) -> dict:
    # Create empty list that will hold dict of name, version, and publisher for each installed software
    software_list: list[dict] = []

    # Create empty result dict that will hold whether it was a success (bool)
    # and the data_or_reason value to be returned
    result_dict: dict = {}

    # If the platform (OS) is Windows
    if OS == "Windows":
        import winreg as wrg

        # Create index counter to iterate through software subkeys
        index: int = 0
        # Open the Uninstall key which holds the software subkeys
        opened_uninstall = wrg.OpenKey(
            wrg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        )

        try:
            # Loop continues until EnumKey raises OSError when no more subkeys are left
            while True:
                # Create empty dict on each loop to eventually hold the software info
                software_info: dict = {}
                # Get back the program subkey at the index for that loop
                program_index = wrg.EnumKey(opened_uninstall, index)
                # Open the program subkey for this loop
                opened_program_subkey = wrg.OpenKey(
                    opened_uninstall, program_index
                )

                # try to set the name key for software_info dict from the opened subkeys "DisplayName"
                try:
                    software_info["name"] = (
                        wrg.QueryValueEx(opened_program_subkey, "DisplayName")
                    )[0]
                # if the "DisplayName" value is missing then say so
                except OSError:
                    software_info["name"] = "Missing Name"

                # try to set the version key for software_info dict from the opened subkeys "DisplayVersion"
                try:
                    software_info["version"] = (
                        wrg.QueryValueEx(
                            opened_program_subkey, "DisplayVersion"
                        )
                    )[0]
                # if the "DisplayVersion" value is missing then say so
                except OSError:
                    software_info["version"] = "Missing Version"

                # try to set the publisher key for software_info dict from the opened subkeys "Publisher"
                try:
                    software_info["publisher"] = (
                        wrg.QueryValueEx(opened_program_subkey, "Publisher")
                    )[0]
                # if the "Publisher" value is missing then say so
                except OSError:
                    software_info["publisher"] = "Missing Publisher"

                # After trying to assign each software_info key append the dict to the list of softwares
                # finally block guarantees append + close + increment happen even if one field lookup fails
                finally:
                    software_list.append(software_info)
                    # Close the opened program subkey
                    wrg.CloseKey(opened_program_subkey)
                    # Increment the index
                    index += 1

        # Once index reaches a value that does not exist, EnumKey raises OSError
        # which signals we reached the end of subkeys
        except OSError:
            # Close the opened Uninstall Key
            wrg.CloseKey(opened_uninstall)
            # If the software_list is empty at the end
            if len(software_list) == 0:
                result_dict["success"] = False
                result_dict["data_or_reason"] = "No Software discovered"
            # If the software_list is populated
            else:
                result_dict["success"] = True
                result_dict["data_or_reason"] = software_list
            # Return final dict showing whether function succeeded and the data_or_reason
            return result_dict

    # Otherwise, if the platform (OS) is Linux
    elif OS == "Linux":
        # Create a dict from run_command using dpkg
        command_dict: dict = run_command(
            ["dpkg-query", "-W", "-f=${Package}\t${Version}\t${Maintainer}\n"]
        )

        # If the command ran successfully, parse output lines
        if command_dict["success"]:
            # Create list from the data_or_reason key of command_dict split by newlines
            data_list: list = command_dict["data_or_reason"].split("\n")

            # For each line in data_list split by tab into name/version/publisher fields
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

            # Once all software_info entries are appended, set result to success
            # and add list to the data_or_reason key of result dict
            result_dict["success"] = True
            result_dict["data_or_reason"] = software_list
            return result_dict
        # If initial command did not succeed, set success to False and provide reason
        else:
            result_dict["success"] = False
            result_dict["data_or_reason"] = command_dict["data_or_reason"]
            return result_dict

    # If the platform (OS) is Darwin (macOS)
    elif OS == "Darwin":
        import json

        # Create a dict from run_command using system_profiler
        command_dict = run_command(
            ["system_profiler", "SPApplicationsDataType", "-json"]
        )

        # If the command ran successfully, parse returned JSON
        if command_dict["success"]:
            # Create dict from the json returned in the data_or_reason key from command_dict
            json_data = json.loads(command_dict["data_or_reason"])
            # Get the value from the json_data dict with the list of dicts for each software
            json_list = json_data.get("SPApplicationsDataType")

            # for each software in the list from json_list...
            # .get() is used so missing keys return None instead of raising KeyError
            for software in json_list:
                # Make a temporary software_dict to hold values for one software item
                software_dict: dict = {}
                # Get software name and set it to the "name" key in software_dict
                software_dict["name"] = software.get("_name")
                # Get software version and set it to the "version" key in software_dict
                software_dict["version"] = software.get("version")
                # Get software obtained_from and set it to the "publisher" key in software_dict
                software_dict["publisher"] = software.get("obtained_from")
                # Append the temporary dict to software_list
                software_list.append(software_dict)

            # After each software item is processed, set success to True
            # and make the software_list the value for data_or_reason in dict
            result_dict["success"] = True
            result_dict["data_or_reason"] = software_list
            return result_dict
        # If initial command did not succeed, set success to False and provide reason
        else:
            result_dict["success"] = False
            result_dict["data_or_reason"] = command_dict["data_or_reason"]
            return result_dict

    # Else the OS is not supported yet
    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS not yet implemented"
        return result_dict
