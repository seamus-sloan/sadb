# Multi-Device ADB Helper (sadb)

`sadb` alleviates some of the pains of testing and developing on multiple physical and emulated devices by providing a handful of common `adb` commands for the user to use on a selected device.

## Dependencies
- [Screencopy](https://github.com/Genymobile/scrcpy) (`scrcpy`)
- Android Debug Bridge (`adb`)
  - *Comes pre-packaged with [Android Studio](https://developer.android.com/studio) or can be downloaded as a [standalone](https://developer.android.com/studio/releases/platform-tools)*



## Usage
- `sadb devices` - List all connected devices (`adb devices`)
- `sadb wifi` - Switch selected connected device to be connected over wifi
- `sadb install [YOUR_APK.apk]` - Install APK on one or all devices
- `sadb uninstall [YOUR.PACKAGE.NAME]` - Uninstall the package on one or all devices
- `sadb stop [YOUR.PACKAGE.NAME]` - Stop the specified package on one or all devices
- `sadb start [YOUR.PACKAGE.NAME]` - Start the specified package on one or all devices
- `sadb record [VIDEO_NAME.mp4]` - Record on one device and save to current directory
  - *Video file is named `video.mp4` if no video name is specified.*
- `sadb screenshot [IMAGE_NAME.png]` - Screenshot on one device and save to current directory
  - *Screenshot file is named `screenshot.png` if no name is specified.*
- `sadb scrcpy` - Start `scrcpy` on a selected device
- `sadb pull [PATH_TO_FILE] [NAME]` - Pull specified file to current directory
  - *File name is left alone if no name is specified.*

## Add to your bash profile
```
...
alias sadb='sh ~/Scripts/sadb/sadb.sh'
...
```