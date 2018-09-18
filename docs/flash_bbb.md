# Part 3: Flash Image onto BBB

Back to [Part 2: Prepare SD Card Image](prepare_sd.md)...or...Forward to [Part 4: Provision BBB](provision_bbb.md)

## Install Steps
1. Download the latest image (unless you built your own) from [here](https://drive.google.com/drive/folders/1_8qds9_7xkiPrP8CDYuQaFylpPfw_vqI?usp=sharing)
2. Download [Etcher](https://etcher.io/) for flashing .iso files to SD cards
3. Insert the 8GB SD card into your computer and flash the downloaded image to it w/Etcher
4. Make sure BBB is *NOT Powered*
5. Plug in SD card to BBB
6. Apply power to BBB
7. Watch the 4 status LEDs on the BBB for boot then cylon activity (one LED bouncing back and forth) and eventually all LEDs on the BBB will shut off, including the power one.  This takes about 4 minutes.
8. Remove power from the NS board.
9. Remove the SD card from the BBB.
10. Apply power to the BBB. Wait 5 minutes for initial boot and self configuration.

Proceed to [Part 4: Provision BBB](provision_bbb.md)
