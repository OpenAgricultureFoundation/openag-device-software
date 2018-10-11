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
            devid = contents[index + 1:]
            return devid.rstrip()
    except:
        pass
    return None
