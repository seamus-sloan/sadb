use anyhow::{Context, Result};
use dialoguer::{theme::ColorfulTheme, Select};
use std::process::Command;

#[derive(Debug, Clone)]
pub enum DeviceSelection {
    Single(String),
    All(Vec<String>),
}

pub fn get_devices() -> Result<Vec<String>> {
    let output = Command::new("adb")
        .arg("devices")
        .output()
        .context("Failed to execute adb devices command")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!("adb devices command failed"));
    }

    let stdout = String::from_utf8(output.stdout).context("Failed to parse adb devices output")?;

    parse_devices_output(&stdout)
}

pub fn parse_devices_output(output: &str) -> Result<Vec<String>> {
    let devices: Vec<String> = output
        .lines()
        .skip(1) // Skip the "List of devices attached" header
        .filter_map(|line| {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 2 && parts[1] == "device" {
                Some(parts[0].to_string())
            } else {
                None
            }
        })
        .collect();

    Ok(devices)
}

pub fn select_device(devices: &[String], allow_all: bool) -> Result<Option<DeviceSelection>> {
    if devices.is_empty() {
        println!("No devices found");
        return Ok(None);
    }

    if devices.len() == 1 {
        return Ok(Some(DeviceSelection::Single(devices[0].clone())));
    }

    let mut options: Vec<String> = devices.to_vec();
    if allow_all {
        options.push("ALL".to_string());
    }

    let selection = Select::with_theme(&ColorfulTheme::default())
        .with_prompt("Select a device:")
        .items(&options)
        .default(0)
        .interact()
        .context("Failed to get device selection")?;

    if allow_all && selection == devices.len() {
        Ok(Some(DeviceSelection::All(devices.to_vec())))
    } else {
        Ok(Some(DeviceSelection::Single(devices[selection].clone())))
    }
}

pub fn execute_command_on_device(device: &str, cmd_args: &[&str]) -> Result<()> {
    let mut cmd = Command::new("adb");
    cmd.args(["-s", device]).args(cmd_args);

    let status = cmd.status().context("Failed to execute adb command")?;

    if !status.success() {
        eprintln!("Command failed on device {}", device);
    }

    Ok(())
}

pub fn execute_command_on_devices(selection: DeviceSelection, cmd_args: &[&str]) -> Result<()> {
    match selection {
        DeviceSelection::Single(device) => {
            execute_command_on_device(&device, cmd_args)?;
        }
        DeviceSelection::All(devices) => {
            for device in devices {
                execute_command_on_device(&device, cmd_args)?;
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_devices_output_empty() {
        let output = "List of devices attached\n";
        let devices = parse_devices_output(output).unwrap();
        assert_eq!(devices.len(), 0);
    }

    #[test]
    fn test_parse_devices_output_single_device() {
        let output = "List of devices attached\nemulator-5554\tdevice\n";
        let devices = parse_devices_output(output).unwrap();
        assert_eq!(devices.len(), 1);
        assert_eq!(devices[0], "emulator-5554");
    }

    #[test]
    fn test_parse_devices_output_multiple_devices() {
        let output = "List of devices attached\n\
                      emulator-5554\tdevice\n\
                      R5CRC123456\tdevice\n\
                      R5CRC789012\toffline\n";
        let devices = parse_devices_output(output).unwrap();
        assert_eq!(devices.len(), 2); // offline devices should be excluded
        assert_eq!(devices[0], "emulator-5554");
        assert_eq!(devices[1], "R5CRC123456");
    }

    #[test]
    fn test_parse_devices_output_with_unauthorized() {
        let output = "List of devices attached\n\
                      emulator-5554\tdevice\n\
                      R5CRC123456\tunauthorized\n";
        let devices = parse_devices_output(output).unwrap();
        assert_eq!(devices.len(), 1); // unauthorized devices should be excluded
        assert_eq!(devices[0], "emulator-5554");
    }

    #[test]
    fn test_device_selection_enum() {
        let single = DeviceSelection::Single("device1".to_string());
        let all = DeviceSelection::All(vec!["device1".to_string(), "device2".to_string()]);

        match single {
            DeviceSelection::Single(device) => assert_eq!(device, "device1"),
            _ => panic!("Expected Single variant"),
        }

        match all {
            DeviceSelection::All(devices) => {
                assert_eq!(devices.len(), 2);
                assert_eq!(devices[0], "device1");
                assert_eq!(devices[1], "device2");
            }
            _ => panic!("Expected All variant"),
        }
    }
}
