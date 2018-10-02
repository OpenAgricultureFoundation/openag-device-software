# Import stndard python modules
import subprocess, socket, json, os, platform, time, uuid, urllib.request

# Import python types
from typing import Dict, Any

# Import app viewers
from app.viewers import ConnectViewer, IoTViewer

# Initialize file paths
REG_DATA_PATH = "data/registration/"


# TODO Notes:
# Remove redundant functions accross connect, iot, update, resource, and upgrade
# Adjust function and variable names to match python conventions
# Add static type checking
# Write tests
# Catch specific exceptions
# Pull out file path strings to top of file
# We may just want many of these functions in the manager or in device utilities
# Inherit from state machine manager
# Always use get method to access dicts unless checking for KeyError (rare cases)
# Always use decorators to access shared state w/state.lock


##### INTERNET CONNECTION FUNCTIONS ####################################################


def valid_internet_connection() -> bool:
    """Checks if internet connection is valid."""
    try:
        urllib.request.urlopen("http://google.com")
        return True
    except urllib.error.URLError:  # type: ignore
        return False


def get_ip():
    """Gets IP address of the active interface."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "Unknown"


def get_wifis():
    """Gets a list of local wifis."""
    wifis = []
    all_wifis = get_all_wifis()
    if len(all_wifis) == 0:
        return wifis

    # Parse just what we want to send to browser:
    for wifi in all_wifis:
        # No hidden SSIDs or beaglebone APs
        if not wifi["hidden"] and not wifi["ssid"].startswith("BeagleBone-"):
            wifis.append({"ssid": wifi["ssid"], "service": wifi["service"]})
    return wifis


def get_all_wifis():
    """Gets a list of all local wifis."""
    wifis = []
    if not is_bbb():
        return wifis
    try:
        # Command and list of args as list of strings
        cmd = ["scripts/get_wifis.sh"]
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc1:
            output = proc1.stdout.read().decode("utf-8")
            output += proc1.stderr.read().decode("utf-8")
            wifi_list = []
            lines = output.splitlines()
            for line in lines:
                ssid = ""
                service = ""
                connected = False
                hidden = False
                tokens = line.split()
                # wifi_f45eab3f07fb_hidden_managed_psk
                # MIT GUEST wifi_f45eab3f07fb_4d4954_managed_none
                # *AO TRENDnet711 wifi_f45ea7fb_544373131_managed_psk
                for token in tokens:
                    if token.startswith("wifi_"):
                        service = token
                    elif token.startswith("*"):
                        connected = True
                    else:
                        if 0 != len(ssid):
                            ssid += " "
                        ssid += token

                if 0 == len(ssid):
                    # this is a hidden SSID
                    hidden = True
                    ssid = "<hidden SSID>"

                if service.startswith("wifi_"):
                    wifis.append(
                        {
                            "ssid": ssid,
                            "service": service,
                            "connected": connected,
                            "hidden": hidden,
                        }
                    )
    except:
        pass
    return wifis


def join_wifi(wifi, password):
    """Joins specified wifi access point."""
    result = False
    if not is_bbb():
        return result
    try:
        if 0 == len(password):
            password = ""

        cmd = ["scripts/connect_wifi.sh", wifi, password]
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc1:
            output = proc1.stdout.read().decode("utf-8")
            output += proc1.stderr.read().decode("utf-8")
            result = True
            time.sleep(5)  # Time for networking stack to init
    except:
        pass
    return result


def delete_wifi_connections():
    """Deletes all wifi connections."""
    if not is_bbb():
        return False
    try:
        # First we must disconnect from any active wifis
        all_wifis = get_all_wifis()
        for wifi in all_wifis:
            if wifi["connected"]:
                cmd = ["connmanctl", "disconnect", wifi["service"]]
                subprocess.run(cmd)

        # Now we can remove all wifi configuration
        cmd = ["scripts/delete_all_wifi_connections.sh"]
        with subprocess.run(cmd):
            return True
    except:
        pass
    return False


##### DEVICE TYPE FUNCTIONS ############################################################


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


##### REMOVE VIEWER DEPENDENCE #########################################################


def get_status() -> Dict[str, Any]:
    """Returns a dict of all the fields we display on the Django Connect tab."""

    status = {}
    try:
        cv = ConnectViewer()  # data from the state.connect dict and DB

        # This never changes, initialized by ConnectionManager,
        # and read from the state dict here.
        status["is_bbb"] = cv.connect_dict["is_bbb"]

        # These change dynamically, so get each time.
        status["device_UI"] = get_remote_ui_url()
        status["is_wifi_bbb"] = is_wifi_bbb()
        status["wifis"] = get_wifis()
        status["IP"] = get_ip()
        status["is_registered_with_iot"] = is_registered_with_iot()
        status["device_id"] = get_device_id()

        # Get the IoT connection status directly from its state dict
        iotv = IoTViewer()
        status["iot_connection"] = iotv.iot_dict["connected"]

        status["valid_internet_connection"] = valid_internet_connection()
        if valid_internet_connection():
            status["status"] = "Connected"
        else:
            status["status"] = "No connection"
        status["error"] = None

    except:
        pass
    return status


##### PUT THESE IN IOT UTILITIES #######################################################


def is_registered_with_iot():
    """Checks if IoT registration is valid."""
    if (
        os.path.exists(REG_DATA_PATH + "device_id.bash")
        and os.path.exists(REG_DATA_PATH + "roots.pem")
        and os.path.exists(REG_DATA_PATH + "rsa_cert.pem")
        and os.path.exists(REG_DATA_PATH + "rsa_private.pem")
    ):
        return True
    return False


def register_iot():
    """Registers device with IoT. Returns registration verification code for success 
    or None."""
    if not valid_internet_connection():
        return None
    try:
        cmd = ["mkdir", "-p", REG_DATA_PATH]
        subprocess.run(cmd)

        cmd = [
            "scripts/one_time_key_creation_and_iot_device_registration.sh",
            REG_DATA_PATH,
        ]
        subprocess.run(cmd)

        fn = REG_DATA_PATH + "verification_code.txt"
        verification_code = open(fn).read()
        os.remove(fn)
        return verification_code
    except:
        pass
    return None


def delete_iot_registration():
    """Deletes IoT registration data."""
    try:
        # remove the IoT config dir
        cmd = ["rm", "-fr", REG_DATA_PATH]
        with subprocess.run(cmd):
            return True
    except:
        pass
    return False


def get_device_id():
    """Gets device ID string."""
    if not is_registered_with_iot():
        return None
    return get_device_id_from_file()


def get_device_id_from_file():
    """Gets device ID string, with no other logic."""
    try:
        with open(REG_DATA_PATH + "device_id.bash") as f:
            contents = f.read()
            index = contents.find("=")
            devid = contents[index + 1 :]
            return devid.rstrip()
    except:
        pass
    return None
