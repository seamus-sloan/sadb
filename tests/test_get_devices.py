"""Test get devices is returning the correct devices"""
#!/usr/bin/python3

#pylint: disable=missing-function-docstring, wrong-import-position

# Created by:   Seamus Sloan
# Last Edited:  July 10, 2023

import sys
sys.path.append("..")
from sadb import split_get_devices

def test_get_devices_returns_correct_three_devices(test_devices):
    devices = split_get_devices(test_devices(3))
    print(devices)
    assert devices == ['FA79J1A00421', 'ZY223TDZ43', 'HT4CJ0203660']


def test_get_devices_returns_correct_five_devices(test_devices):
    devices = split_get_devices(test_devices(5))
    print(devices)
    assert devices == ["FA79J1A00421", "ZY223TDZ43",
                       "HT4CJ0203660", "R58M45YME1R", "emulator-5554"]


def test_get_devices_returns_correct_single_device(test_devices):
    devices = split_get_devices(test_devices(1))
    print(devices)
    assert devices == ['FA79J1A00421']


def test_get_devices_returns_correct_no_devices(test_devices):
    devices = split_get_devices(test_devices(0))
    print(devices)
    assert devices == []
