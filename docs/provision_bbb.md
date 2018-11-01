# Part 4: Provision BBB

Back to [Part 3: Flash Image onto BBB](flash_bbb.md)...or...Forward to [Part 5: User Setup](user_setup.md)

## Create Beaglebone Label
1. Connect to beaglebone with usb cable
2. Login to beaglebone (via SSH)
   ```
   ssh debian@beaglebone.local
   # Password: openag12
   ```
3. Get BBB Serial Number
   ```
   ./scripts/get_bbb_serial.sh 
   ```
4. Get WIFI Access Point ID
   ```
   ./scripts/show_access_point.sh
   ```
5. Create label in the following format
   ```
   BBB: <BBB S/N>
   WIFI: <WIFI CODE>
   ```
   Example:
    ```
   BBB: 1712EW003727
   WIFI: 46D8
   ```
6. Print out and stick to the back of the beaglebone
