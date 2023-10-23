"""Test all functions are sending the correct commands"""
#!/usr/bin/python3

#pylint: disable=missing-function-docstring, wrong-import-position

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
DEFAULT_VIDEO_NAME = "video.mp4"
DEFAULT_VIDEO_SAVE_LOC = "/data/local/tmp/"


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


def test_record_default_name():
    expected_file_location = f"{DEFAULT_VIDEO_SAVE_LOC}{DEFAULT_VIDEO_NAME}"

    with patch("sadb.subprocess") as mock_subprocess, \
         patch("time.sleep", side_effect=[None, KeyboardInterrupt, None]) as mock_sleep, \
         patch("sadb.input", return_value='y') as mock_input:

        mock_popen = MagicMock()
        mock_subprocess.Popen.return_value = mock_popen
        mock_subprocess.run.return_value = MagicMock(returncode=0)

        # Call the function
        record(TEST_DEVICE, "")

        # Check if subprocess.Popen was called with correct arguments
        mock_subprocess.Popen.assert_called_once_with(["adb", "-s", TEST_DEVICE, "shell", \
                                                       f"screenrecord {expected_file_location}"])

        # Check if KeyboardInterrupt was handled correctly
        mock_popen.terminate.assert_called_once()

        # Check if subprocess.run was called with correct arguments for pulling the file
        assert mock_subprocess.run.call_args_list[0] == \
            call(["adb", "-s", TEST_DEVICE, "pull", expected_file_location, DEFAULT_VIDEO_NAME])

        # Check if subprocess.run was called with correct arguments for deleting the file
        assert mock_subprocess.run.call_args_list[1] == \
            call(["adb", "-s", TEST_DEVICE, "shell", f"rm {expected_file_location}"])


def test_record_custom_name():
    custom_name = "customName.mp4"
    expected_file_location = f"{DEFAULT_VIDEO_SAVE_LOC}{custom_name}"

    with patch("sadb.subprocess") as mock_subprocess, \
         patch("time.sleep", side_effect=[None, KeyboardInterrupt, None]) as mock_sleep, \
         patch("sadb.input", return_value='y') as mock_input:

        mock_popen = MagicMock()
        mock_subprocess.Popen.return_value = mock_popen
        mock_subprocess.run.return_value = MagicMock(returncode=0)

        # Call the function
        record(TEST_DEVICE, custom_name)

        # Check if subprocess.Popen was called with correct arguments
        mock_subprocess.Popen.assert_called_once_with(["adb", "-s", TEST_DEVICE, "shell", \
                                                       f"screenrecord {expected_file_location}"])

        # Check if KeyboardInterrupt was handled correctly
        mock_popen.terminate.assert_called_once()

        # Check if subprocess.run was called with correct arguments for pulling the file
        assert mock_subprocess.run.call_args_list[0] == \
            call(["adb", "-s", TEST_DEVICE, "pull", expected_file_location, custom_name])

        # Check if subprocess.run was called with correct arguments for deleting the file
        assert mock_subprocess.run.call_args_list[1] == \
            call(["adb", "-s", TEST_DEVICE, "shell", f"rm {expected_file_location}"])


def test_record_without_deleting_file():
    expected_file_location = f"{DEFAULT_VIDEO_SAVE_LOC}{DEFAULT_VIDEO_NAME}"

    with patch("sadb.subprocess") as mock_subprocess, \
         patch("time.sleep", side_effect=[None, KeyboardInterrupt, None]) as mock_sleep, \
         patch("sadb.input", return_value='n') as mock_input:

        mock_popen = MagicMock()
        mock_subprocess.Popen.return_value = mock_popen
        mock_subprocess.run.return_value = MagicMock(returncode=0)

        # Call the function
        record(TEST_DEVICE, DEFAULT_VIDEO_NAME)

        # Check if subprocess.Popen was called with correct arguments
        mock_subprocess.Popen.assert_called_once_with(["adb", "-s", TEST_DEVICE, "shell", \
                                                       f"screenrecord {expected_file_location}"])

        # Check if KeyboardInterrupt was handled correctly
        mock_popen.terminate.assert_called_once()

        # Check if subprocess.run was called with correct arguments for pulling the file
        assert mock_subprocess.run.call_args_list[0] == \
            call(["adb", "-s", TEST_DEVICE, "pull", "/data/local/tmp/video.mp4", "video.mp4"])

        # Check if subprocess.run was not called with arguments for deleting the file
        delete_call = call(["adb", "-s", TEST_DEVICE, "shell", f"rm {expected_file_location}"])
        assert delete_call not in mock_subprocess.run.call_args_list


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
