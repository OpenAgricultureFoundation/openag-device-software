# Import python modules
import subprocess
import socket
import json
import os
import platform
import time
import urllib.request
import uuid

from app.viewers import ConnectViewer
from app.viewers import IoTViewer

REG_DATA_DIR = "data/registration/"


class ConnectUtilities:
    """Utilities to connect to the internet and IoT."""

    @staticmethod
    def get_status():
        """Returns a dict of all the fields we display on the Django Connect tab."""

        status = {}
        try:
            cv = ConnectViewer()  # data from the state.connect dict and DB

            # This never changes, initialized by ConnectionManager,
            # and read from the state dict here.
            #status["is_bbb"] = cv.connect_dict["is_bbb"]
            status["is_bbb"] = ConnectUtilities.is_bbb()

            # These change dynamically, so get each time.
            status["device_UI"] = ConnectUtilities.get_remote_UI_URL()
            status["is_wifi_bbb"] = ConnectUtilities.is_wifi_bbb()
            status["wifis"] = ConnectUtilities.get_wifis()
            status["IP"] = ConnectUtilities.get_IP()
            status["is_registered_with_iot"] = \
                ConnectUtilities.is_registered_with_iot()
            status["device_id"] = ConnectUtilities.get_device_id()

            # Get the IoT connection status directly from its state dict
            iotv = IoTViewer()
            status["iot_connection"] = iotv.iot_dict["connected"]

            status["valid_internet_connection"] = \
                ConnectUtilities.valid_internet_connection()
            if ConnectUtilities.valid_internet_connection():
                status["status"] = "Connected"
            else:
                status["status"] = "No connection"
            status["error"] = None

        except:
            pass
        return status

    @staticmethod
    def valid_internet_connection():
        """Checks if we have a valid internet connection and DNS?"""
        try:
            urllib.request.urlopen("http://google.com")
            return True
        except:
            return False

    @staticmethod
    def is_simulation_mode():
        if os.environ.get("SIMULATE") == "true":
            return True
        return False

    @staticmethod
    def is_bbb():
        """Checks if current device is a beaglebone."""
        # We are in simulation mode, so pretend we are a BBB
        if ConnectUtilities.is_simulation_mode():
            return True

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

    @staticmethod
    def get_wifis():
        """Gets a list of local wifis."""
        wifis = []
        all_wifis = ConnectUtilities.get_all_wifis()
        if 0 == len(all_wifis):
            return wifis
        # Parse just what we want to send to browser:
        for wifi in all_wifis:
            # No hidden SSIDs or beaglebone APs
            if not wifi["hidden"] and not wifi["ssid"].startswith("BeagleBone-"):
                wifis.append({"ssid": wifi["ssid"], "service": wifi["service"]})
        return wifis

    @staticmethod
    def join_wifi(wifi, password):
        """Joins specified wifi access point."""
        result = False
        if ConnectUtilities.is_simulation_mode():
            return True
        try:
            if 0 == len(password):
                password = ""

            cmd = ["scripts/connect_wifi.sh", wifi, password]
            subprocess.run(cmd)
            result = True
            time.sleep(5)  # Time for networking stack to init
        except:
            pass
        return result

    @staticmethod
    def join_wifi_advanced(ssid_name, passphrase, hidden_ssid, security, eap, identity, phase2):
        """Joins specified wifi access point with advanced config. args."""
        result = False
        if ConnectUtilities.is_simulation_mode():
            return True
        try:
            if 0 == len(passphrase):
                passphrase = ""
            cmd = ["scripts/advanced_connect_wifi.sh", ssid_name, passphrase, hidden_ssid, security, eap, identity, phase2]
            subprocess.run(cmd)
            result = True
            time.sleep(5)  # Time for networking stack to init
        except:
            pass
        return result

    @staticmethod
    def delete_wifi_connections():
        """Deletes all wifi connections."""
        if ConnectUtilities.is_simulation_mode():
            return False
        try:
            # First we must disconnect from any active wifis
            all_wifis = ConnectUtilities.get_all_wifis()
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

    @staticmethod
    def is_wifi_bbb():
        """Checks if bbb is a wifi model."""
        # We are in simulation mode, so pretend we are a BBB wifi.
        if ConnectUtilities.is_simulation_mode():
            return True

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

    @staticmethod
    def get_IP():
        """Gets IP address of the active interface."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            pass
        return ""

    @staticmethod
    def get_remote_UI_URL():
        """Get the URL for remote access to the device UI 
           e.g. 1712EW004671.serveo.net"""
        if ConnectUtilities.is_simulation_mode():
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

    @staticmethod
    def is_registered_with_iot():
        """Checks if IoT registration is valid."""
        if (
            os.path.exists(REG_DATA_DIR + "device_id.bash")
            and os.path.exists(REG_DATA_DIR + "roots.pem")
            and os.path.exists(REG_DATA_DIR + "rsa_cert.pem")
            and os.path.exists(REG_DATA_DIR + "rsa_private.pem")
        ):
            return True
        return False

    @staticmethod
    def get_device_id():
        """Gets device ID string."""
        if not ConnectUtilities.is_registered_with_iot():
            return None
        return ConnectUtilities.get_device_id_from_file()

    @staticmethod
    def get_device_id_from_file():
        """Gets device ID string, with no other logic."""
        try:
            with open(REG_DATA_DIR + "device_id.bash") as f:
                contents = f.read()
                index = contents.find("=")
                devid = contents[index + 1 :]
                return devid.rstrip()
        except:
            pass
        return None

    @staticmethod
    def get_all_wifis():
        """Gets a list of all local wifis."""
        wifis = []
        if ConnectUtilities.is_simulation_mode():
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

    @staticmethod
    def delete_iot_registration():
        """Deletes IoT registration data."""
        try:
            # remove the IoT config dir
            cmd = ["rm", "-fr", REG_DATA_DIR]
            with subprocess.run(cmd):
                return True
        except:
            pass
        return False

    @staticmethod
    def register_iot():
        """Registers device with IoT. 
           Returns registration verification code for success or None."""

        if not ConnectUtilities.valid_internet_connection():
            return None

        if ConnectUtilities.is_registered_with_iot():
            return ConnectUtilities.get_iot_verification_code()

        try:
            cmd = ["mkdir", "-p", REG_DATA_DIR]
            subprocess.run(cmd)

            cmd = [
                "scripts/one_time_key_creation_and_iot_device_registration.sh",
                REG_DATA_DIR,
            ]
            subprocess.run(cmd)

            return ConnectUtilities.get_iot_verification_code()
        except:
            pass
        return None

    @staticmethod
    def get_iot_verification_code():
        """Returns the IoT verification code needed to pair a device with 
           a cloud user account. """
        try:
            fn = REG_DATA_DIR + "verification_code.txt"
            verification_code = open(fn).read()
            return verification_code
        except:
            pass
        return None


