#!/bin/bash


# Created by:   Seamus Sloan
# Last edited:  October 13, 2022


# Get all connected device names
DEVICES=($(adb devices | sed '1d' | sed '$d' | sed 's/\t.*//'))
ADBWIFIPORT=5555
USERSELECTION=""





#region Install APK
function install() {
    selectDevice true

    # Install the apk on the device (or devices)
    if [[ ${#USERSELECTION[@]} > 1 ]]
    then
        for device in "${USERSELECTION[@]}"
        do
            install_on_device ${device} ${apk}
        done
    else
        device=${USERSELECTION}
        install_on_device ${device} ${apk}
    fi
}

function install_on_device() {
    printf "\nInstalling ${apk} on ${device}...\n"
    installation_command=$(adb -s ${device} install ${apk})
}
#endregion





#region Uninstall APK
function uninstall() {
    selectDevice

    # Uninstall the package on the device (or devices)
    if [[ ${#USERSELECTION[@]} > 1 ]]
    then
        for device in "${USERSELECTION[@]}"
        do
            uninstall_on_device ${device} ${package}
        done
    else
        device=${USERSELECTION}
        uninstall_on_device ${device} ${package}
    fi
}

function uninstall_on_device() {
    printf "\nUninstalling ${package} on ${device}...\n"
    uninstallation_command=$(adb -s ${device} uninstall ${package})
}
#endregion





#region Stop Package
function stop() {
    selectDevice

    # Install the apk on the device (or devices)
    if [[ ${#USERSELECTION[@]} > 1 ]]
    then
        for device in "${USERSELECTION[@]}"
        do
            stopPackage ${device} ${package}
        done
    else
        device=${USERSELECTION}
        stopPackage ${device} ${package}
    fi
}

function stopPackage() {
    printf "\nStopping ${package} on ${device}...\n"
    stop_package_command=$(adb -s ${device} shell am force-stop ${package})

}
#endregion





#region Start Package
function start() {
    selectDevice

    # Install the apk on the device (or devices)
    if [[ ${#USERSELECTION[@]} > 1 ]]
    then
        for device in "${USERSELECTION[@]}"
        do
            startPackage ${device} ${package}
        done
    else
        device=${USERSELECTION}
        startPackage ${device} ${package}
    fi
}

function startPackage() {
    printf "\nStarting ${package} on ${device}...\n"
    stop_package_command=$(adb -s ${device} shell monkey -p ${package} -c android.intent.category.LAUNCHER 1)

}
#endregion





#region ADB over WiFi
function adbwifi() {
    # Start in TCPIP
    startTcpip
    sleep 5

    # Select the device to connect over WiFi
    selectDevice true

    # Get the IP Address of the device
    device=${USERSELECTION}
    getDeviceIp ${device}

    # Connect to the device
    connectToDevice ${deviceIp}
}

function startTcpip() {
    adb tcpip ${ADBWIFIPORT}
}

function getDeviceIp() {
  deviceIp=$(adb -s ${device} shell ip addr show wlan0 | grep 'inet ' | sed -e "s/inet //" | awk -F/ '{print $1}' | tr -d "[:space:]")
  echo Your device is IP: $deviceIp $'\n'
}

function connectToDevice() {
    adb connect ${deviceIp}:${ADBWIFIPORT}
}
#endregion





function record() {
    selectDevice
    printf "Screenrecording on ${USERSELECTION}... (Ctrl + C to stop)\n"
    trap record_pull INT
    record_command=$(adb -s ${USERSELECTION} shell screenrecord sdcard/video.mp4)
}





function record_pull() {
    printf '\n'
    read -p "Download the screenrecording to the current directory? (y\n): " selection
    if [[ ${selection} == "y" ]]
    then
        printf "\nDownloading screen recording from ${USERSELECTION}...\n"
        record_pull_command=$(adb -s ${USERSELECTION} pull sdcard/video.mp4)
    fi
}





function screenshot() {
    selectDevice
    printf "Screenshotting on ${USERSELECTION}\n"
    screenshot_command=$(adb -s ${USERSELECTION} exec-out screencap -p > screenshot.png)
}





function screencopy() {
    selectDevice
    printf "Running scrcpy on ${USERSELECTION}\n"
    command=$(scrcpy -s ${USERSELECTION})
}





function devices() {
    adb devices
}





function selectDevice(){
    # If the user only has one device connected
    if [[ ${#DEVICES[@]} == 1 ]]
    then
        USERSELECTION=${DEVICES[0]}
    else
        # List all available devices
        printf "Select a device:\n"
        count=0
        for device in "${DEVICES[@]}"
        do
            printf "  [${count}] - ${device}\n"
            ((count++))
        done

        # If the user is performing an action that can be
        # done on multiple devices (install/uninstall)
        if [[ -n ${ALLOPTION} ]]
        then
            printf "  [${count}] - ALL DEVICES\n"
        else
            ((count--))
        fi

        printf '\n'
        read -p "Device [0 - $count]: " selection

        # Save user's selection
        if [[ ${selection} == ${count} && -n ${ALLOPTION} ]]
        then
            USERSELECTION=(${DEVICES[@]})
        else
            USERSELECTION=${DEVICES[${selection}]}
        fi
    fi
}





function help(){
    version

    printf 'Options:\n'
    printf ' -h|-help|--h|--help\n'
    printf ' -version|--version\n'
    printf '\n'

    printf 'Functions:\n'
    printf ' sadb devices\n'
    printf ' sadb install [YOUR_APK.apk]\n'
    printf ' sadb uninstall [YOUR.PACKAGE.NAME]\n'
    printf ' sadb record\n'
    printf ' sadb record [VIDEO_NAME].mp4\n'
    printf ' sadb screenshot\n'
    printf ' sadb screenshot [IMAGE_NAME].png\n'
    printf ' sadb scrcpy\n'
    printf ' sadb stop [YOUR.PACKAGE.NAME]\n'
    printf ' sadb start [YOUR.PACKAGE.NAME]\n'
    printf ' sadb wifi\n'
    printf '\n'
}





function version(){
    printf '\nSADB Version 1.1.0'
    printf '\n'
}





#=============================================#
#=============================================#
#=============================================#
#==============     MAIN     =================#
#=============================================#
#=============================================#

while getopts ":hv:" option; do
    case ${option} in
        h)
            help
            exit;;
        v)
            version
            exit;;
    esac
done


case $1 in
    devices)
        devices;;

    wifi)
        ALLOPTION=false
        adbwifi;;

    install)
        if [[ $# != 2 ]]
        then
            printf '`install` requires an APK to be specified.\n'
            help
        else
            ALLOPTION=true
            apk=$2
            install $apk
        fi;;

    uninstall)
        if [[ $# != 2 ]]
        then
            printf '`uninstall` requires a package to be specified.\n'
            help
        else
            ALLOPTION=true
            package=$2
            uninstall $package
        fi;;

    stop)
        if [[ $# != 2 ]]
        then
            printf '`stop` requires a package to be specified.\n'
            help
        else
            ALLOPTION=true
            package=$2
            stop $package
        fi;;

    start)
        if [[ $# != 2 ]]
        then
            printf '`stop` requires a package to be specified.\n'
            help
        else
            ALLOPTION=true
            package=$2
            start $package
        fi;;

    record)
        record
        if [[ $# == 2 ]]
        then
            mv -v video.mp4 $2
        fi;;

    screenshot)
        screenshot
        if [[ $# == 2 ]]
        then
            mv -v screenshot.png $2
        fi;;

    scrcpy)
        screencopy
        exit;;

    *)
        help;;

esac
