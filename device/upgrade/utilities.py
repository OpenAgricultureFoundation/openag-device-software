# # Import standard python modules
# import subprocess, socket, json, os, platform, time, uuid,

# # Import  device utilities
# from device.utilities.state.main import State

# # Import app viewers
# from app.viewers import UpgradeViewer

# TODO Notes:
# Remove redundant functions accross connect, iot, update, resource, and upgrade
# We may just want many of these functions in the manager or in device utilities
# Adjust function and variable names to match python conventions
# Add static type checking
# Write tests
# Catch specific exceptions
# Pull out file path strings to top of file
# Inherit from state machine manager
# Always use get method to access dicts unless checking for KeyError (rare cases)
# Always use decorators to access shared state w/state.lock
# Use consistent names for class variables and state variables
# Always logger class from device utilities
# Make logic easy to read (descriptive variables, frequent comments, minimized nesting)
# Add method docstring to every function


# class UpgradeUtilities:
#     """ Utilities to upgrade this apt package. """

#     # Class variable to hold a reference to the state.upgrade dict
#     ref_state = State()

#     @staticmethod
#     def save_state(state):
#         """Saves a reference to the state as a static class var."""
#         UpgradeUtilities.ref_state = state

#     @staticmethod
#     def get_status():
#         """Returns a dict of all the fields we display on the Django Upgrade tab."""
#         return UpgradeUtilities.ref_state.upgrade

#     @staticmethod
#     def update_dict():
#         """ Updates our dict with the software versions. Only call once a day, this will
#         take a few minutes to execute. Example call:
#             sudo apt-get update
#             apt-cache policy openagbrain
#             openagbrain:
#               Installed: (none)
#               Candidate: 0.1-2"""
#         try:
#             UpgradeUtilities.ref_state.upgrade["status"] = "Checking for upgrades..."

#             # update this machines list of available packages
#             cmd = ["sudo", "apt-get", "update"]
#             subprocess.run(cmd)

#             # command and list of args as list of strings
#             cmd = ["apt-cache", "policy", "openagbrain"]
#             with subprocess.Popen(
#                 cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#             ) as proc1:
#                 output = proc1.stdout.read().decode("utf-8")
#                 output += proc1.stderr.read().decode("utf-8")
#                 lines = output.splitlines()
#                 installed = ""
#                 candidate = ""
#                 for line in lines:
#                     tokens = line.split()
#                     for token in tokens:
#                         if token.startswith("Installed:"):
#                             installed = tokens[1]
#                             break
#                         elif token.startswith("Candidate:"):
#                             candidate = tokens[1]
#                             break

#                 UpgradeUtilities.ref_state.upgrade["current_version"] = installed
#                 UpgradeUtilities.ref_state.upgrade["upgrade_version"] = candidate
#                 # very simple upgrade logic, trust debian package logic
#                 if "(none)" == installed or installed != candidate:
#                     UpgradeUtilities.ref_state.upgrade["show_upgrade"] = True

#             UpgradeUtilities.ref_state.upgrade["status"] = "Up to date."
#             if UpgradeUtilities.ref_state.upgrade.get("show_upgrade", False):
#                 UpgradeUtilities.ref_state.upgrade[
#                     "status"
#                 ] = "Software upgrade is available."

#         except:
#             return False
#         return True

#     @staticmethod
#     def update_software():
#         """Update our debian package with the latest version available.

#         If we call 'sudo apt-get install -y openagbrain' here, inside django,
#         we will create a deadlock where apt can't complete the install because
#         it is run as a child of the process it has to terminate.

#         So, let's get creative:

#         0. This logic assumes django is being run as root with sudo or
#            from the rc.local service.  It also assumes that 'apt-get update'
#            has already been run and we know there is an update available.

#         1. Write file /tmp/openagbrain-at-commands with contents:
#             systemctl stop rc.local
#             apt-get install -y openagbrain

#         2. Create an 'at' job which runs the above commands in a minute:
#             at -f /tmp/openagbrain-at-commands now + 1 minute"""
#         try:
#             fn = "/tmp/openagbrain-at-commands"
#             f = open(fn, "w")
#             f.write("systemctl stop rc.local\n")
#             f.write("apt-get install -y openagbrain\n")
#             f.close()

#             # update our debian package
#             cmd = [
#                 "at",
#                 "-f",
#                 "/tmp/openagbrain-at-commands",
#                 "now",
#                 "+",
#                 "1",
#                 "minute",
#             ]
#             subprocess.Popen(cmd)

#             UpgradeUtilities.ref_state.upgrade[
#                 "status"
#             ] = "Upgrading, will restart in 5 minutes..."
#             UpgradeUtilities.ref_state.upgrade["show_upgrade"] = False

#         except Exception as e:
#             UpgradeUtilities.ref_state.upgrade["error"] = e

#         return UpgradeUtilities.ref_state.upgrade

#     @staticmethod
#     def check():
#         """Checks for software updates."""
#         UpgradeUtilities.update_dict()
#         return UpgradeUtilities.get_status()
