use crate::device::{execute_command_on_devices, DeviceSelection};
use anyhow::{Context, Result};
use std::io::{self, Write};
use std::process::Command;

pub fn stop_package(selection: DeviceSelection, package_name: &str) -> Result<()> {
    let cmd_args = &["shell", "am", "force-stop", package_name];
    execute_command_on_devices(selection, cmd_args)
}

pub fn start_package(selection: DeviceSelection, package_name: &str) -> Result<()> {
    let cmd_args = &[
        "shell",
        "monkey",
        "-p",
        package_name,
        "-c",
        "android.intent.category.LAUNCHER",
        "1",
    ];
    execute_command_on_devices(selection, cmd_args)
}

pub fn clear_package(selection: DeviceSelection, package_name: &str) -> Result<()> {
    let cmd_args = &["shell", "pm", "clear", package_name];
    execute_command_on_devices(selection, cmd_args)
}

pub fn install_apk(selection: DeviceSelection, apk_path: &str) -> Result<()> {
    let cmd_args = &["install", apk_path];
    execute_command_on_devices(selection, cmd_args)
}

pub fn uninstall_package(selection: DeviceSelection, package_name: &str) -> Result<()> {
    let cmd_args = &["uninstall", package_name];
    execute_command_on_devices(selection, cmd_args)
}

pub fn run_scrcpy(device: &str) -> Result<()> {
    let status = Command::new("scrcpy")
        .args(["-s", device])
        .status()
        .context("Failed to execute scrcpy command")?;

    if !status.success() {
        eprintln!("scrcpy command failed");
    }

    Ok(())
}

pub fn parse_ip_output(output: &str) -> Option<String> {
    for line in output.lines() {
        if line.contains("inet") && !line.contains("inet6") {
            if let Some(ip_part) = line.split_whitespace().nth(1) {
                if let Some(ip) = ip_part.split('/').next() {
                    return Some(ip.to_string());
                }
            }
        }
    }
    None
}

pub fn get_device_ip(device: &str) -> Result<()> {
    let output = Command::new("adb")
        .args(["-s", device, "shell", "ip", "addr", "show", "wlan0"])
        .output()
        .context("Failed to get device IP address")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!(
            "Failed to get IP address for device {}",
            device
        ));
    }

    let stdout = String::from_utf8(output.stdout).context("Failed to parse IP address output")?;

    if let Some(ip) = parse_ip_output(&stdout) {
        println!("{}'s IP address is:\t {}", device, ip);
    } else {
        println!("Could not find IP address for device {}", device);
    }

    Ok(())
}

pub fn take_screenshot(device: &str, filename: &str) -> Result<()> {
    let output = Command::new("adb")
        .args(["-s", device, "exec-out", "screencap", "-p"])
        .output()
        .context("Failed to take screenshot")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!("Screenshot command failed"));
    }

    std::fs::write(filename, output.stdout).context("Failed to save screenshot")?;

    println!("Screenshot saved to {}", filename);
    Ok(())
}

pub fn record_screen(device: &str, filename: &str) -> Result<()> {
    let remote_path = format!("/data/local/tmp/{}", filename);

    println!("Recording... Press CTRL-C to stop.");

    let mut child = Command::new("adb")
        .args([
            "-s",
            device,
            "shell",
            &format!("screenrecord {}", remote_path),
        ])
        .spawn()
        .context("Failed to start screen recording")?;

    // Wait for user interrupt
    let _ = ctrlc::set_handler(move || {
        // The child process will be terminated when this process exits
    });

    child
        .wait()
        .context("Failed to wait for recording process")?;

    println!("\nWaiting for recording to save to device...\n");
    std::thread::sleep(std::time::Duration::from_secs(5));

    // Pull the file from device
    let status = Command::new("adb")
        .args(["-s", device, "pull", &remote_path, filename])
        .status()
        .context("Failed to pull recording from device")?;

    if status.success() {
        println!(
            "Success! Screen recording saved to {}/{}",
            std::env::current_dir()?.display(),
            filename
        );

        print!("\nDelete video from device? (Y/n): ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        if input.trim().to_lowercase() == "y" || input.trim().is_empty() {
            let _ = Command::new("adb")
                .args(["-s", device, "shell", "rm", &remote_path])
                .status();
        }
    }

    Ok(())
}

pub fn connect_wifi(device: &str) -> Result<()> {
    // First get the IP address
    let output = Command::new("adb")
        .args(["-s", device, "shell", "ip", "addr", "show", "wlan0"])
        .output()
        .context("Failed to get device IP address")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!(
            "Failed to get IP address for device {}",
            device
        ));
    }

    let stdout = String::from_utf8(output.stdout).context("Failed to parse IP address output")?;

    let ip = parse_ip_output(&stdout)
        .ok_or_else(|| anyhow::anyhow!("Could not get IP address of device"))?;

    // Enable tcpip mode
    Command::new("adb")
        .args(["-s", device, "tcpip", "5555"])
        .status()
        .context("Failed to enable tcpip mode")?;

    // Connect via WiFi
    let status = Command::new("adb")
        .args(["connect", &format!("{}:5555", ip)])
        .status()
        .context("Failed to connect via WiFi")?;

    if status.success() {
        println!("Connected to {} via WiFi", device);
    }

    Ok(())
}

pub fn search_packages(device: &str, search_term: &str) -> Result<()> {
    let output = Command::new("adb")
        .args(["-s", device, "shell", "pm", "list", "packages"])
        .output()
        .context("Failed to list packages")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!("Failed to list packages"));
    }

    let stdout = String::from_utf8(output.stdout).context("Failed to parse package list")?;

    for line in stdout.lines() {
        if line.contains(search_term) {
            println!("{}", line);
        }
    }

    Ok(())
}

pub fn run_raw_command(device: &str, args: &[String]) -> Result<()> {
    let mut cmd = Command::new("adb");
    cmd.args(["-s", device]).args(args);

    let status = cmd.status().context("Failed to execute raw adb command")?;

    if !status.success() {
        eprintln!("Command failed");
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_ip_output_valid() {
        let output = "3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 3000\n\
                     link/ether 12:34:56:78:9a:bc brd ff:ff:ff:ff:ff:ff\n\
                     inet 192.168.1.100/24 brd 192.168.1.255 scope global dynamic noprefixroute wlan0\n\
                     valid_lft 86395sec preferred_lft 86395sec\n\
                     inet6 fe80::1034:5678:9abc:def0/64 scope link noprefixroute\n\
                     valid_lft forever preferred_lft forever";

        let ip = parse_ip_output(output);
        assert_eq!(ip, Some("192.168.1.100".to_string()));
    }

    #[test]
    fn test_parse_ip_output_no_inet() {
        let output = "3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 3000\n\
                     link/ether 12:34:56:78:9a:bc brd ff:ff:ff:ff:ff:ff";

        let ip = parse_ip_output(output);
        assert_eq!(ip, None);
    }

    #[test]
    fn test_parse_ip_output_only_inet6() {
        let output = "3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 3000\n\
                     link/ether 12:34:56:78:9a:bc brd ff:ff:ff:ff:ff:ff\n\
                     inet6 fe80::1034:5678:9abc:def0/64 scope link noprefixroute\n\
                     valid_lft forever preferred_lft forever";

        let ip = parse_ip_output(output);
        assert_eq!(ip, None);
    }

    #[test]
    fn test_device_selection_variants() {
        let single_device = DeviceSelection::Single("test-device".to_string());
        let multiple_devices =
            DeviceSelection::All(vec!["device1".to_string(), "device2".to_string()]);

        // Test that we can match on the variants
        match single_device {
            DeviceSelection::Single(device) => assert_eq!(device, "test-device"),
            DeviceSelection::All(_) => panic!("Expected Single variant"),
        }

        match multiple_devices {
            DeviceSelection::Single(_) => panic!("Expected All variant"),
            DeviceSelection::All(devices) => {
                assert_eq!(devices.len(), 2);
                assert!(devices.contains(&"device1".to_string()));
                assert!(devices.contains(&"device2".to_string()));
            }
        }
    }
}
