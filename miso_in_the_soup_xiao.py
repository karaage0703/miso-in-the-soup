#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial


def open(port: str) -> None:
    global ser
    try:
        ser = serial.Serial(port, 9600, timeout=3)
    except serial.SerialException:
        ser = None
        print("Cannot find miso-in-the-soup-xiao device.")


def capture() -> list:
    if ser is None:
        return [
            0,
            0,
            0,
            0,
        ]

    values = None
    ser.write("capture".encode())
    while True:
        line = ser.readline().decode()
        if line == "ok\r\n":
            break
        values = line.split()

    return [int(v) for v in values]


def setLed(led_pattern: int) -> None:
    if ser is None:
        return

    ser.write(f"setLed {led_pattern}".encode())
    line = ser.readline().decode()
    if line != "ok\r\n":
        raise IOError()


def setVibration(vibration_pattern: int) -> None:
    if ser is None:
        return

    ser.write(f"setVibration {vibration_pattern}".encode())
    line = ser.readline().decode()
    if line != "ok\r\n":
        raise IOError()
