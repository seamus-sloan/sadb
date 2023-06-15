# Multi-Device ADB Helper (sadb)

`sadb` alleviates some of the pains of testing and developing on multiple physical and emulated devices by providing a handful of common `adb` commands for the user to use on a selected device.

## Dependencies
- [Screencopy](https://github.com/Genymobile/scrcpy) (`scrcpy`)
- Android Debug Bridge (`adb`)
  - *Comes pre-packaged with [Android Studio](https://developer.android.com/studio) or can be downloaded as a [standalone](https://developer.android.com/studio/releases/platform-tools)*
- [Python 3.7+](https://www.python.org/downloads/)



## Usage
- `sadb wifi` - Switch selected connected device to be connected over wifi
- `sadb ip` - Get the IP Address of the selected device
- `sadb install [YOUR_APK.apk]` - Install APK on one or all devices
- `sadb uninstall [YOUR.PACKAGE.NAME]` - Uninstall the package on one or all devices
- `sadb stop [YOUR.PACKAGE.NAME]` - Stop the specified package on one or all devices
- `sadb start [YOUR.PACKAGE.NAME]` - Start the specified package on one or all devices
- `sadb clear [YOUR.PACKAGE.NAME]` - Clear the storage of the specified package on one or all devices
- `sadb record [VIDEO_NAME.mp4]` - Record on one device and save to current directory
  - *Video file is named `video.mp4` if no video name is specified.*
- `sadb screenshot [IMAGE_NAME.png]` - Screenshot on one device and save to current directory
  - *Screenshot file is named `screenshot.png` if no name is specified.*
- `sadb scrcpy` - Start `scrcpy` on a selected device
- `sadb search [GREP_SEARCH_TERM]` - Search all device's packages for the search term
- `sadb r [ADB_COMMANDS]` - Run a normal ADB command on a selected device
  - *For example, you can run `sadb r devices` to execute `adb devices`*
  - *Another great example is running `sadb r shell "pm list packages | grep dji"` to search for dji packages* 


## Add to your terminal profile
```
...
alias sadb='python3 ~/Scripts/sadb/sadb.py'
...
```