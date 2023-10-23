#!/usr/bin/python3

# Created by:   Seamus Sloan
# Last Edited:  July 10, 2023

import sys
from unittest.mock import ANY, MagicMock, call, mock_open, patch
from conftest import DEVICE_IDS
sys.path.append(".")
from sadb import stop, start, clear, install, uninstall
from sadb import scrcpy, get_ip, screenshot, record, wifi, search

TEST_APK = "myApp.apk"
TEST_PACKAGE = "com.example.app"
TEST_DEVICE = DEVICE_IDS[0]


def test_stop():
    with patch("subprocess.run") as mock_run:
        stop(TEST_DEVICE, TEST_PACKAGE)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", "am", "force-stop", TEST_PACKAGE])


def test_start():
    with patch("subprocess.run") as mock_run:
        start(TEST_DEVICE, TEST_PACKAGE)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", "monkey", "-p", TEST_PACKAGE,
                "-c", "android.intent.category.LAUNCHER", "1"],
            stdout=ANY, stderr=ANY
        )


def test_clear():
    with patch("subprocess.run") as mock_run:
        clear(TEST_DEVICE, TEST_PACKAGE)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", "pm", "clear", TEST_PACKAGE])


def test_install():
    with patch("subprocess.run") as mock_run:
        install(TEST_DEVICE, TEST_APK)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "install", TEST_APK])


def test_uninstall():
    with patch("subprocess.run") as mock_run:
        uninstall(TEST_DEVICE, TEST_PACKAGE)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "uninstall", TEST_PACKAGE])


def test_scrcpy():
    with patch("subprocess.run") as mock_run:
        scrcpy(TEST_DEVICE)
        mock_run.assert_called_once_with(["scrcpy", "-s", TEST_DEVICE])


def test_get_ip():
    with patch("subprocess.run") as mock_run:
        get_ip(TEST_DEVICE)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", "ip", "addr", "show", "wlan0"],
            capture_output=True, text=True)


def test_screenshot_default_name():
    filename = "screenshot.png"
    with patch("builtins.open", mock_open()) as mock_file, patch("subprocess.run") as mock_run:
        screenshot(TEST_DEVICE, filename)
        mock_file.assert_called_once_with(filename, "wb")
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "exec-out", "screencap", "-p"],
            stdout=mock_file.return_value)


def test_screenshot_custom_name():
    filename = "custom_screenshot_name.png"
    with patch("builtins.open", mock_open()) as mock_file, patch("subprocess.run") as mock_run:
        screenshot(TEST_DEVICE, filename)
        mock_file.assert_called_once_with(filename, "wb")
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "exec-out", "screencap", "-p"],
            stdout=mock_file.return_value)


def test_record_custom_name():
    filename = "custom.mp4"
    remote_path = "/data/local/tmp/screenrecord.mp4"

    mock_proc = MagicMock()
    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen, \
            patch("subprocess.run") as mock_run, \
            patch("time.sleep", side_effect=[None, None, KeyboardInterrupt]) as mock_sleep:
        record(TEST_DEVICE, filename)
        mock_popen.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", f"screenrecord {remote_path}"])
        assert call(["adb", "-s", TEST_DEVICE, "pull", remote_path,
                    filename]) in mock_run.call_args_list
        assert call(["adb", "-s", TEST_DEVICE, "shell",
                    f"rm {remote_path}"]) in mock_run.call_args_list


def test_record_default_name():
    filename = "video.mp4"
    remote_path = "/data/local/tmp/screenrecord.mp4"

    mock_proc = MagicMock()
    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen, \
            patch("subprocess.run") as mock_run, \
            patch("time.sleep", side_effect=[None, None, KeyboardInterrupt]) as mock_sleep:
        record(TEST_DEVICE, "")
        mock_popen.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", f"screenrecord {remote_path}"])
        assert call(["adb", "-s", TEST_DEVICE, "pull", remote_path,
                    filename]) in mock_run.call_args_list
        assert call(["adb", "-s", TEST_DEVICE, "shell",
                    f"rm {remote_path}"]) in mock_run.call_args_list


def test_wifi():
    ip_address = "192.168.1.1"
    with patch("sadb.get_ip", return_value=ip_address) as mock_get_ip, \
            patch("subprocess.run") as mock_run, \
            patch("builtins.print") as mock_print:
        wifi(TEST_DEVICE)
        mock_get_ip.assert_called_once_with(TEST_DEVICE)
        mock_run.assert_has_calls([
            call(["adb", "-s", TEST_DEVICE, "tcpip", "5555"]),
            call(["adb", "connect", f"{ip_address}:5555"])
        ])


def test_search():
    search_term = "example"
    with patch("subprocess.run") as mock_run:
        search(TEST_DEVICE, search_term)
        mock_run.assert_called_once_with(
            ["adb", "-s", TEST_DEVICE, "shell", "pm", "list",
                "packages", "|", "grep", search_term]
        )
