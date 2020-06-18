#!/usr/bin/env python3

import bluetooth._bluetooth as bluez
import struct
import redis
import time, datetime

OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
EVT_LE_ADVERTISING_REPORT = 0x02
LE_META_EVENT = 0x3e

class ExposureScanner:
    def __init__(self):
        self.sock = bluez.hci_open_dev(0)
        # Filter socket for HCI_EVENT_PKT
        fltr = bluez.hci_filter_new()
        bluez.hci_filter_all_events(fltr)
        bluez.hci_filter_set_ptype(fltr, bluez.HCI_EVENT_PKT)
        self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, fltr)
        self.db = redis.Redis(host="raspberry.local", port=6379, db=0)

    def toggle_scan(self, enable):
        if enable:
            self.set_scan_options()

        # True: Filter duplicates
        cmd = struct.pack(">BB", enable, False)
        bluez.hci_send_cmd(self.sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd)

    def set_scan_options(self):
        # 1. Should scanning be active?
        # 2. Set scan interval to 10ms
        # 3. Set scan window to 10ms
        # 4. Do not use a random bluetooth address
        # 5. Do not filter
        cmd = struct.pack(
            ">BHHBB",
            False,
            int(10 / 0.625),
            int(10 / 0.625),
            False,
            0x00)
        bluez.hci_send_cmd(self.sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, cmd)

    def handle(self, pkt):
        # Get 16 byte rolling identifier
        if len(pkt) < 14:
            return
        
        pkt = pkt[14:]

        flags = None
        service_class = None
        service_data = None

        i = 0
        while i < len(pkt):
            length = int(pkt[i])
            if i + length < len(pkt):
                if length >= 2:
                    key = pkt[i+1]
                    value = pkt[i+2 : i+1 + length][::-1].hex()
                    if key == 0x01:
                        flags = value
                    elif key == 0x03:
                        service_class = value
                    elif key == 0x16:
                        service_data = value
            i += length+1

        #if flags == "1a" and service_class == "fd86":
        if service_class == "fd6f" and len(service_data) == 44 and service_data[-4:] == "fd6f":
            key = service_data[0:32]
            if not len(key) == 32:
                return

            dt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.db.hsetnx(key, "first_seen", dt)
            self.db.hset(key, "last_seen", dt)
            self.db.hincrby(key, "seen_counter", 1)
            self.db.sadd("set:rolling", key)
            #print(key)
            #self.db.sadd("keys-list", "k:{}".format(key))

    def scan(self):
        self.toggle_scan(False)
        self.toggle_scan(True)
        while True:
            pkt = self.sock.recv(256)
            event = int(pkt[1])
            subevent = int(pkt[3])
            if event == LE_META_EVENT and subevent == EVT_LE_ADVERTISING_REPORT:
                self.handle(pkt)

    def __del__(self):
        self.toggle_scan(False)
        self.sock.close()

scanner = ExposureScanner()
scanner.scan()
