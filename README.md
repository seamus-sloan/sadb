<img src="https://github.com/seamus-sloan/sadb/assets/49955196/e03b59ce-18a6-467d-9445-b3b5a79f2389" alt="sadb banner">

# Introducing a better way to control your devices
`sadb` is a wrapper on [`adb`](https://developer.android.com/studio/releases/platform-tools) that allows you to easily do the things you do most with `adb` -- and on multiple devices! 

Whether you're running `adb install com.example.app` over and over again on multiple different connected devices or if you're just too lazy to type in `adb shell pm packages list | grep some.package.name`, `sadb` makes those commands runnable on multiple devices and defines some "aliases" to make those commands easier for you.

- Can't remember how to see your device's IP address and don't want to go through wifi settings? 
  - `sadb ip`
- Trying to connect over wifi but you can't remember the commands? 
  - `sadb wifi`
- Installing the same APK on 4 different devices? 
  - `sadb install your.apk` then select `ALL`
- ... **_The list goes on and on!_**


# What do I need to use this?
- [`Rust`](https://www.rust-lang.org/tools/install) (for building from source)
- [`adb`](https://developer.android.com/studio/releases/platform-tools)
  - If you don't have [adb installed with Android Studio](https://developer.android.com/studio), then you can always download [the platform tools as a standalone](https://developer.android.com/studio/releases/platform-tools). 
- [`scrcpy`](https://github.com/Genymobile/scrcpy)
  - You don't need to have this, but there is a command for `scrcpy` that you'll be unable to use without it.

# How do I use it?
The main idea behind `sadb` is to allow you to run `adb` commands on multiple devices. That's why before each command is executed, you're forced to select which device(s) you'd like to run the command on. 

```
sadb stop com.example.app 
    - Stop a package on all or a single device
sadb start com.example.app 
    - Start a package on all or a single device
sadb clear com.example.app 
    - Clear a package's storage on all or a single device
sadb install path/to/myApp.apk 
    - Install an APK on all or a single device
sadb uninstall com.example.app 
    - Uninstall a package on all or a single device
sadb scrcpy 
    - Start scrcpy on a device
sadb ip 
    - Get the selected device's IP address
sadb screenshot -f myScreenshot.png 
    - Take a screenshot of a device
sadb record -f myVideo.mp4 
    - Record the screen of a device (Press CTRL-C to stop recording)
sadb wifi 
    - Connect to a device via WiFi
sadb search packageName 
    - Search for an installed package on a device
sadb r [ANY ADB COMMAND] 
    - Run an adb command on a device
```

# Building and Installing

## Building from source
```bash
git clone https://github.com/seamus-sloan/sadb.git
cd sadb
cargo build --release
```

The binary will be available at `target/release/sadb`.

## Installation Options

### Option 1: Copy to PATH
```bash
# Copy the binary to a location in your PATH
sudo cp target/release/sadb /usr/local/bin/
```

### Option 2: Create an alias
Add this to your shell profile (e.g., `~/.zshrc`, `~/.bash_profile`):
```bash
alias sadb='/path/to/your/sadb/target/release/sadb'
```

### Option 3: Add to PATH
Add the binary location to your PATH:
```bash
export PATH="/path/to/your/sadb/target/release:$PATH"
```
