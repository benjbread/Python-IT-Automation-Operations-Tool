import re

from .helpers import run_command


def detect_services(OS: str):
    # Create empty list that will hold dict of name, path, owner, and status for each found service
    service_list: list[dict] = []

    # Create empty result dict that will hold wether it was a success (bool) and the data_or_reason and be returned
    result_dict: dict = {}

    if OS == "Windows":
        import psutil

        # Creates list of each service detected as WindowService class
        results = list(psutil.win_service_iter())
        # Get individual service as WindowService class
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
            try:
                service_info["owner"] = r.username()
            except Exception as e:
                service_info["path"] = f"RAISED: {type(e).__name__}: {e}"

            status = r.status()
            if status:
                service_info["status"] = status
            else:
                service_info["status"] = "No status found"

            service_list.append(service_info)

        if len(service_list) == 0:
            result_dict["success"] = False
            result_dict["data_or_reason"] = "No Services discovered"
        # If the service_list is populated
        else:
            result_dict["success"] = True
            result_dict["data_or_reason"] = service_list
        # return the final dict of wether function succeeded or not, and then the data_or_reason
        return result_dict

    elif OS == "Linux":
        pass

    elif OS == "Darwin":
        pass

    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS not yet implemented"
        return result_dict
