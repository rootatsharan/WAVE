#!/usr/bin/env python3
import argparse
import requests
import sys

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
NC = '\033[0m'  # Reset

def print_banner():
    print(f"{GREEN}")
    print("╔═══════════════════════════════════════════════╗")
    print("║           WAVE-SF (Subdomain/API Finder)     ║")
    print("║      Web Automation Vulnerability Explorer   ║")
    print("╚═══════════════════════════════════════════════╝")
    print(f"{NC}{RED}MADE BY SHARANKUMAR VR{NC}\n")

def find_subdomains(domain, wordlist):
    print(f"{YELLOW}[i] Scanning for subdomains of: {domain}{NC}")
    found = []
    for sub in wordlist:
        url = f"http://{sub}.{domain}"
        try:
            res = requests.get(url, timeout=2)
            if res.status_code < 400:
                print(f"{GREEN}[+] Found: {sub}.{domain} (status {res.status_code}){NC}")
                found.append(f"{sub}.{domain}")
        except requests.RequestException:
            continue
    return found

def find_api_endpoints(domain, end_points):
    print(f"{YELLOW}[i] Probing for API endpoints on: {domain}{NC}")
    found = []
    for ep in end_points:
        url = f"https://{domain}/{ep.lstrip('/')}"
        try:
            res = requests.get(url, timeout=2)
            if res.status_code < 400:
                print(f"{GREEN}[+] Found endpoint: /{ep.lstrip('/')} (status {res.status_code}){NC}")
                found.append(ep)
        except requests.RequestException:
            continue
    return found

def main():
    print_banner()
    parser = argparse.ArgumentParser(
        description="WAVE-SF: Subdomain & API Endpoint Finder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 WAVE-SF.py --domain example.com --subdomains --wordlist subs.txt
  python3 WAVE-SF.py --domain example.com --apis --endpoints apis.txt
"""
    )
    parser.add_argument('--domain', required=True, help='Target domain')
    parser.add_argument('--subdomains', action='store_true', help='Find Subdomains')
    parser.add_argument('--apis', action='store_true', help='Find API Endpoints')
    parser.add_argument('--wordlist', help='Wordlist for subdomains')
    parser.add_argument('--endpoints', help='Endpoints file for API paths')
    args = parser.parse_args()

    if args.subdomains:
        if not args.wordlist:
            print(f"{RED}[!] Need a wordlist for subdomain scan (--wordlist subs.txt){NC}")
            sys.exit(1)
        with open(args.wordlist) as f:
            wordlist = [line.strip() for line in f if line.strip()]
        find_subdomains(args.domain, wordlist)

    if args.apis:
        if not args.endpoints:
            print(f"{RED}[!] Need endpoints file for API scan (--endpoints apis.txt){NC}")
            sys.exit(1)
        with open(args.endpoints) as f:
            endpoints = [line.strip() for line in f if line.strip()]
        find_api_endpoints(args.domain, endpoints)

if __name__ == "__main__":
    main()
