# Import python modules
import logging
import subprocess
import socket
import json
import os
import platform


class ConnectUtils:
    """ Utilities to connect to the internet and IoT. """

    # Initialize logger
    extra = {"console_name": "ConnectUtils", "file_name": "connect_utils"}
    logger = logging.getLogger("connect")
    logger = logging.LoggerAdapter(logger, extra)

    # ------------------------------------------------------------------------
    # Returns True if this is a Beaglebone.
    @staticmethod
    def is_bbb():
        # Only for rob developing
        if platform.node() == 'rbaynes.local':
            return True

        try:
            # command and list of args as list of string
            cmd = ["cat", "/etc/dogtag"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                if 'Beagle' in output:
                    return True
        except:
            pass
        return False

    # ------------------------------------------------------------------------
    # Return the list of local wifis.
    @staticmethod
    def get_wifis():
        wifis = ['']
        if not ConnectUtils.is_bbb():
            return wifis
        try:
            # command and list of args as list of string
            cmd = ["scripts/get_wifis.sh"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
#debugrob, make a list of the SSID, handle missing ssid and use <hidden SSID>
                print('debugrob get_wifis={}'.format(output))

        except:
            pass
        return wifis

    # ------------------------------------------------------------------------
    @staticmethod
    def join_wifi(wifi, password):
        """
debugrob, implement this
        message = ConnectUtils.join_wifi(wifi, password)
        """
        return ''

    # ------------------------------------------------------------------------
    # Returns True if this BBB is a wifi model.
    @staticmethod
    def is_wifi_bbb():
        # Only for rob developing
        if platform.node() == 'rbaynes.local':
            return True

        if not ConnectUtils.is_bbb():
            return False
        try:
            # command and list of args as list of string
            cmd = ["ifconfig", "wlan0"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                if 'wlan0: flags' in output:
                    return True
        except:
            pass
        return False

    # ------------------------------------------------------------------------
    @staticmethod
    def get_IP():
        """ Returns the IP address of the active interface. """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            pass
        return 'No IP address'

    # ------------------------------------------------------------------------
    @staticmethod
    def get_remote_UI_URL():
        """ Return the URL to the device UI. """
        try:
            about = json.load(open("about.json"))
            sn = str(about["serial_number"])
            sn = sn.replace('-', '.')
            return "http://{}.serveo.net/".format(sn)
        except:
            pass
        return ''

    # ------------------------------------------------------------------------
    @staticmethod
    def is_registered_with_IoT():
        """ Returns True if there is a valid IoT registration. """
        if os.path.exists('registration/data/device_id.bash') and \
                os.path.exists('registration/data/roots.pem') and \
                os.path.exists('registration/data/rsa_cert.pem') and \
                os.path.exists('registration/data/rsa_private.pem'):
            return True
        return False

    # ------------------------------------------------------------------------
    @staticmethod
    def get_device_id():
        """ Returns the device ID string. """
        if not ConnectUtils.is_registered_with_IoT():
            return ''
        try:
            f = open('registration/data/device_id.bash')
            contents = f.read()
            index = contents.find('=')
            devid = contents[index + 1:]
            return devid.rstrip()
        except:
            pass
        return ''





