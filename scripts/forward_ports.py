import uuid, os

# Get mac address
mac_addr = hex(uuid.getnode()).replace("0x", "")

# Build subdomain
subdomain = ".".join(mac_addr[i:i + 2] for i in range(0, 11, 2))

# Build bash command
command = "autossh -M 0 -R {subdomain}.serveo.net:80:localhost:80 serveo.net -R {subdomain}:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f".format(
    subdomain=subdomain
)

# Run bash command
print("Forwarding ports to {}".format(subdomain))
os.system(command)
