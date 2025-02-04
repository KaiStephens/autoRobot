import subprocess
import serial
import time
import os

mac_address = "cc-db-a7-9f-5a-fa"  
bluetooth_port = "/dev/tty.ESP32_Bluetooth_Motor_C" 
baud_rate = 115200

def wait_for_device_ready(port, timeout=5):
    """Check if the device node for the serial port exists within a given timeout."""
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        if os.path.exists(port):
            print(f"Found port: {port}")
            return True
        time.sleep(0.2)
    return False

def connect_via_bluetooth():
    """Connects to the ESP32 device over Bluetooth and returns an open serial connection."""
    print(f"Unpairing (forgetting) {mac_address} via blueutil...")
    forget_result = subprocess.run(
        ["blueutil", "--unpair", mac_address],
        capture_output=True,
        text=True
    )
    print("Unpair output:", forget_result.stdout, forget_result.stderr)

    print(f"Pairing with {mac_address} via blueutil...")
    pair_result = subprocess.run(
        ["blueutil", "--pair", mac_address],
        capture_output=True,
        text=True
    )
    print("Pair output:", pair_result.stdout, pair_result.stderr)

    print(f"Connecting to {mac_address} via blueutil...")
    connect_result = subprocess.run(
        ["blueutil", "--connect", mac_address],
        capture_output=True,
        text=True
    )
    print("Connect output:", connect_result.stdout, connect_result.stderr)

    # Give the system a moment to create the serial device
    time.sleep(0)

    if not wait_for_device_ready(bluetooth_port, timeout=10):
        print("ERROR: The serial device never became available. Exiting...")
        return None

    try:
        print(f"Opening serial connection on {bluetooth_port} at {baud_rate} baud...")
        esp32_connection = serial.Serial(bluetooth_port, baud_rate)
        print(f"Successfully connected to {bluetooth_port}")
        return esp32_connection
    except Exception as e:
        print(f"ERROR: Failed to open {bluetooth_port}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    connection = connect_via_bluetooth()
    if connection:
        connection.close()
