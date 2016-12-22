weewx-ws3000

This is a driver for weewx that collects data from WS-3000 temperature/humidity
sensors.  The WS-3000 is a small console that receives data wirelessly from up
to 8 temperature/humidity sensors.

Installation

0) install weewx (see the weewx user guide)

1) download the driver

wget -O weewx-ws3000.zip https://github.com/matthewwall/weewx-ws3000/archive/master.zip

2) install the driver

wee_extension --install weewx-ws3000.zip

3) configure the driver

wee_config --reconfigure --driver=user.ws3000

4) start weewx

sudo /etc/init.d/weewx start
