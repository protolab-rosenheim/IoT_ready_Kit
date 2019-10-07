# IoT Ready Kit #

## Todo after hypriot install
* Change hostname in user-data
* sudo apt-get update
* sudo apt-get upgrade
* passwd pirate
* sudo timedatectl set-timezone Europe/Berlin
* wget https://s-usv.de/files/software/susvd-en-2.40-systemd-pi.tar.gz
* tar -xvf susvd-en-2.40-systemd-pi.tar.gz
* sudo apt install python-smbus i2c-tools
* sudo apt install /home/pirate/susvd-en-2.40-systemd-pi.deb
* sudo raspi-config -> Interfacing -> enable I2C
* sudo reboot
* sudo i2cdetect -y 1 -> Two addresses have to be visible
* sudo hwclock -w -> Write time to hw clock
* cd /opt/susvd
* sudo ./susv -timer 5 -> Shutdown after 5 secs if rpi uses usv battery
* sudo ./susv -status -> Shutdown timer has to be at 5 seconds
* sudo ./susvd -start

## USV firmware update
* wget https://s-usv.de/files/firmware/susv_fw_261_pi.tar.gz
* cd /opt/susvd
* sudo ./susv -flash PATH_TO_HEX_FILE
* sudo ./susv -status