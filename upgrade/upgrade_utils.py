# Import python modules
import subprocess
import socket
import json
import os
import platform
import time
import urllib.request
import uuid

from app.viewers import UpgradeViewer


class UpgradeUtils:
    """ Utilities to upgrade this apt package. """

    # --------------------------------------------------------------------------
    # Return a dict of all the fields we display on the Django Upgrade tab.
    @staticmethod
    def get_status():
        upgradedict = {}
        try:
            uv = UpgradeViewer()  # data from the state.upgrade dict and DB
            upgradedict = uv.upgrade_dict
        except:
            pass
        return upgradedict


    # ------------------------------------------------------------------------
    # Update our dict with the software versions.
    # Only call once a day, this will take a few minutes to execute.
    @staticmethod
    def update_dict(upgradedict):
        """
        sudo apt-get update
        apt-cache policy openagbrain
        openagbrain:
          Installed: (none)
          Candidate: 0.1-2
        """
        try:
            upgradedict['status'] = 'Checking for upgrades...'

            # update this machines list of available packages
            cmd = ['sudo', 'apt-get', 'update']
            subprocess.run(cmd)

            # command and list of args as list of strings
            cmd = ['apt-cache', 'policy', 'openagbrain']
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                lines = output.splitlines()
                installed = ''
                candidate = ''
                for line in lines:
                    tokens = line.split()
                    for token in tokens:
                        if token.startswith('Installed:'):
                            installed = tokens[1]
                            break
                        elif token.startswith('Candidate:'):
                            candidate = tokens[1]
                            break

                upgradedict['current_version'] = installed
                upgradedict['upgrade_version'] = candidate
                # very simple upgrade logic, trust debian package logic
                if '(none)' == installed or \
                        installed != candidate:
                    upgradedict['show_upgrade'] = True

            upgradedict['status'] = 'Up to date.'
            if upgradedict.get('show_upgrade', False):
                upgradedict['status'] = 'Software upgrade is available.'

        except:
            return False
        return True


    # ------------------------------------------------------------------------
    # Update our debian package with the latest version available.
    @staticmethod
    def update_software():
        """
        If we call 'sudo apt-get install -y openagbrain' here, inside django,
        we will create a deadlock where apt can't complete the install because
        it is run as a child of the process it has to terminate.

        So, let's get hacky:
        - rm /etc/rc.local (it is a symlink to our install anyway)

        - write a new (temporary) rc.local that contains:
            #!/bin/sh
            apt-get install -y openagbrain

        - service rc.local restart
        """
        uv = UpgradeViewer()  # data from the state.upgrade dict and DB
        upgrade = uv.upgrade_dict
        try:
            # update our debian package
            cmd = ['sudo', 'apt-get', 'install', '-y', 'openagbrain']
            subprocess.Popen(cmd)

            upgrade['status'] = 'Up to date.'
            upgrade['show_upgrade'] = False

        except Exception as e:
            upgrade['error'] = e

        return upgrade


    # ------------------------------------------------------------------------
    # Check for updates
    @staticmethod
    def check():
        """
        sudo apt-get install -y openagbrain
        """
        uv = UpgradeViewer()  # data from the state.upgrade dict and DB
        upgradedict = uv.upgrade_dict
        UpgradeUtils.update_dict(upgradedict)
        return UpgradeUtils.get_status()


