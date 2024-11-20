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


def readline(timeout: float) -> bytes:
    line = bytearray([])
    while True:
        b = ser.read()
        if len(b) != 1:
            print("WARNING: Timeout")
            return None

        line.append(b[0])
        if b[0] == 10:
            break

    return line.decode()


def capture() -> list:
    if ser is None:
        return [
            0,
            0,
            0,
            0,
        ]

    values = "  0   0   0   0\n".split()
    ser.write("capture".encode())
    while True:
        line = readline(3)
        if line is None:
            break
        if line == "ok\r\n":
            return [int(v) for v in values]
        values = line.split()

    ser.reset_input_buffer()

    values = "  0   0   0   0\n".split()
    ser.write("capture".encode())
    while True:
        line = readline(3)
        if line is None:
            break
        if line == "ok\r\n":
            return [int(v) for v in values]
        values = line.split()

    raise IOError()


def setLed(led_pattern: int) -> None:
    if ser is None:
        return

    ser.write(f"setLed {led_pattern}".encode())
    line = readline(3)
    if line == "ok\r\n":
        return

    ser.reset_input_buffer()

    ser.write(f"setLed {led_pattern}".encode())
    line = readline(3)
    if line == "ok\r\n":
        return

    raise IOError()


def setVibration(vibration_pattern: int) -> None:
    if ser is None:
        return

    ser.write(f"setVibration {vibration_pattern}".encode())
    line = readline(3)
    if line == "ok\r\n":
        return

    ser.reset_input_buffer()

    ser.write(f"setVibration {vibration_pattern}".encode())
    line = readline(3)
    if line == "ok\r\n":
        return

    raise IOError()
