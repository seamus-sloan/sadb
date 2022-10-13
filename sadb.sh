#!/bin/bash


# Created by:   Seamus Sloan
# Last edited:  April 6, 2022


# Usage:
# sadb install your_app.apk
# sadb display
# sadb uninstall your.package.name
# sadb screenshot
# sadb scrcpy


# Get all connected device names
DEVICES=($(adb devices | sed '1d' | sed '$d' | sed 's/\t.*//'))
USERSELECTION=""


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
    printf "Uninstalling ${package} on ${device}...\n"
    uninstallation_command=$(adb -s ${device} uninstall ${package})
}


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
    printf '\t Display help and usage\n'
    printf ' -version|--version\n'
    printf '\t Display version number\n'
    printf '\n'

    printf 'Functions:\n'
    printf ' sadb install [YOUR_APK.apk]\n'
    printf '\t Install a specified apk onto a selected device\n'
    printf ' sadb uninstall [YOUR.PACKAGE.NAME]\n'
    printf '\t Uninstall a specified package from a selected device\n'
    printf ' sadb record\n'
    printf ' sadb record [VIDEO_NAME].mp4\n'
    printf '\t Record the screen on the selected device\n'
    printf ' sadb screenshot\n'
    printf ' sadb screenshot [IMAGE_NAME].png\n'
    printf '\t Capture a screenshotfrom a selected device\n'
    printf ' sadb scrcpy\n'
    printf '\t Launch scrcpy on a selected device\n'
    printf '\n'
}


function version(){
    printf '\nSADB Version 1.0.0'
    printf '\n'
}







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
