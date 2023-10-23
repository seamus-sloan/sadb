"""Test all functions are sending the correct commands"""
#!/usr/bin/python3

#pylint: disable=missing-function-docstring, wrong-import-position
# Created by:   Seamus Sloan
# Last Edited:  July 10, 2023

import pytest


DEVICE_IDS = ["FA79J1A00421", "ZY223TDZ43", "HT4CJ0203660", "R58M45YME1R", "emulator-5554"]

@pytest.fixture
def test_device_list():
    return DEVICE_IDS

@pytest.fixture
def test_devices():
    def _test_devices(number_of_devices):
        result = "List of devices attached\n"
        for i in range(number_of_devices):
            result += DEVICE_IDS[i] + "\tdevice\n"
        return result
    return _test_devices