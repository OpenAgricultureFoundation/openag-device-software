import uuid

mac_addr = hex(uuid.getnode()).replace("0x", "")
print(":".join(mac_addr[i:i + 2] for i in range(0, 11, 2)))
