from .helpers import run_command


# returns a dict of wether function succeeded or not, and then the data_or_reason
def detect_software(OS: str) -> dict:
    # Create empty list that will hold dict of name, version, and publisher for each installed software
    software_list: list[dict] = []

    # Create empty result dict that will hold wether it was a success (bool) and the data_or_reason and be returned
    result_dict: dict = {}

    # If the platform (OS) is Windows
    if OS == "Windows":
        import winreg as wrg

        # create index counter to go through the software subkeys
        index: int = 0
        # Open the Uninstall key which holds the software subkeys
        opened_uninstall = wrg.OpenKey(
            wrg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        )

        try:
            while True:
                # Create empty dict on each loop to eventually hold the software info
                software_info: dict = {}
                # Get back the program subkey at the index for that loop
                program_index = wrg.EnumKey(opened_uninstall, index)
                # Open the program subkey for this loop
                opened_program_subkey = wrg.OpenKey(
                    opened_uninstall, program_index
                )
                print(opened_program_subkey)

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
                finally:
                    software_list.append(software_info)
                    # Close the opened program subkey
                    wrg.CloseKey(opened_program_subkey)
                    # Increment the index
                    index += 1

        # Once index has reached value that doesnt exist it means we have reached end of subkeys and OSError is raised.
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
            # return the final dict of wether function succeeded or not, and then the data_or_reason
            return result_dict

    # Otherwise, if the platform (OS) is Linux
    elif OS == "Linux":
        # Create a dict from run_command using dpkg
        command_dict: dict = run_command(
            ["dpkg-query", "-W", "-f=${Package}\t${Version}\t${Maintainer}\n"]
        )

        # if the command ran was sucessful run this
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

            # Once all software_info has been appened to software_list set the result to a success
            # and add list to the data_or_reason key of result dict
            result_dict["success"] = True
            result_dict["data_or_reason"] = software_list
            return result_dict
        # If inital command didnt suceed then set sucess to false and provide reason
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

        # if the command ran was sucessful run this
        if command_dict["success"]:
            # Create dict from the json returned in the data_or_reason key from command_dict
            json_data = json.loads(command_dict["data_or_reason"])
            # Get the value from the jason_data dict with the list of dicts for each software
            json_list = json_data.get("SPApplicationsDataType")

            # for each software in the list from json_list...
            for software in json_list:
                # make a temporary software_dict to hold the values
                software_dict: dict = {}
                # get the softwares "name" and set it to the "name" key in software_dict
                software_dict["name"] = software.get("_name")
                # get the softwares "version" and set it to the "version" key in software_dict
                software_dict["version"] = software.get("version")
                # get the softwares "obtained_from" and set it to the "publisher" key in software_dict
                software_dict["publisher"] = software.get("obtained_from")
                # append the temporary dict the the software_list
                software_list.append(software_dict)

            # after each software has been iterated through set success to True
            # and make the software_list the value for data_or_reason in dict
            result_dict["success"] = True
            result_dict["data_or_reason"] = software_list
            return result_dict
        # If inital command didnt suceed then set sucess to False and provide reason
        else:
            result_dict["success"] = False
            result_dict["data_or_reason"] = command_dict["data_or_reason"]
            return result_dict

    # Else the OS isnt supported yet
    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS not yet implemented"
        return result_dict
