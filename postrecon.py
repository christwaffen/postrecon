#!/usr/bin/env python3
import os
import subprocess
import platform

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""{Colors.HEADER}====================================================
    PostRecon by Maciej Oleksy - Linux Recon Tool
    ===================================================={Colors.ENDC}"""
    print(banner)

def run_command(command):
    """executing shell commands"""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return stdout.strip()
    except Exception:
        return ""

def get_system_info():
    """basic information about the machine"""
    print(f"\n{Colors.OKBLUE}[*] System info {Colors.ENDC}")
    
    kernel = platform.release()
    hostname = platform.node()
    # Fixing the f-string error for older Python versions
    distro_cmd = "cat /etc/issue | head -n 1 | cut -d' ' -f1"
    distro = run_command(distro_cmd)
    
    print(f"Kernel: {kernel}")
    print(f"Distribution: {distro}")
    print(f"Hostname: {hostname}")

def get_user_info():
    """information about the current user and their privileges"""
    print(f"\n{Colors.OKBLUE}[*] User info {Colors.ENDC}")
    
    user = run_command("whoami")
    uid = os.getuid()
    id_info = run_command("id")
    
    print(f"Current user: {user} (ID: {uid})")
    print(f"Groups: {id_info}")
    
    # Check for passwordless sudo
    print(f"Sudo without a password:")
    sudo_check = run_command("sudo -l -n 2>/dev/null")
    if sudo_check:
        print(f"{Colors.OKGREEN}{sudo_check}{Colors.ENDC}")
    else:
        print("Sudo not detected")

def check_shell_history():
    """searching history files for passwords and API keys"""
    print(f"\n{Colors.OKBLUE}[*] Shell history analysis (Searching for passwords/keys){Colors.ENDC}")
    
    history_files = [
        '~/.bash_history', '~/.zsh_history', '~/.python_history', 
        '~/.mysql_history', '~/.nano_history', '~/.viminfo'
    ]
    
    keywords = ['pass', 'pwd', 'token', 'key', 'mysql', 'ssh', 'curl', 'wget', 'admin', 'config', '{user}']
    grep_pattern = "|".join(keywords)
    found_any = False

    for h_file in history_files:
        path = os.path.expanduser(h_file)
        if os.access(path, os.R_OK):
            # Keywords and the last 15 results
            cmd = f"grep -Ei '{grep_pattern}' {path} 2>/dev/null | tail -n 15"
            results = run_command(cmd)
            if results:
                print(f"{Colors.WARNING}[!] Potentially sensitive data in {h_file}:{Colors.ENDC}")
                print(results)
                found_any = True
    
    if not found_any:
        print("[-] No sensitive phrases found in history files")

def check_network():
    """checking for open listening ports"""
    print(f"\n{Colors.OKBLUE}[*] Network and ports (Listening){Colors.ENDC}")
    # Try `ss`; if that doesn't work, use `netstat`
    net = run_command("ss -tulpn | grep LISTEN")
    if not net:
        net = run_command("netstat -tulpn | grep LISTEN")
    
    if net:
        print(net)
    else:
        print("No information about ports (you may lack permissions for ss/netstat)")

def check_cron_jobs():
    """analysis of Cron jobs for privilege escalation"""
    print(f"\n{Colors.OKBLUE}[*] Task scheduler (Cron){Colors.ENDC}")
    
    user_cron = run_command("crontab -l 2>/dev/null")
    if user_cron:
        print(f"{Colors.BOLD}your tasks:{Colors.ENDC}\n{user_cron}")
    else:
        print("No tasks in crontab for the current user")

    print(f"\n{Colors.WARNING}[!] Cron files writable by you:{Colors.ENDC}")
    writable_cron = run_command("find /etc/cron* -writable -type f 2>/dev/null")
    if writable_cron:
        print(f"{Colors.FAIL}{writable_cron}{Colors.ENDC}")
    else:
        print("No writable files in /etc/cron*")

def check_sensitive_files():
    """checking permissions for critical system files"""
    print(f"\n{Colors.OKBLUE}[*] Checking sensitive files{Colors.ENDC}")
    files_to_check = [
        '/etc/passwd', '/etc/shadow', '/root/.bash_history', 
        '~/.ssh/id_rsa', '/etc/exports', '/etc/hosts'
    ]
    for f in files_to_check:
        path = os.path.expanduser(f)
        if os.access(path, os.R_OK):
            print(f"{Colors.OKGREEN}[+] Reading available: {f}{Colors.ENDC}")
        else:
            print(f"[-] No access to: {f}")

def find_suid_files():
    """searching for files with the SUID bit"""
    print(f"\n{Colors.OKBLUE}[*] Files with the SUID bit (potential escalation){Colors.ENDC}")
    cmd = "find /usr/bin /usr/sbin /bin /sbin -perm -4000 -type f 2>/dev/null"
    suids = run_command(cmd)
    if suids:
        print(suids)
    else:
        print("No SUID files found in typical locations")

def check_tmp_exploits():
    """analysis of temporary directories"""
    print(f"\n{Colors.OKBLUE}[*] Parsing the /tmp and /var/tmp directory{Colors.ENDC}")
    
    # 1. Root files that you can edit
    root_files = run_command("Find /tmp /var/tmp -user root -writable -type f 2>/dev/null")
    if root_files:
        print(f"{Colors.FAIL}[!] Root's files writable by you in /tmp:{Colors.ENDC}\n{root_files}")

    # 2. Scripts (Bash, Python, etc.)
    scripts_cmd = r"ls -la /tmp /var/tmp | grep -E '\.(sh|py|pl|rb)$'"
    scripts = run_command(scripts_cmd)
    if scripts:
        print(f"{Colors.WARNING}[!] Scripts found in /tmp:{Colors.ENDC}\n{scripts}")

    # 3. Unix Sockets
    sockets = run_command("Find /tmp /var/tmp -type s 2>/dev/null")
    if sockets:
        print(f"{Colors.OKGREEN}[+] Unix sockets found:{Colors.ENDC}\n{sockets}")

def main():
   
    if os.name != 'posix':
        print(f"{Colors.FAIL}This tool works only on Linux systems.{Colors.ENDC}")
        return

    print_banner()
    
    # Running all modules sequentially
    get_system_info()
    get_user_info()
    check_shell_history()
    check_network()
    check_cron_jobs()
    check_sensitive_files()
    find_suid_files()
    check_tmp_exploits()
    
    print(f"\n{Colors.HEADER}=== Checking Complete ==={Colors.ENDC}")

if __name__ == "__main__":
    main()