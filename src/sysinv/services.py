from .helpers import run_command


def detect_services(OS: str):
    # Function detects services and returns the standard project result dict contract
    # where success is bool and data_or_reason is either list data or failure reason text
    # Create empty list that will hold dict of name, path, owner, and status for each found service
    service_list: list[dict] = []

    # Create empty result dict that will hold whether it was a success (bool)
    # and the data_or_reason value to be returned
    result_dict: dict = {}

    # Windows branch uses psutil win_service APIs instead of shell commands
    if OS == "Windows":
        import psutil

        # Create list of detected services as WindowsService objects
        results = list(psutil.win_service_iter())
        # Iterate through each WindowsService object
        for r in results:
            # Create temp dict to store service_info
            service_info: dict = {}
            name = r.name()
            if name:
                service_info["name"] = name
            else:
                service_info["name"] = "No name found"

            path = r.binpath()
            if path:
                service_info["path"] = path
            else:
                service_info["path"] = "No path found"

            username = r.username()
            if username:
                service_info["owner"] = r.username()
            else:
                service_info["owner"] = "No owner found"

            status = r.status()
            if status:
                service_info["status"] = status
            else:
                service_info["status"] = "No status found"

            service_list.append(service_info)

        # If the service_list is empty
        if len(service_list) == 0:
            result_dict["success"] = False
            result_dict["data_or_reason"] = "No Services discovered"
        # If the service_list is populated
        else:
            result_dict["success"] = True
            result_dict["data_or_reason"] = service_list
        # Return final dict showing whether function succeeded and the data_or_reason
        return result_dict

    # Linux branch uses systemctl shell commands and parses returned text/json
    elif OS == "Linux":
        import json

        # Create result dict from run_command using systemctl list-units
        command_dict: dict = run_command(
            [
                "systemctl",
                "list-units",
                "--type=service",
                "--all",
                "--output=json",
            ]
        )

        # If the command ran successfully, parse the service list
        if command_dict["success"]:
            # Create list from the json returned in the data_or_reason key from command_dict
            json_list = json.loads(command_dict["data_or_reason"])

            for service in json_list:
                # Make a temporary service_dict to hold values for one service
                service_dict: dict = {}
                # Exclude phantom references
                if service.get("load") != "not-found":
                    service_dict["name"] = service.get("unit")
                    service_dict["status"] = service.get("active")
                    new_command_dict: dict = run_command(
                        [
                            "systemctl",
                            "show",
                            service_dict["name"],
                            "--property=ExecStart,User",
                        ]
                    )
                    if new_command_dict["success"]:
                        # The show command returns raw text lines for ExecStart and User
                        # so we parse those lines and normalize missing values to fallback strings
                        data: str = new_command_dict["data_or_reason"]

                        # Case 1: output begins with ExecStart line first
                        if data.startswith("Exec"):
                            # Parse executable path from the ExecStart structure
                            x = data.split("path=", 1)[1]
                            path = x.split(" ", 1)[0]
                            # If User line exists parse owner, otherwise default fallback
                            if data.count("\nUser=") >= 1:
                                owner = data.split("\nUser=", 1)[1]
                                owner = owner.split("\n", 1)[0]
                                if len(owner) == 0:
                                    owner = "No owner found"
                            else:
                                owner = "No owner found"
                        # Case 2: output begins with User line first
                        elif data.startswith("User"):
                            owner = data.split("User=", 1)[1]
                            owner = owner.split("\n", 1)[0]
                            if len(owner) == 0:
                                owner = "No owner found"
                            # If ExecStart appears later in output, parse path from that line
                            if data.count("\nExecStart={") >= 1:
                                path = data.split("\nExecStart={ path=", 1)[1]
                                path = path.split(" ", 1)[0]
                            else:
                                path = "No path found"
                        # Case 3: neither expected line format appears
                        else:
                            path = "No path found"
                            owner = "No owner found"

                        # Save normalized path/owner values into current service record
                        service_dict["path"] = path
                        service_dict["owner"] = owner
                    else:
                        # If second systemctl call fails for this service, keep record with fallback values
                        owner = "No owner found"
                        service_dict["owner"] = owner
                        path = "No path found"
                        service_dict["path"] = path
                    service_list.append(service_dict)
            # If the service_list is empty
            if len(service_list) == 0:
                result_dict["success"] = False
                result_dict["data_or_reason"] = "No Services discovered"
            # If the service_list is populated
            else:
                result_dict["success"] = True
                result_dict["data_or_reason"] = service_list
            # Return final dict showing whether function succeeded and the data_or_reason
            return result_dict
        else:
            result_dict["success"] = False
            result_dict["data_or_reason"] = command_dict["data_or_reason"]
            return result_dict

    # Darwin (macOS) service detection not implemented yet
    elif OS == "Darwin":
        pass

    # Any OS value outside handled branches returns not implemented contract response
    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS not yet implemented"
        return result_dict
