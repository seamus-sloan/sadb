# Created by:   Seamus Sloan
# Last edited:  June 15, 2023

import argparse
import sys
import subprocess

COMMANDS = {
    "stop": 1,
    "start": 1,
}


def get_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    devices = [line.split()[0] for line in lines]
    return devices


def select_device(devices):
    if len(devices) == 0:
        print("No devices found")
        return None
    if len(devices) == 1:
        return devices[0]
    print("Select a device:")
    for i, device in enumerate(devices):
        print(f"[{i + 1}]: {device}")
    while True:
        choice = input("Enter the number of the device: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(devices):
                return devices[index]
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
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="A wrapper for adb commands")
    subparsers = parser.add_subparsers(dest="command")

    stop_parser = subparsers.add_parser("stop", help="Stop a package")
    stop_parser.add_argument(
        "package_name", help="The name of the package to stop")

    start_parser = subparsers.add_parser("start", help="Start a package")
    start_parser.add_argument(
        "package_name", help="The name of the package to start")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    devices = get_devices()
    device = select_device(devices)

    if device is None:
        return

    if args.command == "stop":
        stop(device, args.package_name)
    elif args.command == "start":
        start(device, args.package_name)


if __name__ == "__main__":
    main()
