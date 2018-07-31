# Import standard python libraries
import sys, os, json, requests, subprocess, shlex


def connect(subdomain):
    print("Forwarding ports: {}".format(subdomain))
    command = "autossh -M 0 -R {}.serveo.net:80:localhost:8000 serveo.net -R {}:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f".format(
        subdomain, subdomain
    )
    os.system(command)


# Run main
if __name__ == "__main__":
    about = json.load(open("../about.json"))
    serial_number = about.get("serial_number", None)

    # Check for valid device id
    if serial_number != "<DEVICE>-<VERSION>-<ID>" and serial_number != None:
        subdomain = serial_number.replace("-", ".")
        connect(subdomain)
        sys.exit(0)

    # Search for valid developer device ID (check 10 devices)
    valid_url = None
    for i in range(1, 10):
        url = "http://dev.bbb.{:03}.serveo.net".format(i)
        response = requests.get(url)
        if response.status_code != 200:
            valid_url = url
            subdomain = "dev.bbb.{:03}".format(i)
            break

    # Check if found a valid url
    if valid_url != None:
        connect(subdomain)
    else:
        print("Unable to find valid url")
