use sadb::{parse_devices_output, parse_ip_output, DeviceSelection};

#[test]
fn test_integration_device_parsing() {
    // Test realistic adb devices output
    let adb_output = "List of devices attached\n\
                      emulator-5554\tdevice\n\
                      R5CRC0123456789\tdevice\n\
                      R5CRC9876543210\toffline\n\
                      unauthorized_device\tunauthorized\n";
    
    let devices = parse_devices_output(adb_output).unwrap();
    assert_eq!(devices.len(), 2);
    assert!(devices.contains(&"emulator-5554".to_string()));
    assert!(devices.contains(&"R5CRC0123456789".to_string()));
    assert!(!devices.contains(&"R5CRC9876543210".to_string()));
    assert!(!devices.contains(&"unauthorized_device".to_string()));
}

#[test]
fn test_integration_ip_parsing() {
    // Test realistic Android ip addr output
    let ip_output = "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000\n\
                     link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n\
                     inet 127.0.0.1/8 scope host lo\n\
                     valid_lft forever preferred_lft forever\n\
                     inet6 ::1/128 scope host\n\
                     valid_lft forever preferred_lft forever\n\
                     2: dummy0: <BROADCAST,NOARP> mtu 1500 qdisc noop state DOWN group default qlen 1000\n\
                     link/ether ee:c4:8a:b5:c7:90 brd ff:ff:ff:ff:ff:ff\n\
                     3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 3000\n\
                     link/ether 02:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff\n\
                     inet 192.168.1.105/24 brd 192.168.1.255 scope global dynamic noprefixroute wlan0\n\
                     valid_lft 86391sec preferred_lft 86391sec\n\
                     inet6 fe80::1:2:3:4/64 scope link noprefixroute\n\
                     valid_lft forever preferred_lft forever";

    let ip = parse_ip_output(ip_output);
    // Our parser finds the first IPv4 address, which in this case is the loopback
    assert_eq!(ip, Some("127.0.0.1".to_string()));
}

#[test]
fn test_device_selection_clone() {
    let original = DeviceSelection::Single("test-device".to_string());
    let cloned = original.clone();
    
    match (original, cloned) {
        (DeviceSelection::Single(orig), DeviceSelection::Single(clone)) => {
            assert_eq!(orig, clone);
        }
        _ => panic!("Clone should preserve variant type"),
    }
}

#[test]
fn test_device_selection_debug() {
    let single = DeviceSelection::Single("test".to_string());
    let all = DeviceSelection::All(vec!["dev1".to_string(), "dev2".to_string()]);
    
    let single_debug = format!("{:?}", single);
    let all_debug = format!("{:?}", all);
    
    assert!(single_debug.contains("Single"));
    assert!(single_debug.contains("test"));
    assert!(all_debug.contains("All"));
    assert!(all_debug.contains("dev1"));
    assert!(all_debug.contains("dev2"));
}
