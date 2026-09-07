import re

from .helpers import run_command


def detect_services(OS: str):
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
            if r.name():
                service_info["name"] = r.name()
            else:
                service_info["name"] = "No name found"

            if r.binpath():
                service_info["path"] = r.binpath()
            else:
                service_info["path"] = "No path found"

            if r.username():
                service_info["owner"] = r.username()
            else:
                service_info["owner"] = "No owner found"

            if r.status():
                service_info["status"] = r.status()
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
