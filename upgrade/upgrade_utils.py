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
        status = {}
        try:
            uv = UpgradeViewer()  # data from the state.upgrade dict and DB
            status = uv.upgrade_dict
        except:
            pass
        return status


    # ------------------------------------------------------------------------
    # Update our state dict with the software versions.
    # Only call once a day, this will take a few minutes to execute.
    @staticmethod
    def update_dict(state):
        """
        sudo apt-get update
        apt-cache policy openagbrain
        openagbrain:
          Installed: (none)
          Candidate: 0.1-2
        """
        try:
            state.upgrade['status'] = 'Checking for upgrades...'

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

                state.upgrade['current_version'] = installed
                state.upgrade['upgrade_version'] = candidate
                # very simple upgrade logic, trust debian package logic
                if '(none)' == installed or \
                        installed != candidate:
                    state.upgrade['show_upgrade'] = True

            state.upgrade['status'] = 'Up to date.'
            if state.upgrade.get('show_upgrade', False):
                state.upgrade['status'] = 'Software upgrade is available.'

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
#debugrob: old
            # update our debian package
#            cmd = ['sudo', 'apt-get', 'install', '-y', 'openagbrain']
#            subprocess.run(cmd)

            fn = '/etc/rc.local'
            cmd = ['sudo', 'rm', '-f', fn]
            subprocess.run(cmd)

            f = open(fn, 'w')
            f.write('#!/bin/sh\n')
            f.write('apt-get install -y openagbrain')
            f.close()

            cmd = ['sudo', 'service', 'rc.local', 'restart']
            subprocess.run(cmd)

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
        state = uv.upgrade_dict
        UpgradeUtils.update_dict(state)
        return UpgradeUtils.get_status()

        try:
#debugrob: use Popen and subprocess.DETACHED_PROCESS

            # update our debian package
            cmd = ['sudo', 'apt-get', 'install', '-y', 'openagbrain']
            subprocess.run(cmd)

            upgrade['status'] = 'Up to date.'
            upgrade['show_upgrade'] = False

        except Exception as e:
            upgrade['error'] = e

        return upgrade


