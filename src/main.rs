mod device;
mod commands;

use clap::{Parser, Subcommand};
use anyhow::{Result, Context};
use device::{get_devices, select_device, DeviceSelection};
use commands::*;

#[derive(Parser)]
#[command(name = "sadb")]
#[command(about = "A wrapper for adb on multiple devices")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Stop a package on all or a single device
    Stop { package_name: String },
    /// Start a package on all or a single device
    Start { package_name: String },
    /// Clear a package's storage on all or a single device
    Clear { package_name: String },
    /// Install an APK on all or a single device
    Install { apk: String },
    /// Uninstall a package on all or a single device
    Uninstall { package_name: String },
    /// Start scrcpy on a device
    Scrcpy,
    /// Get the selected device's IP address
    Ip,
    /// Take a screenshot of a device
    Screenshot {
        #[arg(short, long, default_value = "screenshot.png")]
        filename: String,
    },
    /// Record the screen of a device (Press CTRL-C to stop recording)
    Record {
        #[arg(short, long, default_value = "video.mp4")]
        filename: String,
    },
    /// Connect to a device via WiFi
    Wifi,
    /// Search for an installed package on a device
    Search { search_term: String },
    /// Run an adb command on a device
    R { args: Vec<String> },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let devices = get_devices().context("Failed to get connected devices")?;

    match cli.command {
        Commands::Stop { package_name } => {
            if let Some(selection) = select_device(&devices, true)? {
                stop_package(selection, &package_name)?;
            }
        }
        Commands::Start { package_name } => {
            if let Some(selection) = select_device(&devices, true)? {
                start_package(selection, &package_name)?;
            }
        }
        Commands::Clear { package_name } => {
            if let Some(selection) = select_device(&devices, true)? {
                clear_package(selection, &package_name)?;
            }
        }
        Commands::Install { apk } => {
            if let Some(selection) = select_device(&devices, true)? {
                install_apk(selection, &apk)?;
            }
        }
        Commands::Uninstall { package_name } => {
            if let Some(selection) = select_device(&devices, true)? {
                uninstall_package(selection, &package_name)?;
            }
        }
        Commands::Scrcpy => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                run_scrcpy(&device)?;
            }
        }
        Commands::Ip => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                get_device_ip(&device)?;
            }
        }
        Commands::Screenshot { filename } => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                take_screenshot(&device, &filename)?;
            }
        }
        Commands::Record { filename } => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                record_screen(&device, &filename)?;
            }
        }
        Commands::Wifi => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                connect_wifi(&device)?;
            }
        }
        Commands::Search { search_term } => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                search_packages(&device, &search_term)?;
            }
        }
        Commands::R { args } => {
            if let Some(DeviceSelection::Single(device)) = select_device(&devices, false)? {
                run_raw_command(&device, &args)?;
            }
        }
    }

    Ok(())
}
