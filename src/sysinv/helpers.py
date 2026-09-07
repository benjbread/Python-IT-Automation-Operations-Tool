import subprocess


# Function to run external programs, system commands, or shell scripts
# and return dict of success which holds a bool and data_or_reason that has the output
def run_command(command_list: list[str]) -> dict:
    # try and run the command...
    try:
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        # if no errors are raised then make a dict with success as True and the output of the command
        result_dict = {"success": True, "data_or_reason": result.stdout}
        return result_dict
    # if an command fails and returns a non-zero exit status
    except subprocess.CalledProcessError as err:
        # make a dict with success as False and the output of the stderr
        result_dict = {
            "success": False,
            "data_or_reason": f"{err.cmd} failed: {err.stderr}",
        }
        return result_dict
    # if an command takes longer than our timeout
    except subprocess.TimeoutExpired as err:
        # make a dict with success as False and how long it was given until cancelled
        result_dict = {
            "success": False,
            "data_or_reason": f"Process timed out after: {err.timeout} seconds",
        }
        return result_dict
