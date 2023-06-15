# Created by:   Seamus Sloan
# Last Edited:  June 15, 2023

import argparse
import os
import sys
import subprocess
import time


def get_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    devices = [line.split()[0] for line in lines]
    return devices


def select_device(devices, allow_all=False):
    if len(devices) == 0:
        print("No devices found")
        return None
    if len(devices) == 1:
        return devices[0]
    print("Select a device:")
    for i, device in enumerate(devices):
        print(f"{i + 1}. {device}")
    if allow_all:
        print(f"{len(devices) + 1}. ALL")
    while True:
        try:
            choice = input("Enter the number of the device: ")
            index = int(choice) - 1
            if 0 <= index < len(devices):
                return devices[index]
            elif allow_all and index == len(devices):
                return devices
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")


def stop(device, package_name):
    cmd = ["adb", "-s", device, "shell", "am", "force-stop", package_name]
    subprocess.run(cmd)


def start(device, package_name):
    cmd = ["adb", "-s", device, "shell", "monkey", "-p",
           package_name, "-c", "android.intent.category.LAUNCHER", "1"]
    with open("/dev/null", "w") as devnull:
        subprocess.run(cmd, stdout=devnull, stderr=devnull)


def clear(device, package_name):
    cmd = ["adb", "-s", device, "shell", "pm", "clear", package_name]
    subprocess.run(cmd)


def install(device, apk):
    cmd = ["adb", "-s", device, "install", apk]
    subprocess.run(cmd)


def uninstall(device, package_name):
    cmd = ["adb", "-s", device, "uninstall", package_name]
    subprocess.run(cmd)


def scrcpy(device):
    cmd = ["scrcpy", "-s", device]
    subprocess.run(cmd)


def get_ip(device):
    cmd = ["adb", "-s", device, "shell", "ip", "addr", "show", "wlan0"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    for line in lines:
        if "inet" in line and not "inet6" in line:
            ip_address = line.strip().split()[1].split("/")[0]
            print(f"{device}'s IP address is:\t {ip_address}")
            return ip_address


def screenshot(device, filename):
    if not filename:
        filename = "screenshot.png"
    cmd = ["adb", "-s", device, "exec-out", "screencap", "-p"]
    with open(filename, "wb") as f:
        result = subprocess.run(cmd, stdout=f)
        if result.returncode == 0:
            print(f"Screenshot saved to {filename}")


def record(device, filename):
    if not filename:
        filename = "video.mp4"
    remote_path = "/sdcard/screenrecord.mp4"

    cmd = ["adb", "-s", device, "shell", f"screenrecord {remote_path}"]
    proc = subprocess.Popen(cmd)

    print("Recording... Press CTRL-C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        proc.terminate()

    cmd = ["adb", "-s", device, "pull", remote_path, filename]
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"Screen recording saved to {filename}")

    cmd = ["adb", "-s", device, "shell", f"rm {remote_path}"]
    subprocess.run(cmd)


def wifi(device):
    ip_address = get_ip(device)

    if not ip_address:
        print("Could not get IP address of device")
        return

    cmd = ["adb", "-s", device, "tcpip", "5555"]
    subprocess.run(cmd)

    cmd = ["adb", "connect", f"{ip_address}:5555"]
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"Connected to {device} via WiFi")


def search(device, search_term):
    cmd = ["adb", "-s", device, "shell", "pm",
           "list", "packages", "|", "grep", search_term]
    subprocess.run(cmd)


def parse_args():
    parser = argparse.ArgumentParser(
        description="A wrapper for adb on multiple devices")
    subparsers = parser.add_subparsers(dest="command")

    # Stop
    stop_parser = subparsers.add_parser("stop", help="Stop a package")
    stop_parser.add_argument(
        "package_name", help="The name of the package to stop")

    # Start
    start_parser = subparsers.add_parser("start", help="Start a package")
    start_parser.add_argument(
        "package_name", help="The name of the package to start")

    # Clear
    clear_parser = subparsers.add_parser(
        "clear", help="Clear storage for a package")
    clear_parser.add_argument(
        "package_name", help="The name of the package to clear")

    # Install
    install_parser = subparsers.add_parser("install", help="Install an APK")
    install_parser.add_argument(
        "apk", help="The path to the APK to install")

    # Uninstall
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Uninstall a package")
    uninstall_parser.add_argument(
        "package_name", help="The name of the package to uninstall")

    # Screencopy
    subparsers.add_parser("scrcpy", help="Start scrcpy on a device")

    # IP Address
    subparsers.add_parser("ip", help="Get the selected device's IP address")

    # Screenshot
    screenshot_parser = subparsers.add_parser(
        "screenshot", help="Take a screenshot of a device")
    screenshot_parser.add_argument(
        "-f", "--filename", help="The name of the file to save the screenshot as (default: screenshot.png)")

    # Record
    record_parser = subparsers.add_parser(
        "record", help="Record the screen of a device (Press CTRL-C to stop recording)")
    record_parser.add_argument(
        "-f", "--filename", help="The name of the file to save the screen recording as (default: video.mp4)")

    # WiFi
    wifi_parser = subparsers.add_parser(
        "wifi", help="Connect to a device via WiFi")

    # Search
    search_parser = subparsers.add_parser(
        "search", help="Search for an installed package")
    search_parser.add_argument(
        "search_term", help="The name of the package to search for")

    # R (Unwrapped)
    r_parser = subparsers.add_parser("r", help="Run an adb command")
    r_parser.add_argument(
        "args", help="Any argument you would normally pass through adb", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    return args


def main():
    try:
        args = parse_args()
        devices = get_devices()

        if args.command == "stop":
            selected_devices = select_device(devices, allow_all=True)
            if selected_devices is None:
                return
            for device in selected_devices:
                stop(device, args.package_name)

        elif args.command == "start":
            selected_devices = select_device(devices, allow_all=True)
            if selected_devices is None:
                return
            for device in selected_devices:
                start(device, args.package_name)

        elif args.command == "clear":
            selected_devices = select_device(devices, allow_all=True)
            if selected_devices is None:
                return
            for device in selected_devices:
                clear(device, args.package_name)

        elif args.command == "install":
            selected_devices = select_device(devices, allow_all=True)
            if selected_devices is None:
                return
            for device in selected_devices:
                install(device, args.apk)

        elif args.command == "uninstall":
            selected_devices = select_device(devices, allow_all=True)
            if selected_devices is None:
                return
            for device in selected_devices:
                uninstall(device, args.package_name)

        elif args.command == "scrcpy":
            device = select_device(devices)
            if device is None:
                return
            scrcpy(device)

        elif args.command == "ip":
            device = select_device(devices)
            if device is None:
                return
            get_ip(device)

        elif args.command == "screenshot":
            device = select_device(devices)
            if device is None:
                return
            screenshot(device, args.filename)

        elif args.command == "record":
            device = select_device(devices)
            if device is None:
                return
            record(device, args.filename)

        elif args.command == "wifi":
            device = select_device(devices)
            if device is None:
                return
            wifi(device)

        elif args.command == "search":
            device = select_device(devices)
            if device is None:
                return
            search(device, args.search_term)

        elif args.command == "r":
            device = select_device(devices)
            if device is None:
                return
            cmd = ["adb", "-s", device] + args.args
            subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
