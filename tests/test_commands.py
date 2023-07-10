#!/usr/bin/python3

import os
import sys
from unittest.mock import ANY, MagicMock, call, mock_open, patch
from conftest import DEVICE_IDS

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, root_dir)
from sadb import stop, start, clear, install, uninstall, scrcpy, get_ip, screenshot, record, wifi, search

testApk = "myApp.apk"
testPackage = "com.example.app"
testDevice = DEVICE_IDS[0]


def test_stop():
    with patch("subprocess.run") as mock_run:
        stop(testDevice, testPackage)
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "shell", "am", "force-stop", testPackage])


def test_start():
    with patch("subprocess.run") as mock_run:
        start(testDevice, testPackage)
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "shell", "monkey", "-p",
           testPackage, "-c", "android.intent.category.LAUNCHER", "1"],
           stdout=ANY,
           stderr=ANY)


def test_clear():
    with patch("subprocess.run") as mock_run:
        clear(testDevice, testPackage)
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "shell", "pm", "clear", testPackage])


def test_install():
    with patch("subprocess.run") as mock_run:
        install(testDevice, testApk)
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "install", testApk])


def test_uninstall():
    with patch("subprocess.run") as mock_run:
        uninstall(testDevice, testPackage)
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "uninstall", testPackage])


def test_scrcpy():
    with patch("subprocess.run") as mock_run:
        scrcpy(testDevice)
        mock_run.assert_called_once_with(["scrcpy", "-s", testDevice])


def test_get_ip():
    with patch("subprocess.run") as mock_run:
        get_ip(testDevice)
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "shell", "ip", "addr", "show", "wlan0"], capture_output=True, text=True)


def test_screenshot_default_name():
    filename = "screenshot.png"
    with patch("builtins.open", mock_open()) as mock_file, patch("subprocess.run") as mock_run:
        screenshot(testDevice, filename)
        mock_file.assert_called_once_with(filename, "wb")
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "exec-out", "screencap", "-p"], stdout=mock_file.return_value)


def test_screenshot_custom_name():
    filename = "custom_screenshot_name.png"
    with patch("builtins.open", mock_open()) as mock_file, patch("subprocess.run") as mock_run:
        screenshot(testDevice, filename)
        mock_file.assert_called_once_with(filename, "wb")
        mock_run.assert_called_once_with(["adb", "-s", testDevice, "exec-out", "screencap", "-p"], stdout=mock_file.return_value)


def test_record_custom_name():
    filename = "custom.mp4"
    remote_path = "/sdcard/screenrecord.mp4"

    mock_proc = MagicMock()
    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen, \
            patch("subprocess.run") as mock_run, \
            patch("time.sleep", side_effect=[None, None, KeyboardInterrupt]) as mock_sleep:  
        record(testDevice, filename)
        mock_popen.assert_called_once_with(["adb", "-s", testDevice, "shell", f"screenrecord {remote_path}"])
        assert call(["adb", "-s", testDevice, "pull", remote_path, filename]) in mock_run.call_args_list
        assert call(["adb", "-s", testDevice, "shell", f"rm {remote_path}"]) in mock_run.call_args_list


def test_record_default_name():
    filename = "video.mp4"
    remote_path = "/sdcard/screenrecord.mp4"

    mock_proc = MagicMock()
    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen, \
            patch("subprocess.run") as mock_run, \
            patch("time.sleep", side_effect=[None, None, KeyboardInterrupt]) as mock_sleep:        
        record(testDevice, "")
        mock_popen.assert_called_once_with(["adb", "-s", testDevice, "shell", f"screenrecord {remote_path}"])
        assert call(["adb", "-s", testDevice, "pull", remote_path, filename]) in mock_run.call_args_list
        assert call(["adb", "-s", testDevice, "shell", f"rm {remote_path}"]) in mock_run.call_args_list


def test_wifi_success():
    ip_address = "192.168.1.1"
    with patch("sadb.get_ip", return_value=ip_address) as mock_get_ip, \
            patch("subprocess.run") as mock_run, \
            patch("builtins.print") as mock_print:
        wifi(testDevice)
        mock_get_ip.assert_called_once_with(testDevice)
        mock_run.assert_has_calls([
            call(["adb", "-s", testDevice, "tcpip", "5555"]),
            call(["adb", "connect", f"{ip_address}:5555"])
        ])


def test_search():
    search_term = "example"
    with patch("subprocess.run") as mock_run:
        search(testDevice, search_term)
        mock_run.assert_called_once_with(
            ["adb", "-s", testDevice, "shell", "pm", "list", "packages", "|", "grep", search_term]
        )
