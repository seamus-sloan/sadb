#!/usr/bin/python3

# Created by:   Seamus Sloan
# Last Edited:  July 10, 2023


import os
import sys
sys.path.append("..")

from sadb import select_device


def test_select_one_device(monkeypatch, testDeviceList):
    monkeypatch.setattr('builtins.input', lambda _: 1)

    device = select_device(testDeviceList)
    assert device == "FA79J1A00421"


def test_select_second_device(monkeypatch, testDeviceList):
    monkeypatch.setattr('builtins.input', lambda _: 2)

    device = select_device(testDeviceList)
    assert device == "ZY223TDZ43"


def test_select_all_devices(monkeypatch, testDeviceList):
    monkeypatch.setattr('builtins.input', lambda _: len(testDeviceList) + 1)

    device = select_device(testDeviceList, allow_all=True)
    assert device == testDeviceList


def test_display_of_no_devices(capsys):
    select_device([])
    captured = capsys.readouterr()
    assert captured.out == "No devices found\n"


def test_display_of_one_device(testDeviceList):
    devices = [testDeviceList[0]]
    assert select_device(devices) == "FA79J1A00421"


def test_select_device_multiple_devices(monkeypatch, capsys, testDeviceList):
    monkeypatch.setattr('builtins.input', lambda _: "1")
    select_device(testDeviceList)
    captured = capsys.readouterr()
    assert captured.out == """Select a device:
1. FA79J1A00421
2. ZY223TDZ43
3. HT4CJ0203660
4. R58M45YME1R
5. emulator-5554
"""


def test_display_of_multiple_devices_allow_all(monkeypatch, capsys, testDeviceList):
    monkeypatch.setattr('builtins.input', lambda _: "1")
    select_device(testDeviceList, allow_all=True)
    captured = capsys.readouterr()
    assert captured.out == """Select a device:
1. FA79J1A00421
2. ZY223TDZ43
3. HT4CJ0203660
4. R58M45YME1R
5. emulator-5554
6. ALL
"""
