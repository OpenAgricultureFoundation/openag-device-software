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


class ConnectUtils:
    """ Utilities to connect to the internet and IoT. """

    # --------------------------------------------------------------------------
    # Return a dict of all the fields we display on the Django Connect tab.
    @staticmethod
    def get_status():
        status = {}
        try:
            cv = ConnectViewer()  # data from the state.connect dict and DB

            # This never changes, initialized by ConnectionManager,
            # and read from the state dict here.
            status['is_bbb'] = cv.connect_dict['is_bbb']

            # These change dynamically, so get each time.
            status['device_UI'] = ConnectUtils.get_remote_UI_URL()
            status['is_wifi_bbb'] = ConnectUtils.is_wifi_bbb()
            status['wifis'] = ConnectUtils.get_wifis()
            status['IP'] = ConnectUtils.get_IP()
            status['is_registered_with_IoT'] = \
                    ConnectUtils.is_registered_with_IoT()
            status['device_id'] = ConnectUtils.get_device_id()

            # Get the IoT connection status directly from its state dict
            iotv = IoTViewer()
            status['iot_connection'] = iotv.iot_dict["connected"]

            status['valid_internet_connection'] = \
                    ConnectUtils.valid_internet_connection()
            if ConnectUtils.valid_internet_connection():
                status['status'] = 'Connected'
            else:
                status['status'] = 'No connection'
            status['error'] = None

        except:
            pass
        return status

    # --------------------------------------------------------------------------
    # Do we have a valid internet connection and DNS?0
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
        all_wifis = ConnectUtils.get_all_wifis()
        if 0 == len(all_wifis):
            return wifis
        # Parse just what we want to send to browser:
        for wifi in all_wifis:
            # No hidden SSIDs or beaglebone APs
            if not wifi['hidden'] and \
                    not wifi['ssid'].startswith('BeagleBone-'):
                wifis.append({ 'ssid':wifi['ssid'], 
                        'service':wifi['service'] })
        return wifis


    # ------------------------------------------------------------------------
    # Join the specified wifi access point.
    @staticmethod
    def join_wifi(wifi, password):
        result = False
        if not ConnectUtils.is_bbb():
            return result
        try:
            if 0 == len(password):
                password = ''

            cmd = ["scripts/connect_wifi.sh", wifi, password]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                result = True
                time.sleep(5)  # time for networking stack to init
        except:
            pass
        return result


    # ------------------------------------------------------------------------
    # Delete all wifi connections.
    @staticmethod
    def delete_wifi_connections():
        if not ConnectUtils.is_bbb():
            return False
        try:
            # first we must disconnect from any active wifis
            all_wifis = ConnectUtils.get_all_wifis()
            for wifi in all_wifis:
                if wifi['connected']:
                    cmd = ['connmanctl', 'disconnect', wifi['service']]
                    subprocess.run(cmd)

            # now we can remove all wifi configuration
            cmd = ['scripts/delete_all_wifi_connections.sh']
            with subprocess.run(cmd):
                return True
        except:
            pass
        return False


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
    # Returns the IP address of the active interface. 
    @staticmethod
    def get_IP():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            pass
        return ''

    # ------------------------------------------------------------------------
    # Get the URL for remote access to the device UI.
    # 1712EW004671.serveo.net
    @staticmethod
    def get_remote_UI_URL():
        if not ConnectUtils.is_bbb():
            return "This is not a beaglebone"
        try:
            # Get this BBB's serial number
            serial = 'oops'
            cmd = ['scripts/get_BBB_SN.sh']
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                serial = output.strip()

            return "http://{}.serveo.net/".format(serial)
        except:
            pass
        return ''

    # ------------------------------------------------------------------------
    # Returns True if there is a valid IoT registration. 
    @staticmethod
    def is_registered_with_IoT():
        if os.path.exists('registration/data/device_id.bash') and \
                os.path.exists('registration/data/roots.pem') and \
                os.path.exists('registration/data/rsa_cert.pem') and \
                os.path.exists('registration/data/rsa_private.pem'):
            return True
        return False

    # ------------------------------------------------------------------------
    # Returns the device ID string. 
    @staticmethod
    def get_device_id():
        if not ConnectUtils.is_registered_with_IoT():
            return None
        return ConnectUtils.get_device_id_from_file()

    # ------------------------------------------------------------------------
    # Returns the device ID string, with no other logic. 
    @staticmethod
    def get_device_id_from_file():
        try:
            f = open('registration/data/device_id.bash')
            contents = f.read()
            index = contents.find('=')
            devid = contents[index + 1:]
            return devid.rstrip()
        except:
            pass
        return None

    # ------------------------------------------------------------------------
    # For internal use.  Return the list of local wifis.
    @staticmethod
    def get_all_wifis():
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
                    connected = False
                    hidden = False
                    tokens = line.split()
                    # wifi_f45eab3f07fb_hidden_managed_psk
                    # MIT GUEST wifi_f45eab3f07fb_4d4954_managed_none
                    # *AO TRENDnet711 wifi_f45ea7fb_544373131_managed_psk
                    for token in tokens:
                        if token.startswith('wifi_'):
                            service = token
                        elif token.startswith('*'):
                            connected = True
                        else:
                            if 0 != len(ssid):
                                ssid += ' '
                            ssid += token

                    if 0 == len(ssid):
                        # this is a hidden SSID 
                        hidden = True
                        ssid = '<hidden SSID>'

                    if service.startswith('wifi_'):
                        wifis.append({'ssid':ssid, 
                                'service':service,
                                'connected':connected,
                                'hidden':hidden })
        except:
            pass
        return wifis


    # ------------------------------------------------------------------------
    # Delete the IoT registration.
    @staticmethod
    def delete_iot_registration():
        try:
            # remove the IoT config dir
            cmd = ['rm', '-fr', 'registration/data/']
            with subprocess.run(cmd):
                return True
        except:
            pass
        return False


    # ------------------------------------------------------------------------
    # Register this machine with IoT.
    # Returns the registration verification code for success or None.
    @staticmethod
    def register_iot():
        if not ConnectUtils.valid_internet_connection():
            return None
        try:
            reg_dir = 'registration/data'
            cmd = ['mkdir', '-p', reg_dir]
            subprocess.run(cmd)

            cmd = ['registration/one_time_key_creation_and_iot_device_registration.sh', reg_dir]
            subprocess.run(cmd)

            fn = reg_dir + '/verification_code.txt'
            verification_code = open(fn).read()
            os.remove(fn)
            return verification_code
        except:
            pass
        return None




