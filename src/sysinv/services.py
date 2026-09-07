from .helpers import run_command


def detect_services(OS: str):
    # services_list: list[dict] = []

    # Create empty result dict that will hold wether it was a success (bool) and the data_or_reason and be returned
    result_dict: dict = {}
    if OS == "Windows":
        import psutil

        result = list(psutil.win_service_iter())

        print(result)

    elif OS == "Linux":
        pass

    elif OS == "Darwin":
        pass

    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS not yet implemented"
        return result_dict
