# Part 4: Provision BBB

Back to [Part 3: Flash Image onto BBB](flash_bbb.md)...or...Forward to [Part 5: User Setup](user_setup.md)

## Create Beaglebone Label
1. Connect to beaglebone with usb cable
2. Login to beaglebone (via SSH)
   ```
   ssh debian@beaglebone.local
   # Password: openag12
   ```
3. Get MAC Address
   ```
   python scripts/get_mac.py
   ```
4. Get WIFI Access Point ID
   ```
   ./scripts/show_access_point.sh
   ```
5. Create label in the following format
   ```
   MAC: <MAC ADDR>
   WIFI: <WIFI CODE>
   ```
   Example:
    ```
   MAC: 92:64:AE:5B:D9:4C
   WIFI: 46D8
   ```
6. Print out and stick to the back of the beaglebone
