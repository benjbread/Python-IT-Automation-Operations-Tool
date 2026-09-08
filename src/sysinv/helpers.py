import subprocess


# Function to run external programs, system commands, or shell scripts
# and return a dict where success is bool and data_or_reason holds command output
def run_command(command_list: list[str]) -> dict:
    # command_list should be passed as list items so subprocess does safe argument handling
    # try and run the command...
    try:
        result = subprocess.run(
            command_list,
            # capture_output grabs stdout/stderr so function can package them in returned dict
            capture_output=True,
            # text=True decodes bytes output into normal python strings
            text=True,
            # check=True raises CalledProcessError for non-zero exit status
            check=True,
            # timeout stops command from hanging forever
            timeout=60,
        )
        # If no errors are raised, return success True with stdout output
        result_dict = {"success": True, "data_or_reason": result.stdout}
        return result_dict
    # If a command fails and returns a non-zero exit status
    except subprocess.CalledProcessError as err:
        # make a dict with success as False and include command + stderr to preserve specific failure reason
        result_dict = {
            "success": False,
            "data_or_reason": f"{err.cmd} failed: {err.stderr}",
        }
        return result_dict
    # If a command takes longer than timeout
    except subprocess.TimeoutExpired as err:
        # make a dict with success as False and how long it was given until cancelled
        result_dict = {
            "success": False,
            "data_or_reason": f"Process timed out after: {err.timeout} seconds",
        }
        return result_dict
