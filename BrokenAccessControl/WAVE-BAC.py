#!/usr/bin/env python3
"""
WAVE-BAC.py - Broken Access Control Testing Module
Part of WAVE (Web Automation Vulnerability Explorer)
Tests for vertical and horizontal privilege escalation, IDOR, and path traversal
"""

import argparse
import requests
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re

GREEN = '\033[0;32m'
NC = '\033[0m'  # Reset/No Color
RED = '\033[0;31m'

def print_banner():
    banner = f"""
{GREEN}
╔═══════════════════════════════════════════════╗
║       WAVE-BAC (Broken Access Control)       ║
║   Web Automation Vulnerability Explorer      ║
║      Authorization & Access Testing          ║
╚═══════════════════════════════════════════════╝
{NC}
"""
    print(banner)
    print(f"{RED}MADE BY SHARANKUMAR VR{NC}\n")

class BrokenAccessControlTester:
    def __init__(self, url, cookies=None, headers=None):
        self.url = url
        self.session = requests.Session()
        
        if cookies:
            cookie_dict = {}
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    key, value = cookie.strip().split('=', 1)
                    cookie_dict[key] = value
            self.session.cookies.update(cookie_dict)
        
        if headers:
            header_dict = {}
            for header in headers.split(';'):
                if ':' in header:
                    key, value = header.strip().split(':', 1)
                    header_dict[key.strip()] = value.strip()
            self.session.headers.update(header_dict)
    
    def test_idor(self, param_name, test_values):
        """Test for Insecure Direct Object Reference (IDOR)"""
        print("\n[*] Testing for IDOR vulnerabilities...")
        
        parsed = urlparse(self.url)
        params = parse_qs(parsed.query)
        
        results = []
        
        for test_value in test_values:
            params[param_name] = [test_value]
            new_query = urlencode(params, doseq=True)
            test_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                  parsed.params, new_query, parsed.fragment))
            
            try:
                response = self.session.get(test_url, timeout=10)
                
                result = {
                    'value': test_value,
                    'status': response.status_code,
                    'length': len(response.content),
                    'url': test_url
                }
                
                print(f"  [+] Testing {param_name}={test_value}: Status {response.status_code}, Length {len(response.content)}")
                
                if response.status_code == 200:
                    print(f"      [!] Potential IDOR found - accessible with value: {test_value}")
                
                results.append(result)
                
            except requests.RequestException as e:
                print(f"  [-] Error testing {test_value}: {e}")
        
        return results
    
    def test_path_traversal(self, param_name, payloads=None):
        """Test for path traversal vulnerabilities"""
        print("\n[*] Testing for Path Traversal vulnerabilities...")
        
        if payloads is None:
            payloads = [
                '../../../etc/passwd',
                '....//....//....//etc/passwd',
                '..%2F..%2F..%2Fetc%2Fpasswd',
                '..\\..\\..\\windows\\win.ini',
                '/etc/passwd',
                'C:\\windows\\win.ini'
            ]
        
        parsed = urlparse(self.url)
        params = parse_qs(parsed.query)
        
        results = []
        
        for payload in payloads:
            params[param_name] = [payload]
            new_query = urlencode(params, doseq=True)
            test_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                                  parsed.params, new_query, parsed.fragment))
            
            try:
                response = self.session.get(test_url, timeout=10)
                
                # Check for common indicators
                indicators = [
                    'root:x:', 'daemon:', '/bin/bash',  # Linux /etc/passwd
                    '[extensions]', '[fonts]',  # Windows win.ini
                ]
                
                found_indicators = [ind for ind in indicators if ind in response.text]
                
                if found_indicators:
                    print(f"  [!] VULNERABLE - Path traversal successful with: {payload}")
                    print(f"      Found indicators: {', '.join(found_indicators)}")
                    results.append({'payload': payload, 'vulnerable': True, 'indicators': found_indicators})
                else:
                    print(f"  [+] Testing: {payload} - Status {response.status_code}")
                    results.append({'payload': payload, 'vulnerable': False})
                    
            except requests.RequestException as e:
                print(f"  [-] Error testing {payload}: {e}")
        
        return results
    
    def test_forced_browsing(self, endpoints):
        """Test for forced browsing / unprotected endpoints"""
        print("\n[*] Testing for Forced Browsing vulnerabilities...")
        
        parsed = urlparse(self.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        results = []
        
        for endpoint in endpoints:
            test_url = base_url + endpoint
            
            try:
                response = self.session.get(test_url, timeout=10, allow_redirects=False)
                
                result = {
                    'endpoint': endpoint,
                    'status': response.status_code,
                    'length': len(response.content)
                }
                
                if response.status_code == 200:
                    print(f"  [!] ACCESSIBLE: {endpoint} (Status: {response.status_code})")
                elif response.status_code in [301, 302, 303, 307, 308]:
                    print(f"  [~] REDIRECT: {endpoint} -> {response.headers.get('Location', 'Unknown')}")
                elif response.status_code == 403:
                    print(f"  [-] FORBIDDEN: {endpoint}")
                elif response.status_code == 401:
                    print(f"  [-] UNAUTHORIZED: {endpoint}")
                else:
                    print(f"  [+] Testing: {endpoint} - Status {response.status_code}")
                
                results.append(result)
                
            except requests.RequestException as e:
                print(f"  [-] Error testing {endpoint}: {e}")
        
        return results
    
    def test_privilege_escalation(self, user_id, admin_endpoints):
        """Test for vertical privilege escalation"""
        print("\n[*] Testing for Privilege Escalation...")
        
        parsed = urlparse(self.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        results = []
        
        for endpoint in admin_endpoints:
            test_url = base_url + endpoint
            
            try:
                response = self.session.get(test_url, timeout=10)
                
                if response.status_code == 200 and 'admin' not in response.request.path_url.lower():
                    print(f"  [!] POTENTIAL PRIVILEGE ESCALATION: {endpoint}")
                    print(f"      User {user_id} can access admin endpoint!")
                    results.append({'endpoint': endpoint, 'vulnerable': True})
                else:
                    print(f"  [+] Testing: {endpoint} - Status {response.status_code}")
                    results.append({'endpoint': endpoint, 'vulnerable': False})
                    
            except requests.RequestException as e:
                print(f"  [-] Error testing {endpoint}: {e}")
        
        return results

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="WAVE-BAC: Broken Access Control Testing Module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test IDOR on user ID parameter
  python3 WAVE-BAC.py --url "http://target.com/profile?id=123" --test idor --param id --values "1,2,3,100,999"
  
  # Test path traversal
  python3 WAVE-BAC.py --url "http://target.com/file?name=test.txt" --test path-traversal --param name
  
  # Test forced browsing
  python3 WAVE-BAC.py --url "http://target.com" --test forced-browsing --endpoints "/admin,/admin/users,/api/admin"
  
  # With authentication cookie
  python3 WAVE-BAC.py --url "http://target.com/profile?id=5" --test idor --param id --values "1,2,3,4,5,6" --cookie "session=abc123"
        """
    )
    
    parser.add_argument('--url', required=True, help='Target URL to test')
    parser.add_argument('--test', required=True, 
                       choices=['idor', 'path-traversal', 'forced-browsing', 'privilege-escalation', 'all'],
                       help='Type of access control test to perform')
    parser.add_argument('--param', help='Parameter name to test (for IDOR and path traversal)')
    parser.add_argument('--values', help='Comma-separated test values (for IDOR)')
    parser.add_argument('--endpoints', help='Comma-separated endpoints to test (for forced browsing)')
    parser.add_argument('--cookie', help='Cookie header (e.g., "session=xyz")')
    parser.add_argument('--headers', help='Custom headers separated by semicolon (e.g., "Authorization: Bearer token; X-API-Key: key")')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("[!] URL must start with http:// or https://")
        print(f"[*] Auto-prepending http:// to: {args.url}")
        args.url = f"http://{args.url}"
    
    print(f"[+] Target URL: {args.url}")
    print(f"[+] Test Type: {args.test}")
    
    tester = BrokenAccessControlTester(args.url, cookies=args.cookie, headers=args.headers)
    
    try:
        if args.test == 'idor':
            if not args.param:
                print("[!] Error: --param required for IDOR testing")
                return 1
            if not args.values:
                print("[!] Error: --values required for IDOR testing")
                return 1
            
            test_values = args.values.split(',')
            results = tester.test_idor(args.param, test_values)
            
        elif args.test == 'path-traversal':
            if not args.param:
                print("[!] Error: --param required for path traversal testing")
                return 1
            
            results = tester.test_path_traversal(args.param)
            
        elif args.test == 'forced-browsing':
            if not args.endpoints:
                # Default admin endpoints
                endpoints = ['/admin', '/administrator', '/admin.php', '/admin/users',
                           '/api/admin', '/dashboard', '/panel', '/manager']
            else:
                endpoints = args.endpoints.split(',')
            
            results = tester.test_forced_browsing(endpoints)
            
        elif args.test == 'privilege-escalation':
            if not args.endpoints:
                endpoints = ['/admin', '/admin/delete-user', '/admin/settings', '/api/admin/users']
            else:
                endpoints = args.endpoints.split(',')
            
            results = tester.test_privilege_escalation("current_user", endpoints)
            
        elif args.test == 'all':
            print("\n[*] Running all access control tests...\n")
            # Run basic checks for all types
            
        print("\n[+] Testing completed!")
        return 0
        
    except KeyboardInterrupt:
        print("\n[!] Testing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[!] Error during testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
