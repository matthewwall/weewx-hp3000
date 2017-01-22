#!/usr/bin/env python
# Copyright 2016 Matthew Wall
# Distributed under the terms of the GNU Public License (GPLv3)

"""
Collect data from the WS-3000 console via USB.

  Ambient Weather WS-3000-X5
  Ambient Weather WS-3000-X3

The WS-3000 supports up to 8 remote temperature/humidity sensors.  The console
has a 3"x4" TFT color display, with graph and room for 5 sensor displays.  The
sensor display regions can cycle through different sensors when more than 5
sensors are connected.

Every configuration option in the console can be modified via software.  These
options includes:

 - archive interval
 - date/time
 - date/time format
 - timezone
 - which sensors should be displayed in the 5 display regions
 - horizontal graph axis scaling
 - vertical graph axis
 - calibration for temperature/humidity from each sensor
 - alarms
 - historical data

Historical data are saved to the (optional) microSD card.  If no card is
installed, no data are retained.

Each sensor has its own display of temperature and humidity.

Each sensor is idenfified by channel number.  The channel number is set using
DIP switches on each sensor.  The DIP switches also determine which units will
be displayed in each sensor.

There are 4 two-position DIP switches.  DIP 4 determines units: 0=F 1=C
DIP 1-3 determine which of 8 channels is selected.

Data from sensors is received every 60 seconds.

Each sensor uses 2 AA batteries.  Nominal battery life is 1 year.

The console uses 5V DC from an AC/DC transformer.

Dewpoint and heatindex are calculated within the console.

Temperature sensors measure to +/- 2 degree F

Humidity sensors measure to +/- 5 %

Calibrations are applied in the console, so the values received from the
console are calibrated.  Calculations in the console are performed in degree C.

The console has a radio controlled clock.  During RCC reception, no data will
be transmitted.  If no RCC is received, attempt will be made every two hours
until successful.

This driver was developed without any assistance from Ambient Weather or the
actual manufacter of the WS-3000 hardware.

===============================================================================
Messages from console

The console sends data in 64-byte chunks.  It looks like the console reuses a
buffer, because each message shorter than the previous contains bytes from the
previous message.  The byte sequence 0x40 0x7d indicates end of data within a
buffer.

Many of the console messages correspond with the control messages sent from
the host.

configuration state (30 bytes)

00 7b
01 00 graph type
02 48 graph hours
03 01 time format
04 00 date format
05 00 dst
06 fb timezone
07 01 units
08 00
09 00
0a 00
0b 07 area1
0c 00
0d 00
0e 00
0f 00 area2
10 00
11 00
12 00
13 00 area3
14 00
15 00
16 00
17 00 area4
18 00
19 00
1a 00
1b 00 area5
1c 40
1d 7d

interval (4 bytes)

00 7b
01 05 interval in minutes
02 40
03 7d

unknown (9 bytes)

00 7b
01 01
02 01
03 00
04 00
05 00
06 00
07 40
08 7d

current data (27 bytes)

00 7b
01 00 ch1 temp MSB
02 eb ch1 temp LSB    t1 = (MSB * 256 + LSB) / 10.0
03 25 ch1 hum         h1 = hum
04 7f ch2 temp MSB
05 ff ch2 temp LSB
06 ff ch2 hum
07 7f ch3 temp MSB
08 ff ch3 temp LSB
09 ff ch3 hum
0a 7f ch4 temp MSB
0b ff ch4 temp LSB
0c ff ch4 hum
0d 7f ch5 temp MSB
0e ff ch5 temp LSB
0f ff ch5 hum
10 7f ch6 temp MSB
11 ff ch6 temp LSB
12 ff ch6 hum
13 7f ch7 temp MSB
14 ff ch7 temp LSB
15 ff ch7 hum
16 7f ch8 temp MSB
17 ff ch8 temp LSB
18 ff ch8 hum
19 40
1a 7d

calibration (27 bytes)

00 7b
01 00 ch1 temp MSB
02 00 ch1 temp LSB    tcal1 = (MSB * 256 + LSB) / 10.0
03 00 ch1 hum         hcal1 = hum
04 00 ch2 temp MSB
05 00 ch2 temp LSB
06 00 ch2 hum
07 00 ch3 temp MSB
08 00 ch3 temp LSB
09 00 ch3 hum
0a 00 ch4 temp MSB
0b 00 ch4 temp LSB
0c 00 ch4 hum
0d 00 ch5 temp MSB
0e 00 ch5 temp LSB
0f 00 ch5 hum
10 00 ch6 temp MSB
11 00 ch6 temp LSB
12 00 ch6 hum
13 00 ch7 temp MSB
14 00 ch7 temp LSB
15 00 ch7 hum
16 00 ch8 temp MSB
17 00 ch8 temp LSB
18 00 ch8 hum
19 40
1a 7d

humidity alarm configuration (19 bytes)

00 7b
01 5a ch1 hi    0x5a = 90 %
02 14 ch1 lo    0x14 = 20 %
03 5a ch2 hi
04 14 ch2 lo
05 5a ch3 hi
06 14 ch3 lo
07 5a ch4 hi
08 14 ch4 lo
09 5a ch5 hi
0a 14 ch5 lo
0b 5a ch6 hi
0c 14 ch6 lo
0d 5a ch7 hi
0e 14 ch7 lo
0f 5a ch8 hi
10 14 ch8 lo
1a 40
1b 7d

temperature alarm configuration (35 bytes)

00 7b
01 01 ch1 hi  (0x01*256 + 0x2c) / 10.0 = 30.0 C
02 2c
03 00 ch1 lo  (0x00*256 + 0x64) / 10.0 = 10.0 C
04 64
05 01 ch2 hi
06 2c
07 00 ch2 lo
08 64
09 01 ch3 hi
0a 2c
0b 00 ch3 lo
0c 64
0d 01 ch4 hi
0e 2c
0f 00 ch4 lo
10 64
11 01 ch5 hi
12 2c
13 00 ch5 lo
14 64
15 01 ch6 hi
16 2c
17 00 ch6 lo
18 64
19 01 ch7 hi
1a 2c
1b 00 ch7 lo
1c 64
1d 01 ch8 hi
1e 2c
1f 00 ch8 lo
20 64
21 40
22 7d

===============================================================================
Messages to console

The host sends a sequence of what appear to be empty commands:

7b 06 40 7d
7b 08 40 7d
7b 09 40 7d
7b 05 40 7d
7b 03 40 7d
7b 04 40 7d
7b 41 40 7d

The buffer termination is 0x40 0x7d.

set configuration command (0x10)
00 7b
01 10
02 00 graph type  0=temperature 1=humidity 2=dewpoint 3=heatindex
03 48 graph hours 0x0c=12H 0x18=24H 0x30=48H 48=72H
04 00 time format 0='h:mm:ss' 1='am h:mm:ss' 2='h:mm:ss am'
05 00 date format 0='dd-mm-yyyy' 1='mm-dd-yyyy' 2='yyyy-mm-dd'
06 00 dst         0=off 1=on
07 fb timezone    0xNN - 0x100 if (0xNN & 0xf0 == 0xf0) else 0xNN
08 00 units       1=F 0=C
09 00
0a 00
0b 00
0c 07 area1 01=temp 02=dew 03=temp/dew 07=temp/dew/heat
0d 00
0e 00
0f 00
10 08 area2 08=temp 20=heat 38=temp/dew/heat  (3f=1+2=temp/dew/heat ?)
11 00
12 00
13 00
14 00 area3?
15 00
16 00
17 00
18 00 area4?
19 00
1a 00
1b 00
1c 00 area5?
1d 40
1e 7d

set calibration command (0x11)
00 7b
01 11
02 00
03 0a ch1.T  t*10
04 00 ch1.H
05 00
06 14 ch2.T  t*10
07 00 ch2.H
08 00
09 00 ch3.T
0a 00 ch3.H
0b 00
0c 00 ch4.T
0d 00 ch4.H
0e 00
0f 32 ch5.T  t*10
10 00 ch5.H
11 00
12 00 ch6.T
13 00 ch6.H
14 00
15 00 ch7.T
16 00 ch7.H
17 00
18 00 ch8.T
19 00 ch8.H
1a 40
1b 7d

sync time command (0x30)
00 7b
01 30
02 07 year MSB
03 e0 year LSB
04 0c month
05 11 day-of-month
06 00 hour
07 27 minute
08 0c second?
09 06
0a 40
0b 7d

set interval command (0x40)
00 7b
01 40
02 05 interval in minutes (5-240)
03 40
04 7d

"""

# FIXME: set backlight (enable/disable; on time; off time)
# FIXME: re-register sensors
# FIXME: set alarms (temp on/off; hum on/off; hi/lo temps; hi/lo hums)
# FIXME: clear min/max
# FIXME: get min/max values
# FIXME: verify encoding of negative temperature values
# FIXME: verify encoding of negative timezone offsets

from __future__ import with_statement
import Queue
import syslog
import threading
import time
import usb

import weewx.drivers

DRIVER_NAME = 'WS3000'
DRIVER_VERSION = '0.2'

def loader(config_dict, _):
    return WS3000Driver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    return WS3000ConfigurationEditor()


def logmsg(level, msg):
    syslog.syslog(level, 'ws3000: %s: %s' %
                  (threading.currentThread().getName(), msg))

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


def _fmt(buf):
    if buf:
        return "%s (len=%s)" % (' '.join(["%02x" % x for x in buf]), len(buf))
    return ''


class WS3000ConfigurationEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[WS3000]
    # This section is for WS-3000 sensors

    # The model name such as Ambient WS-3000-X5
    model = WS3000

    # The driver to use
    driver = user.ws3000
"""


class WS3000Driver(weewx.drivers.AbstractDevice):

    DEFAULT_MAP = {
        'inTemp': 't_1',
        'inHumidity': 'h_1',
        'outTemp': 't_2',
        'outHumidity': 'h_2',
        'extraTemp1': 't_3',
        'extraHumid1': 'h_3',
        'extraTemp2': 't_4',
        'extraHumid2': 'h_4',
        'extraTemp3': 't_5',
        'extraHumid3': 'h_5',
        'extraTemp4': 't_6',
        'extraHumid4': 'h_6',
        'extraTemp5': 't_7',
        'extraHumid5': 'h_7',
        'extraTemp6': 't_8',
        'extraHumid6': 'h_8'}

    def __init__(self, **stn_dict):
        loginf('driver version is %s' % DRIVER_VERSION)
        loginf('usb info: %s' % get_usb_info())
        self._model = stn_dict.get('model', 'WS3000')
        self._sensor_map = dict(WS3000Driver.DEFAULT_MAP)
        if 'sensor_map' in stn_dict:
            self._sensor_map.update(stn_dict['sensor_map'])
        loginf('sensor map: %s' % self._sensor_map)
        self._station = WS3000Station()
        self._station.open()
        self._queue = Queue.Queue()
        self._thread = WS3000Thread(self._station, self._queue)
        self._thread.start()

    def closePort(self):
        if self._thread:
            self._thread.running = False
            self._thread.join()
            self._thread = None
        self._station.close()

    def hardware_name(self):
        return self._model

    def genLoopPackets(self):
        while True:
            try:
                data = self._queue.get(True, 10)
                logdbg('data: %s' % data)
                if data.get('type') == 'sensor_values':
                    pkt = self._data_to_packet(data)
                    logdbg('packet: %s' % pkt)
                    yield pkt
            except Queue.Empty:
                logdbg('empty queue')

    def _data_to_packet(self, data):
        # map sensor data to database fields
        pkt = {'dateTime': int(time.time() + 0.5), 'usUnits': weewx.METRICWX}
        for x in self._sensor_map:
            if self._sensor_map[x] in data:
                pkt[x] = data[self._sensor_map[x]]
        return pkt


class WS3000Thread(threading.Thread):
    def __init__(self, station, queue):
        threading.Thread.__init__(self)
        self.name = 'data-thread'
        self.station = station
        self.queue = queue
        self.running = False

    def run(self):
        self.running = True
        self.station.open()
        while self.running:
            raw = self.station.get_data()
            if raw:
                self.queue.put(raw)
        self.station.close()


class USBHID(object):
    def __init__(self, vendor_id, product_id, iface=0, timeout=1000):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.iface = iface
        self.timeout = timeout
        self.devh = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _, value, traceback):
        self.close()

    def open(self):
        dev = self._find_dev(self.vendor_id, self.product_id)
        if not dev:
            logerr("Cannot find USB device with VendorID=0x%04x ProductID=0x%04x" % (self.vendor_id, self.product_id))
            raise weewx.WeeWxIOError('Unable to find station on USB')

        self.devh = dev.open()
        if not self.devh:
            raise weewx.WeeWxIOError('Open USB device failed')

        # be sure kernel does not claim the interface on linux systems
        try:
            self.devh.detachKernelDriver(self.iface)
        except (AttributeError, usb.USBError):
            pass

        # attempt to claim the interface
        try:
            self.devh.claimInterface(self.iface)
            self.devh.setAltInterface(self.iface)
        except usb.USBError, e:
            self.close()
            logerr("Unable to claim USB interface %s: %s" % (self.iface, e))
            raise weewx.WeeWxIOError(e)

    def close(self):
        if self.devh:
            try:
                self.devh.releaseInterface()
            except (ValueError, usb.USBError), e:
                logerr("release interface failed: %s" % e)
            self.devh = None

    def _write(self, buf):
        pass

    def _read(self):
        return None

    def _reset(self):
        # use a usb reset to restore communication with the station.
        # specific cases include when you do an interrupt write with bogus
        # data.  use a reset to bring the station back to responsiveness.
        for x in range(5):
            try:
                self.devh.reset()
                break
            except usb.USBError, e:
                logdbg("usb reset failed: %s" % e)
                time.sleep(2)

    @staticmethod
    def _find_dev(vendor_id, product_id):
        """Find the vendor and product ID on the USB."""
        for bus in usb.busses():
            for dev in bus.devices:
                if dev.idVendor == vendor_id and dev.idProduct == product_id:
                    loginf('Found device on USB bus=%s device=%s' %
                           (bus.dirname, dev.filename))
                    return dev
        return None

    KNOWN_USB_MESSAGES = [
        'No data available', 'No error',
        'Nessun dato disponibile', 'Nessun errore',
        'Keine Daten verfügbar',
        'No hay datos disponibles',
        'Pas de données disponibles'
        ]

    # these are the usb 'errors' that should be ignored
    @staticmethod
    def known_usb_err(e):
        errmsg = repr(e)
        for msg in USBHID.KNOWN_USB_MESSAGES:
            if msg in errmsg:
                return True
        return False

    @staticmethod
    def get_usb_info():
        pyusb_version = '0.4.x'
        try:
            pyusb_version = usb.__version__
        except AttributeError:
            pass
        return "pyusb_version=%s" % pyusb_version


class WS3000Station(object):
    # usb values obtained from 'sudo lsusb -v'
    USB_ENDPOINT_IN = 0x82
    USB_ENDPOINT_OUT = 0x02
    USB_PACKET_SIZE = 0x40 # 64 bytes

    def __init__():
        super(USBHID, self).__init__(0x0483, 0x5750)

    def _write(self, buf):
        logdbg("write: %s" % _fmt(buf))
        cnt = self.devh.interruptWrite(
            self.USB_ENDPOINT_OUT, buf, self.timeout)
        if cnt != len(buf):
            raise weewx.WeeWxIOError('write: bad write length: '
                                     '%s != %s' % (cnt, len(buf)))

    def _read(self, timeout=None):
        if timeout is None:
            timeout = self.timeout
        buf = self.devh.interruptRead(
            self.USB_ENDPOINT_IN,
            self.USB_PACKET_SIZE,
            timeout)
        if not buf:
            return None
        logdbg("read: %s" % _fmt(buf))
        if len(buf) != 64:
            raise weewx.WeeWxIOError('read: bad buffer length: '
                                     '%s != 64' % len(buf))
        if buf[0] != 0x7b:
            raise weewx.WeeWxIOError('read: bad first byte: '
                                     '0x%02x != 0x7b' % buf[0])
        idx = None
        try:
            i = buf.index(0x40)
            if buf[i + 1] == 0x7d:
                idx = i
        except ValueError, IndexError:
            pass
        if idx is None:
            raise weewx.WeeWxIOError('read: no terminating bytes in buffer: '
                                     '%s' % _fmt(buf))
        return buf[0: idx]

    def send_cmd(self, cmd):
        self._write([0x7b, cmd, 0x40, 0x7d])

    def send_06(self):
        self.send_cmd(0x06)

    def send_08(self):
        self.send_cmd(0x08)

    def send_09(self):
        self.send_cmd(0x09)

    def send_05(self):
        self.send_cmd(0x05)

    def send_03(self):
        self.send_cmd(0x03)

    def send_04(self):
        self.send_cmd(0x04)

    def send_41(self):
        self.send_cmd(0x41)

    def send_sequence(self):
        self.send_06()
        self.send_08()
        self.send_09()
        self.send_05()
        self.send_03()
        self.send_04()
        self.send_41()

    def recv(self):
        return self._read(timeout=100)

    @staticmethod
    def raw_to_pkt(buf):
        logdbg("raw: %s" % _fmt(buf))
        pkt = dict()
        if len(buf) == 4: # archive interval
            pkt['type'] = 'interval'
            pkt['interval'] = buf[1]
        elif len(buf) == 30: # configuration
            pkt['type'] = 'configuration'
            pkt['graph_type'] = WS3000Station.decode_graph_type(buf[1])
            pkt['graph_hours'] = buf[2]
            pkt['time_format'] = WS3000Station.decode_time_format(buf[3])
            pkt['date_format'] = WS3000Station.decode_date_format(buf[4])
            pkt['dst'] = WS3000Station.decode_dst(buf[5])
            pkt['timezone'] = WS3000Station.decode_timezone(buf[6])
            pkt['units'] = WS3000Station.decode_units(buf[7])
            pkt['area1'] = buf[11]
            pkt['area2'] = buf[15]
            pkt['area3'] = buf[19]
            pkt['area4'] = buf[23]
            pkt['area5'] = buf[27]
        elif len(buf) == 19: # humidity alarm
            pkt['type'] = 'alarm_humidity'
            for ch in range(8):
                idx = 1 + ch * 2
                pkt['hhi_%s' % ch] = buf[idx]
                pkt['hlo_%s' % ch] = buf[idx + 1]
        elif len(buf) == 35: # temperature alarm
            pkt['type'] = 'alarm_temperature'
            for ch in range(8):
                idx = 1 + ch * 4
                pkt['thi_%s' % ch] = (buf[idx] * 256 + buf[idx + 1]) / 10.0
                pkt['tlo_%s' % ch] = (buf[idx + 2] * 256 + buf[idx + 3]) / 10.0
        elif len(buf) == 27: # sensor calibration
            pkt['type'] = 'sensor_calibration'
            for ch in range(8):
                idx = 1 + ch * 3
                pkt['tc_%s' % ch] = (buf[idx] * 256 + buf[idx + 1]) / 10.0
                pkt['hc_%s' % ch] = buf[idx + 2]
        elif len(buf) == 27: # sensor values
            pkt['type'] = 'sensor_values'
            for ch in range(8):
                idx = 1 + ch * 3
                t = None
                if buf[idx] != 0x7f and buf[idx + 1] != 0xff:
                    t = (buf[idx] * 256 + buf[idx + 1]) / 10.0
                pkt['t_%s' % ch] = t
                h = None
                if buf[idx + 2] != 0xff:
                    h = buf[idx + 2]
                pkt['h_%s' % ch] = h
        else:
            logdbg("unknown data: %s" % _fmt(buf))
        logdbg("pkt: %s" % pkt)
        return pkt

    @staticmethod
    def decode_graph_type(x):
        if x == 0:
            return 'temperature'
        elif x == 1:
            return 'humidity'
        elif x == 2:
            return 'dewpoint'
        elif x == 3:
            return 'heatindex'
        return None

    @staticmethod
    def decode_time_format(x):
        if x == 0:
            return 'h:mm:ss'
        elif x == 1:
            return 'AM h:mm:ss'
        elif x == 2:
            return 'h:mm:ss AM'
        return None

    @staticmethod
    def decode_date_format(x):
        if x == 0:
            return 'dd-mm-yyyy'
        elif x == 1:
            return 'mm-dd-yyyy'
        elif x == 2:
            return 'yyyy-mm-dd'
        return None

    @staticmethod
    def decode_dst(x):
        if x == 0:
            return 'off'
        elif x == 1:
            return 'on'
        return None

    @staticmethod
    def decode_timezone(x):
        if (x & 0xf0) == 0xf0:
            return x - 0x100
        return x

    @staticmethod
    def decode_units(x):
        if x == 0:
            return 'degree_C'
        elif x == 1:
            return 'degree_F'
        return None


# define a main entry point for basic testing of the station.  invoke this as
# follows from the weewx root dir:
#
# PYTHONPATH=bin python bin/user/ws3000.py

if __name__ == '__main__':

    import optparse

    usage = """%prog [options] [--debug] [--help]"""

    syslog.openlog('ws3000', syslog.LOG_PID | syslog.LOG_CONS)
    syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='display driver version')
    parser.add_option('--debug', dest='debug', action='store_true',
                      help='display diagnostic information while running')
    (options, args) = parser.parse_args()

    if options.version:
        print "driver version %s" % DRIVER_VERSION
        exit(1)

    if options.debug:
        syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))

    with WS3000Station() as s:
        queue = Queue.Queue()
        t = WS3000Thread()
        t.listen(s, queue)
        while True:
            try:
                raw = queue.get(True, 10)
                print "raw: %s" % raw
                pkt = WS3000Station.raw_to_pkt(raw)
                print "pkt: %s" % pkt
            except Queue.Empty:
                pass
            except KeyboardInterrupt:
                break
        t.stop_listening()
