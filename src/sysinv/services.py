from .helpers import run_command


def detect_services(OS: str):
    # services_list: list[dict] = []

    # Create empty result dict that will hold wether it was a success (bool) and the data_or_reason and be returned
    result_dict: dict = {}
    if OS == "Windows":
        import psutil

        results = list(psutil.win_service_iter())
        for r in results:
            print(r.name())
            print(r.status())

    elif OS == "Linux":
        pass

    elif OS == "Darwin":
        pass

    else:
        result_dict["success"] = False
        result_dict["data_or_reason"] = "OS not yet implemented"
        return result_dict
