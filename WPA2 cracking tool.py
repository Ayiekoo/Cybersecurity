#!/usr/bin/env python3
"""
Educational WiFi Security Testing Tool
Demonstrates WPA/WPA2 handshake capture and cracking
FOR AUTHORIZED TESTING AND EDUCATION ONLY
"""

import hashlib
import hmac
import binascii
import os
from typing import Optional

# =============================================================================
# WPA/WPA2 CRACKING DEMONSTRATION
# =============================================================================

class WiFiCracker:
    """
    Educational implementation of WPA/WPA2 PSK cracking
    Demonstrates how dictionary attacks against handshakes work
    """
    
    def __init__(self):
        self.target_ssid = None
        self.handshake_captured = False
        self.anonce = None  # Authenticator nonce
        self.snonce = None  # Supplicant nonce
        self.mac_ap = None
        self.mac_client = None
        
    def simulate_handshake_capture(self, ssid: str, password: str):
        """
        Simulate capturing a WPA 4-way handshake
        In real scenario, this uses airodump-ng + aireplay-ng
        """
        print(f"\n[+] Targeting network: {ssid}")
        print("[*] Setting wireless interface to monitor mode...")
        print("[*] Scanning for target BSSID...")
        
        # Simulate the handshake values
        self.target_ssid = ssid
        self.anonce = os.urandom(32)  # 256-bit nonce
        self.snonce = os.urandom(32)
        self.mac_ap = bytes.fromhex("001122334455")
        self.mac_client = bytes.fromhex("00aabbccddee")
        
        # Generate the actual PMK and PTK (what we'd capture in real handshake)
        self.real_pmk = self._calculate_pmk(ssid, password)
        self.real_ptk = self._calculate_ptk(self.real_pmk)
        
        print(f"[+] Captured handshake for {ssid}")
        print(f"    MAC_AP: {self.mac_ap.hex()}")
        print(f"    MAC_Client: {self.mac_client.hex()}")
        print(f"    Anonce: {self.anonce.hex()[:16]}...")
        self.handshake_captured = True
        
    def _calculate_pmk(self, ssid: str, password: str) -> bytes:
        """
        Calculate Pairwise Master Key using PBKDF2
        PMK = PBKDF2-SHA1(password, ssid, 4096 iterations, 256 bits)
        """
        pmk = hashlib.pbkdf2_hmac('sha1', 
                                   password.encode('utf-8'), 
                                   ssid.encode('utf-8'), 
                                   4096, 
                                   32)
        return pmk
    
    def _calculate_ptk(self, pmk: bytes) -> bytes:
        """
        Calculate Pairwise Transient Key
        PTK = PRF-512(PMK, "Pairwise key expansion", 
                       Min(AA,SA) || Max(AA,SA) || Min(ANonce,SNonce) || Max(ANonce,SNonce))
        """
        # Simplified PTK calculation for demonstration
        data = b"Pairwise key expansion" + self.mac_ap + self.mac_client + self.anonce + self.snonce
        ptk = hmac.new(pmk, data, hashlib.sha1).digest()[:32]
        return ptk
    
    def _verify_mic(self, password: str) -> bool:
        """
        Verify if password generates correct MIC (Message Integrity Check)
        In real attack, we compare against captured MIC from frame 2 of handshake
        """
        pmk_test = self._calculate_pmk(self.target_ssid, password)
        ptk_test = self._calculate_ptk(pmk_test)
        
        # Simulate MIC verification (simplified)
        return hmac.compare_digest(self.real_ptk[:16], ptk_test[:16])
    
    def dictionary_attack(self, wordlist_path: str) -> Optional[str]:
        """
        Perform dictionary attack against captured handshake
        """
        if not self.handshake_captured:
            print("[-] No handshake captured. Run simulate_handshake_capture first.")
            return None
        
        print(f"\n[*] Starting dictionary attack...")
        print(f"[*] Loading wordlist: {wordlist_path}")
        
        try:
            with open(wordlist_path, 'r', errors='ignore') as f:
                passwords = f.readlines()
        except FileNotFoundError:
            print(f"[-] Wordlist not found: {wordlist_path}")
            return None
        
        print(f"[+] Loaded {len(passwords)} passwords")
        print("[*] Cracking... (this demonstrates the computational cost)\n")
        
        for i, password in enumerate(passwords):
            password = password.strip()
            
            # Show progress every 1000 attempts
            if i % 1000 == 0 and i > 0:
                print(f"    Attempted: {i} passwords...")
            
            # Test this password
            if self._verify_mic(password):
                print(f"\n[+] PASSWORD FOUND: {password}")
                print(f"[+] PMK: {self._calculate_pmk(self.target_ssid, password).hex()}")
                return password
        
        print("\n[-] Password not found in wordlist")
        return None
    
    def brute_force_attack(self, charset: str, min_len: int, max_len: int):
        """
        Demonstrate brute force attack (computationally expensive)
        Shows why WPA/WPA2 requires strong passwords
        """
        import itertools
        
        print(f"\n[*] Starting brute force attack...")
        print(f"[*] Charset: {charset}")
        print(f"[*] Length range: {min_len}-{max_len}")
        print("[!] WARNING: This will take extremely long for WPA\n")
        
        total_combinations = sum(len(charset) ** length 
                                for length in range(min_len, max_len + 1))
        print(f"[*] Total combinations to test: {total_combinations:,}")
        
        attempts = 0
        for length in range(min_len, max_len + 1):
            for guess in itertools.product(charset, repeat=length):
                attempts += 1
                password = ''.join(guess)
                
                if attempts % 10000 == 0:
                    print(f"    Tested: {attempts:,} - Current: {password}")
                
                if self._verify_mic(password):
                    print(f"\n[+] PASSWORD FOUND: {password}")
                    return password
        
        return None


def generate_rainbow_table(ssid: str, wordlist_path: str, output_file: str):
    """
    Generate precomputed PMK table for specific SSID
    Demonstrates why hidden SSIDs and unique SSID names matter
    """
    print(f"\n[*] Generating rainbow table for SSID: {ssid}")
    print(f"[*] This precomputes PMKs to speed up future attacks")
    
    try:
        with open(wordlist_path, 'r') as f_in, open(output_file, 'w') as f_out:
            for line in f_in:
                password = line.strip()
                pmk = hashlib.pbkdf2_hmac('sha1', 
                                         password.encode('utf-8'),
                                         ssid.encode('utf-8'),
                                         4096, 32)
                # Store: password:PMK
                f_out.write(f"{password}:{pmk.hex()}\n")
        
        print(f"[+] Rainbow table saved to: {output_file}")
        print("[!] With this table, cracking is instant for this SSID")
        
    except FileNotFoundError:
        print(f"[-] Wordlist not found")


def demonstrate_wps_attack():
    """
    Demonstrate WPS PIN attack (much faster than WPA)
    Shows why WPS should be disabled
    """
    print("\n" + "="*50)
    print("WPS PIN ATTACK DEMONSTRATION")
    print("="*50)
    
    # WPS PIN is only 8 digits, but last digit is checksum
    # So only 10^7 = 10 million combinations
    print("[*] WPS PIN is 8 digits (actually 7 + checksum)")
    print("[*] Total combinations: 10,000,000")
    print("[*] Can be cracked in hours, not years")
    print("[*] Some routers vulnerable to Pixie Dust (instant)")
    
    # Simulate WPS PIN cracking
    target_pin = "12345670"  # Example
    
    for i in range(10000000):
        pin = f"{i:08d}"
        
        if i % 500000 == 0:
            print(f"    Testing PINs around {pin}...")
        
        # Check checksum (last digit)
        accum = 0
        for j, digit in enumerate(pin[:7]):
            if j % 2 == 0:
                accum += int(digit) * 3
            else:
                accum += int(digit)
        
        checksum = (10 - (accum % 10)) % 10
        
        if checksum == int(pin[7]):
            # Valid checksum, try this PIN
            if pin == target_pin:
                print(f"[+] WPS PIN FOUND: {pin}")
                print("[+] Router password can now be retrieved")
                return pin
    
    return None


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main():
    print("=" * 60)
    print("WIFI SECURITY TESTING - EDUCATIONAL DEMONSTRATION")
    print("FOR AUTHORIZED PENETRATION TESTING ONLY")
    print("=" * 60)
    
    # Create demo wordlist
    demo_wordlist = "demo_wordlist.txt"
    with open(demo_wordlist, 'w') as f:
        f.write("password\n")
        f.write("12345678\n")
        f.write("qwerty\n")
        f.write("letmein\n")
        f.write("secretpassword\n")  # This will be our target
    
    # Initialize cracker
    cracker = WiFiCracker()
    
    # Scenario 1: Capture and crack WPA handshake
    print("\n--- SCENARIO 1: WPA2 Handshake Attack ---")
    cracker.simulate_handshake_capture("MyHomeNetwork", "secretpassword")
    found = cracker.dictionary_attack(demo_wordlist)
    
    # Scenario 2: Show why brute force is impractical
    print("\n--- SCENARIO 2: Brute Force (Demonstration) ---")
    print("[*] Testing only 3-character passwords...")
    cracker.brute_force_attack("abc", 1, 3)
    
    # Scenario 3: WPS vulnerability
    demonstrate_wps_attack()
    
    # Scenario 4: Rainbow tables
    print("\n--- SCENARIO 4: Rainbow Table Attack ---")
    generate_rainbow_table("CommonSSID", demo_wordlist, "rainbow_table.txt")
    
    # Cleanup
    os.remove(demo_wordlist)
    if os.path.exists("rainbow_table.txt"):
        os.remove("rainbow_table.txt")
    
    print("\n" + "=" * 60)
    print("DEFENSIVE RECOMMENDATIONS:")
    print("=" * 60)
    print("1. Use WPA3 if available (SAE protocol, no handshake to capture)")
    print("2. Use strong passwords: 20+ random characters")
    print("3. Disable WPS completely")
    print("4. Use unique SSID names (prevents rainbow table attacks)")
    print("5. Enable MAC filtering (minor obstacle only)")
    print("6. Reduce signal strength to limit physical range")
    print("7. Regularly check for unauthorized devices")
    print("=" * 60)

if __name__ == "__main__":
    main()
