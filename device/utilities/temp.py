import re


def parse(line):

    # Get active id
    tokens = re.findall("\*\S*", line)
    if len(tokens) == 1:
        id_ = tokens[0]
    else:
        id_ = ""

    # Get psk
    tokens = re.findall("wifi_\S*", line)
    if len(tokens) == 1:
        psk = tokens[0]
    else:
        psk = ""

    # Get ssid
    ssid = line.replace(id_, "").replace(psk, "").strip()
    # ssid = re.findall("[^\*\S*]\S*", line)

    return id_, ssid, psk


line1 = "*AO Electric Elephant     wifi_f45eabf5dc15_456c656374726963456c657068616e74_managed_psk"
line2 = "                         wifi_f45eabf5dc15_hidden_managed_psk"
print(parse(line2))


# id, ssid, psk = parse(line)
