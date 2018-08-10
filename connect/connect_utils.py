# Import python modules
import subprocess
import socket
import json
import os
import platform
import urllib.request


class ConnectUtils:
    """ Utilities to connect to the internet and IoT. """

    # --------------------------------------------------------------------------
    @staticmethod
    def valid_internet_connection():
        try:
            urllib.request.urlopen("http://google.com")
            return True
        except:
            return False

    # ------------------------------------------------------------------------
    # Returns True if this is a Beaglebone.
    @staticmethod
    def is_bbb():
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
        wifis = []
        if not ConnectUtils.is_bbb():
            return wifis
        try:
            # command and list of args as list of strings
            cmd = ["scripts/get_wifis.sh"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                wifi_list = []
                lines = output.splitlines()
                for line in lines:
                    ssid = ''
                    service = ''
                    tokens = line.split()
                    # wifi_f45eab3f07fb_hidden_managed_psk
                    # MIT GUEST wifi_f45eab3f07fb_4d4954_managed_none
                    # *AO TRENDnet711 wifi_f45ea7fb_544373131_managed_psk
                    for token in tokens:
                        if token.startswith('wifi_'):
                            service = token
                        elif not token.startswith('*'):
                            if 0 != len(ssid):
                                ssid += ' '
                            ssid += token

                    if 0 == len(ssid):
                        # Our connect_wifi.sh can't handle hidden SSIDs
                        #ssid = '<hidden SSID>'
                        continue

                    # Also prevent a BBB from being used
                    if service.startswith('wifi_') and \
                            not ssid.startswith('BeagleBone-'):
                        wifis.append({ 'ssid':ssid, 'service':service })
        except:
            pass
        return wifis

    # ------------------------------------------------------------------------
    @staticmethod
    def join_wifi(wifi, password):
        message = 'Could not connect to wifi'
        if not ConnectUtils.is_bbb():
            return 'This is not a beaglebone!'
        try:
            if 0 == len(password):
                password = ''

            cmd = ["scripts/connect_wifi.sh", wifi, password]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                print('debugrob join_wifi output={}'.format(output))
#debugrob, look for success
# Connected wifi_f45eab3f07fb_5452454e446e6574373131_managed_psk
# Error /net/connman/service/wifi_f45eab3f07fb_5452454e446e6574373131_managed_psk: Not registered

# if this returns success, how to refresh the page connect page?  to get all the fields?   OR just send all the fields back in a dict?

                message = 'fix this debugrob'
        except:
            pass
        return message 

#debugrob, delete all wifi connections:
# sudo rm -fr /var/lib/connman/*.config /var/lib/connman/wifi_*

    # ------------------------------------------------------------------------
    # Returns True if this BBB is a wifi model.
    @staticmethod
    def is_wifi_bbb():
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





