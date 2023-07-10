#!/usr/bin/python3
import pytest


DEVICE_IDS = ["FA79J1A00421", "ZY223TDZ43", "HT4CJ0203660", "R58M45YME1R", "emulator-5554"]

@pytest.fixture
def testDeviceList():
    return DEVICE_IDS

@pytest.fixture
def testDevices():
    def _testDevices(number_of_devices):
        result = "List of devices attached\n"
        for i in range(number_of_devices):
            result += DEVICE_IDS[i] + "\tdevice\n"
        return result
    return _testDevices