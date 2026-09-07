import subprocess


def run_command(command_list: list[str]) -> dict:
    try:
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
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
