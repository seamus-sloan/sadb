"""Test device selection is working as expected"""
#!/usr/bin/python3

#pylint: disable=missing-function-docstring, wrong-import-position

# Created by:   Seamus Sloan
# Last Edited:  July 10, 2023

import sys
sys.path.append("..")
from sadb import select_device

def test_select_one_device(monkeypatch, test_device_list):
    monkeypatch.setattr('builtins.input', lambda _: 1)

    device = select_device(test_device_list)
    assert device == "FA79J1A00421"


def test_select_second_device(monkeypatch, test_device_list):
    monkeypatch.setattr('builtins.input', lambda _: 2)

    device = select_device(test_device_list)
    assert device == "ZY223TDZ43"


def test_select_all_devices(monkeypatch, test_device_list):
    monkeypatch.setattr('builtins.input', lambda _: len(test_device_list) + 1)

    device = select_device(test_device_list, allow_all=True)
    assert device == test_device_list


def test_display_of_no_devices(capsys):
    select_device([])
    captured = capsys.readouterr()
    assert captured.out == "No devices found\n"


def test_display_of_one_device(test_device_list):
    devices = [test_device_list[0]]
    assert select_device(devices) == "FA79J1A00421"


def test_select_device_multiple_devices(monkeypatch, capsys, test_device_list):
    monkeypatch.setattr('builtins.input', lambda _: "1")
    select_device(test_device_list)
    captured = capsys.readouterr()
    assert captured.out == """Select a device:
1. FA79J1A00421
2. ZY223TDZ43
3. HT4CJ0203660
4. R58M45YME1R
5. emulator-5554
"""


def test_display_of_multiple_devices_allow_all(monkeypatch, capsys, test_device_list):
    monkeypatch.setattr('builtins.input', lambda _: "1")
    select_device(test_device_list, allow_all=True)
    captured = capsys.readouterr()
    assert captured.out == """Select a device:
1. FA79J1A00421
2. ZY223TDZ43
3. HT4CJ0203660
4. R58M45YME1R
5. emulator-5554
6. ALL
"""
