# Import standard python modules
import subprocess


def is_bbb():
    """Checks if current device is a beaglebone."""
    try:
        # Command and list of args as list of string
        cmd = ["cat", "/etc/dogtag"]
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc1:
            output = proc1.stdout.read().decode("utf-8")
            output += proc1.stderr.read().decode("utf-8")
            if "Beagle" in output:
                return True
    except:
        pass
    return False


def is_wifi_bbb():
    """Checks if bbb is a wifi model."""
    if not is_bbb():
        return False
    try:
        # Command and list of args as list of string
        cmd = ["ifconfig", "wlan0"]
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc1:
            output = proc1.stdout.read().decode("utf-8")
            output += proc1.stderr.read().decode("utf-8")
            if "wlan0: flags" in output:
                return True
    except:
        pass
    return False


def get_remote_ui_url():
    """Get the URL for remote access to the device UI e.g. 1712EW004671.serveo.net"""

    if not is_bbb():
        return "This is not a beaglebone"
    try:
        # Get this BBB's serial number
        serial = "oops"
        cmd = ["scripts/get_BBB_SN.sh"]
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc1:
            output = proc1.stdout.read().decode("utf-8")
            output += proc1.stderr.read().decode("utf-8")
            serial = output.strip()

        return "http://{}.serveo.net/".format(serial)
    except:
        pass
    return ""
