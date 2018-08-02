# Part 4: Provision BBB

Back to [Part 3: Flash Image onto BBB](flash_bbb.md)...or...Forward to [Part 5: User Setup](user_setup.md)

## Steps for BBB Wired
1. Create label in format below, and stick to back of beaglebone:
   ```
   S/N: <DEVICE>-<VERSION>-<NUMBER>
   ```
   Example:
   ```
   S/N: EDU-B-010
   ```
2. Open terminal on your laptop and login to beaglebone with
   ```
   ssh debian@beaglebone.local
   # Password: openag12
   ```

## Steps for BBB Wireless
1. With BBB Wireless powered, look for Beaglebone-XXXX in you list of wireless networks on your laptop, note the code (XXXX).
2. Create label in format below, and stick to back of beaglebone:
   ```
   S/N: <DEVICE>-<VERSION>-<NUMBER>
   WIFI: <CODE>
   ```
   Example:
   ```
   S/N: EDU-B-010
   WIFI: 4627
   ```
3. Connect your laptop to the Beaglebone's wireless access point using password `BeagleBone`
4. Open terminal on your laptop and login to beaglebone with
   ```
   ssh debian@192.168.8.1
   # Password: openag12
   ```
5. Connect beaglebone to your wireless internet
   ```
   cd ~/openag-device-software/scripts
   
   # List all the access points the BBB has access to
   ./get_wifis.sh

   # Choose the access point you want to connect to and copy the wifi_XXX service name
   ./connect_wifi.sh <wifi_XXX> <password if required>
   ```

## Steps for BBB Wireless + Wired
1. Verify internet connection by pinging google
   ```
   ping 8.8.8.8
   ```
   Correct output (GOOD):
   ```
   PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
   64 bytes from 8.8.8.8: icmp_seq=1 ttl=119 time=13.7 ms
   64 bytes from 8.8.8.8: icmp_seq=2 ttl=119 time=11.5 ms
   64 bytes from 8.8.8.8: icmp_seq=3 ttl=119 time=12.2 ms
   ```
   Incorrect output (BAD):
   ```
   connect: Network is unreachable
   ```






Edit about.json
3. etc.