"""
ADVANCED OSI TROUBLESHOOTING TRAINER - CLEAN VERSION
Always 3 issues, simplified prompts
"""

import random
import subprocess
import time
import sys
import os
import json
import textwrap
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class AdvancedOsiTrainer:
    def __init__(self):
        self.containers = {
            "attacker": "172.19.0.5",
            "router": "172.19.0.4", 
            "client": "172.19.0.3",
            "server": "172.19.0.2",
            "osi-server": "172.18.0.4"
        }
        
        self.stats = {
            "scenarios_created": 0,
            "issues_fixed": 0,
            "by_layer": {i: {"created": 0, "fixed": 0} for i in range(1, 8)},
            "history": []
        }
        
        self.current_issues = []
        self.container_shells = {}
        
        self.stats_file = Path.home() / ".osi_trainer_stats.json"
        self.load_stats()
        
        self.detect_shells()
        self.initialize_issues()
    
    def detect_shells(self):
        """Detect available shells"""
        self.container_shells = {}
        for container in self.containers:
            success, _, _ = self.exec_container(container, "echo test", shell="sh")
            if success:
                self.container_shells[container] = "sh"
            else:
                self.container_shells[container] = "direct"
    
    def initialize_issues(self):
        """Initialize all possible issues"""
        self.all_issues = {
            1: [
                {"name": "Interface Down", "cmd": "ip link set eth0 down", "difficulty": 1},
                {"name": "Wrong MTU (500)", "cmd": "ip link set eth0 mtu 500", "difficulty": 1},
                {"name": "Interface Promiscuous", "cmd": "ip link set eth0 promisc on", "difficulty": 1},
            ],
            2: [
                {"name": "MAC Address Changed", "cmd": "ip link set eth0 address 00:11:22:33:44:55", "difficulty": 2},
                {"name": "VLAN Created", "cmd": "ip link add link eth0 name eth0.10 type vlan id 10", "difficulty": 2},
            ],
            3: [
                {"name": "Wrong Route", "cmd": "ip route add 10.0.0.0/24 via 172.19.0.99", "difficulty": 2},
                {"name": "IP Conflict", "cmd": "ip addr add 172.19.0.2/24 dev eth0", "difficulty": 3},
                {"name": "Route Loop", "cmd": "ip route add 172.19.0.0/24 via 172.19.0.3", "difficulty": 3},
                {"name": "Subnet Flushed", "cmd": "ip addr flush dev eth0", "difficulty": 3},
            ],
            4: [
                {"name": "HTTP Port Blocked", "cmd": "iptables -A INPUT -p tcp --dport 80 -j REJECT", "difficulty": 3},
                {"name": "ICMP Blocked", "cmd": "iptables -A INPUT -p icmp -j DROP", "difficulty": 2},
                {"name": "SYN Flood Protection", "cmd": "iptables -A INPUT -p tcp --syn -m limit --limit 1/s -j ACCEPT", "difficulty": 4},
            ],
            5: [
                {"name": "TCP Keepalive Disabled", "cmd": "sh -c 'echo 999999 > /proc/sys/net/ipv4/tcp_keepalive_time 2>/dev/null || true'", "difficulty": 3},
            ],
            6: [
                {"name": "Bad Certs Folder", "cmd": "mkdir -p /tmp/badcerts", "difficulty": 1},
                {"name": "Wrong Encoding", "cmd": "sh -c \"echo 'export LANG=C' >> /etc/profile\"", "difficulty": 2},
            ],
            7: [
                {"name": "Web Server Killed", "cmd": "pkill -f 'python.*http' || killall python3", "difficulty": 2},
                {"name": "DNS Broken", "cmd": "sh -c \"echo 'nameserver 127.0.0.1' > /etc/resolv.conf\"", "difficulty": 3},
                {"name": "App Firewall", "cmd": "iptables -A INPUT -p tcp --dport 80 -m string --string 'GET /malicious' --algo bm -j DROP", "difficulty": 4},
            ]
        }
    
    def exec_container(self, container, command, shell=None):
        """Execute command in container"""
        shell_to_use = shell or self.container_shells.get(container, "sh")
        
        try:
            if shell_to_use == "direct":
                cmd = ["docker", "exec", container] + command.split()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            else:
                cmd = ["docker", "exec", container, shell_to_use, "-c", command]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def check_container_access(self, container):
        """Check if container is accessible"""
        return self.exec_container(container, "echo test")[0]
    
    
    def practice_by_difficulty(self):
        """Practice by difficulty level (always 3 issues, random container)"""
        print("\n" + "="*70)
        print("Practice by difficulty level")
        print("="*70)
        
        print("\n1. Beginner (layers 1-3)")
        print("2. Intermediate (layers 4-5)")
        print("3. Advanced (layers 6-7)")
        print("4. Expert (all layers)")
        print("5. Back")
        
        choice = input("\nSelect level (1-5): ").strip()
        
        if choice == "5":
            return
        
        levels = {
            "1": [1, 2, 3],
            "2": [4, 5],
            "3": [6, 7],
            "4": list(range(1, 8))
        }
        
        if choice in levels:
            layers = levels[choice]
            container = random.choice(list(self.containers.keys()))
            self.create_scenario(layers, container, f"Difficulty level {choice}", num_issues=3)
    
    def targeted_layer_scenario(self):
        """Create scenario for specific OSI layer (user chooses container, 3 issues)"""
        print("\n" + "="*70)
        print("Targeted layer scenario")
        print("="*70)
        
        print("\nSelect OSI layer:")
        for i in range(1, 8):
            print(f"{i}. Layer {i} - {self.get_layer_name(i)}")
        print("8. Back")
        
        try:
            choice = int(input("\nSelect layer (1-8): "))
            if 1 <= choice <= 7:
                container = self.select_container()
                if container:
                    self.create_scenario([choice], container, f"Layer {choice} scenario", num_issues=3)
        except:
            pass
    
    def select_container(self):
        """Let user select a container"""
        print("\nSelect target container:")
        containers = list(self.containers.keys())
        for i, container in enumerate(containers, 1):
            print(f"{i}. {container} ({self.containers[container]})")
        print(f"{len(containers)+1}. Random")
        
        try:
            choice = int(input(f"\nChoice (1-{len(containers)+1}): "))
            if 1 <= choice <= len(containers):
                return containers[choice-1]
            elif choice == len(containers) + 1:
                return random.choice(containers)
        except:
            pass
        return random.choice(containers)
    
    def create_scenario(self, layers, container, scenario_name, num_issues=3):
        """Create a scenario with a specific number of issues"""
        print(f"\nCreating {scenario_name} on {container}...")
        print("="*70)
        
        self.current_issues = []
        issues_created = 0

        while issues_created < num_issues:
            layer = random.choice(layers)
            if layer not in self.all_issues or not self.all_issues[layer]:
                continue
            
            issue = random.choice(self.all_issues[layer])
            
            print(f"\nLayer {layer}: {issue['name']}")
            print(f"Command: {issue['cmd']}")
            
            success, out, err = self.exec_container(container, issue['cmd'])
            
            if success or "File exists" in err or "already exists" in err:
                print("  Issue created.")
                self.current_issues.append({
                    "layer": layer,
                    "container": container,
                    "issue": issue['name'],
                    "command": issue['cmd'],
                    "time": datetime.now().isoformat()
                })
                self.stats["by_layer"][layer]["created"] += 1
                issues_created += 1
            else:
                print(f"  Skipped: {err[:80]}")
        
        if self.current_issues:
            self.stats["scenarios_created"] += 1
            self.save_stats()
            print(f"\nCreated {len(self.current_issues)} issues.")
            self.save_scenario()
        else:
            print("\nNo issues were created.")
    
    def get_layer_name(self, layer):
        """Get OSI layer name"""
        names = {
            1: "Physical",
            2: "Data Link", 
            3: "Network",
            4: "Transport",
            5: "Session",
            6: "Presentation",
            7: "Application"
        }
        return names.get(layer, "Unknown")
    
    def real_world_simulations(self):
        """Real-world simulation scenarios"""
        print("\n" + "="*70)
        print("Real-world simulations")
        print("="*70)
        
        simulations = [
            ("Broken web server", [4, 7], "Simulate web server failure"),
            ("Network outage", [1, 3], "Complete network connectivity loss"),
            ("Security breach", [2, 4, 7], "Security incident simulation"),
            ("Slow network", [1, 3, 4], "Performance degradation"),
            ("DNS/DHCP failure", [3, 7], "Name resolution issues")
        ]
        
        for i, (name, layers, desc) in enumerate(simulations, 1):
            print(f"{i}. {name}")
            print(f"   {desc}")
        
        print(f"{len(simulations)+1}. Back")
        
        try:
            choice = int(input(f"\nSelect simulation (1-{len(simulations)+1}): "))
            if 1 <= choice <= len(simulations):
                name, layers, desc = simulations[choice-1]
                container = self.select_container()
                if container:
                    print(f"\nSimulating: {name}")
                    print(f"Description: {desc}")
                    self.create_scenario(layers, container, name, num_issues=3)
        except:
            pass
    
    def comprehensive_diagnostics(self):
        """Run comprehensive diagnostics"""
        print("\n" + "="*70)
        print("Comprehensive diagnostics")
        print("="*70)
        
        print("\nRunning diagnostics...")
        print("-" * 40)
        
        print("\nConnectivity matrix:")
        print("Source -> Target       Status")
        print("-" * 40)
        
        sources = ["client", "server", "osi-server"]
        targets = ["server:80", "osi-server:8080", "router"]
        
        for src in sources:
            for target in targets:
                if ":" in target:
                    host, port = target.split(":")
                    status = self.test_http(src, host, int(port))
                else:
                    status = self.test_ping(src, self.containers[target])
                
                arrow = "->"
                print(f"{src:8} {arrow:2} {target:15} {status}")
        
        print("\nOSI layer tests:")
        print("Layer  Test                          Status")
        print("-" * 40)
        
        layer_tests = [
            (1, "Interface status", "ip link show eth0"),
            (2, "MAC address", "ip link show eth0 | grep link/ether"),
            (3, "IP configuration", "ip -4 addr show eth0"),
            (3, "Routing table", "ip route show"),
            (4, "Port 80 listen", "netstat -tln 2>/dev/null | grep :80 || ss -tln | grep :80"),
            (7, "DNS resolution", "cat /etc/resolv.conf")
        ]
        
        for layer, test_name, cmd in layer_tests:
            success, out, _ = self.exec_container("client", cmd)
            status = "OK" if success and out else "FAIL"
            print(f"L{layer}    {test_name:25} {status}")
        
        print("\nDiagnostic complete.")
    
    def test_ping(self, src, target_ip):
        """Test ping connectivity"""
        success, _, _ = self.exec_container(src, f"ping -c 1 -W 1 {target_ip}")
        return "OK" if success else "FAIL"
    
    def test_http(self, src, host, port):
        """Test HTTP connectivity"""
        success, _, _ = self.exec_container(src, f"curl -s -o /dev/null -w '%{{http_code}}' http://{host}:{port} --connect-timeout 3")
        return "OK" if success else "FAIL"
    
    def auto_troubleshoot_demo(self):
        """Automatic troubleshooting demo"""
        print("\n" + "="*70)
        print("Auto-troubleshoot demo")
        print("="*70)
        
        if not self.current_issues:
            print("No active issues to troubleshoot.")
            return
        
        print("\nStarting auto-diagnosis...")
        time.sleep(1)
        
        for i, issue in enumerate(self.current_issues, 1):
            print(f"\nStep {i}: Analyzing layer {issue['layer']} issue...")
            print(f"   Problem: {issue['issue']}")
            time.sleep(0.5)
            
            fix = self.get_fix_command(issue)
            if fix:
                print(f"   Solution: {fix if isinstance(fix, str) else ' '.join(fix)}")
                time.sleep(0.5)
                
                print("   Applying fix...", end="", flush=True)
                success, _, err = self.exec_container(issue['container'], 
                    fix if isinstance(fix, str) else " ".join(fix))
                
                if success:
                    print(" done.")
                    self.stats["issues_fixed"] += 1
                    self.stats["by_layer"][issue["layer"]]["fixed"] += 1
                else:
                    print(" warning.")
                    print(f"   Note: {err[:60]}")
            else:
                print("   No automated fix available.")
            
            time.sleep(0.5)
        
        self.current_issues = []
        self.save_stats()
        print("\nAuto-troubleshoot complete.")
    
    def get_fix_command(self, issue):
        """Get fix command for an issue"""
        fixes = {
            "Interface Down": "ip link set eth0 up",
            "Wrong MTU (500)": "ip link set eth0 mtu 1500",
            "Interface Promiscuous": "ip link set eth0 promisc off",
            "MAC Address Changed": "ip link set eth0 address 02:42:ac:13:00:03",
            "VLAN Created": "ip link delete eth0.10",
            "Wrong Route": "ip route del 10.0.0.0/24 via 172.19.0.99",
            "IP Conflict": lambda issue: f"ip addr flush dev eth0 2>/dev/null || true && ip addr add {self.containers[issue['container']]}/24 dev eth0",
            "Route Loop": "ip route del 172.19.0.0/24 via 172.19.0.3",
            "Subnet Flushed": lambda issue: f"ip addr add {self.containers[issue['container']]}/24 dev eth0",
            "HTTP Port Blocked": "iptables -D INPUT -p tcp --dport 80 -j REJECT",
            "ICMP Blocked": "iptables -D INPUT -p icmp -j DROP",
            "SYN Flood Protection": "iptables -D INPUT -p tcp --syn -m limit --limit 1/s -j ACCEPT",
            "TCP Keepalive Disabled": "sh -c 'echo 7200 > /proc/sys/net/ipv4/tcp_keepalive_time 2>/dev/null || true'",
            "Bad Certs Folder": "rm -rf /tmp/badcerts",
            "Wrong Encoding": "sh -c \"grep -v 'export LANG=C' /etc/profile > /tmp/profile && mv /tmp/profile /etc/profile\"",
            "Web Server Killed": "sh -c 'cd /tmp && python3 -m http.server 80 >/dev/null 2>&1 &'",
            "DNS Broken": "sh -c \"echo 'nameserver 8.8.8.8' > /etc/resolv.conf\"",
            "App Firewall": "iptables -D INPUT -p tcp --dport 80 -m string --string 'GET /malicious' --algo bm -j DROP"
        }
        
        fix = fixes.get(issue["issue"])
        if callable(fix):
            return fix(issue)
        return fix
    
    def settings_and_tools(self):
        """Settings and tools menu"""
        print("\n" + "="*70)
        print("Settings and tools")
        print("="*70)
        
        while True:
            print("\n1. Reset all containers")
            print("2. Check container capabilities")
            print("3. Install missing tools")
            print("4. Test network connectivity")
            print("5. Back to main menu")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self.reset_all_containers()
            elif choice == "2":
                self.check_capabilities()
            elif choice == "3":
                self.install_tools()
            elif choice == "4":
                self.test_network()
            elif choice == "5":
                break
    
    def reset_all_containers(self):
        """Reset all containers to clean state"""
        print("\nResetting all containers...")
        
        for container in self.containers:
            print(f"\nCleaning {container}...")
            
            self.exec_container(container, "iptables -F")
            self.exec_container(container, "iptables -X")
            
            self.exec_container(container, "ip link set eth0 up 2>/dev/null || true")
            self.exec_container(container, "ip link set eth0 promisc off 2>/dev/null || true")
            self.exec_container(container, "ip link set eth0 mtu 1500 2>/dev/null || true")
            self.exec_container(container, "ip link delete eth0.10 2>/dev/null || true")
            
            self.exec_container(container, "ip route del 10.0.0.0/24 via 172.19.0.99 2>/dev/null || true")
            self.exec_container(container, "ip route del 172.19.0.0/24 via 172.19.0.3 2>/dev/null || true")
            
            if container in ["server", "osi-server"]:
                port = 80 if container == "server" else 8080
                self.exec_container(container, f"pkill -f 'python.*http' 2>/dev/null || true")
                self.exec_container(container, f"cd /tmp && python3 -m http.server {port} >/dev/null 2>&1 &")
        
        print("\nAll containers reset.")
    
    def check_capabilities(self):
        """Check container capabilities"""
        print("\nContainer capabilities:")
        print("-" * 40)
        
        for container in self.containers:
            print(f"\n{container}:")
            
            success, _, _ = self.exec_container(container, "ip link set eth0 down 2>/dev/null; ip link set eth0 up")
            print(f"  NET_ADMIN: {'yes' if success else 'no'}")
            
            tools = ["ip", "iptables", "curl", "python3", "ping"]
            for tool in tools:
                success, _, _ = self.exec_container(container, f"which {tool}")
                print(f"  {tool}: {'yes' if success else 'no'}")
    
    def install_tools(self):
        """Install missing tools"""
        print("\nInstalling tools...")
        
        packages = "iproute2 iptables curl python3 iputils"
        
        for container in self.containers:
            print(f"\n{container}:", end="", flush=True)
            success, _, err = self.exec_container(container, f"apk add --no-cache {packages} 2>&1")
            if success:
                print(" done.")
            else:
                print(f" warning ({err[:40]})")
        
        print("\nTools installation attempted.")
    
    def test_network(self):
        """Test network connectivity"""
        print("\nNetwork connectivity test:")
        print("-" * 40)
        
        tests = [
            ("Client -> Server", "client", "172.19.0.2", 80),
            ("Client -> OSI-Server", "client", "172.18.0.4", 8080),
            ("Server -> Client", "server", "172.19.0.3", 0),
            ("Router -> Client", "router", "172.19.0.3", 0)
        ]
        
        for name, src, target, port in tests:
            if port > 0:
                success, _, _ = self.exec_container(src, f"curl -s -o /dev/null -w '%{{http_code}}' http://{target}:{port} --connect-timeout 3")
            else:
                success, _, _ = self.exec_container(src, f"ping -c 1 -W 1 {target}")
            
            print(f"{name:20} {'ok' if success else 'fail'}")
    
    def statistics_and_history(self):
        """Show statistics and history"""

        print("\n" + "="*70)
        print("Statistics and history")
        print("="*70)

        print(f"\nOverall statistics:")
        print(f"   Scenarios created: {self.stats['scenarios_created']}")
        print(f"   Issues fixed: {self.stats['issues_fixed']}")

        print("\nBy OSI layer:")
        print("   Layer  Created  Fixed  Success rate")
        print("   " + "-" * 35)

        for layer in range(1, 8):
            created = self.stats["by_layer"][layer]["created"]
            fixed = self.stats["by_layer"][layer]["fixed"]
            rate = (fixed / created * 100) if created > 0 else 0
            print(f"   L{layer}     {created:6}  {fixed:5}  {rate:5.1f}%")

        if self.stats["history"]:
            print(f"\nRecent history ({len(self.stats['history'])} items):")
            for i, item in enumerate(self.stats["history"][-5:], 1):
                print(f"   {i}. {item}")
    
    def help_and_tutorials(self):
        """Help and tutorials"""
        print("\n" + "="*70)
        print("Help and tutorials")
        print("="*70)
        
        tutorials = [
            ("OSI model", self.osi_tutorial),
            ("Troubleshooting methodology", self.troubleshooting_methodology),
            ("Common commands", self.common_commands),
            ("About this trainer", self.about_trainer)
        ]
        
        while True:
            print("\n1. OSI model explanation")
            print("2. Troubleshooting methodology")
            print("3. Common network commands")
            print("4. About this trainer")
            print("5. Back to main menu")
            
            choice = input("\nSelect tutorial (1-5): ").strip()
            
            if choice == "5":
                break
            elif 1 <= int(choice) <= 4:
                tutorials[int(choice)-1][1]()
    
    def osi_tutorial(self):
        """OSI model tutorial"""
        print("\n" + "="*70)
        print("OSI model explanation")
        print("="*70)
        
        layers = [
            (1, "Physical", "Cables, switches, physical connections"),
            (2, "Data Link", "MAC addresses, switches, frames"),
            (3, "Network", "IP addresses, routers, packets"),
            (4, "Transport", "TCP/UDP, ports, segments"),
            (5, "Session", "Connections, sessions, RPC"),
            (6, "Presentation", "Encryption, compression, formatting"),
            (7, "Application", "HTTP, DNS, SMTP, applications")
        ]
        
        print("\nThe OSI model has 7 layers:")
        for num, name, desc in layers:
            print(f"\nLayer {num}: {name}")
            print(f"   {desc}")
        
        print("\nMnemonic: 'Please Do Not Throw Sausage Pizza Away'")
        print("          (Physical, Data Link, Network, Transport, Session, Presentation, Application)")
    
    def troubleshooting_methodology(self):
        """Troubleshooting methodology"""
        print("\n" + "="*70)
        print("Troubleshooting methodology")
        print("="*70)
        
        steps = [
            ("1. Identify", "Clearly define the problem"),
            ("2. Gather", "Collect information and symptoms"),
            ("3. Analyze", "Determine probable cause"),
            ("4. Test", "Test your theory"),
            ("5. Implement", "Implement the solution"),
            ("6. Verify", "Verify full functionality"),
            ("7. Document", "Document findings and solution")
        ]
        
        print("\n7-step troubleshooting methodology:")
        for step, desc in steps:
            print(f"\n{step}. {desc}")
        
        print("\nOSI layer approaches:")
        print("   Top-down: start at layer 7, work down")
        print("   Bottom-up: start at layer 1, work up")
        print("   Divide-and-conquer: start in middle (layer 3/4)")
    
    def common_commands(self):
        """Common network commands"""
        print("\n" + "="*70)
        print("Common network commands")
        print("="*70)
        
        commands = [
            ("ip link show", "Show network interfaces"),
            ("ip addr show", "Show IP addresses"),
            ("ip route show", "Show routing table"),
            ("ping <host>", "Test connectivity"),
            ("curl <url>", "Test HTTP connectivity"),
            ("iptables -L", "List firewall rules"),
            ("netstat -tln", "Show listening ports"),
            ("cat /etc/resolv.conf", "Show DNS configuration")
        ]
        
        print("\nEssential commands:")
        for cmd, desc in commands:
            print(f"\n  {cmd}")
            print(f"    {desc}")
    
    def about_trainer(self):
        """About this trainer"""
        print("\n" + "="*70)
        print("About this trainer")
        print("="*70)
        
        about_text = """
        This OSI troubleshooting trainer is designed to help you practice
        network troubleshooting skills in a safe, controlled environment.
        
        Features:
        * Practice troubleshooting all 7 OSI layers
        * Real-world simulation scenarios
        * Comprehensive diagnostics
        * Auto-troubleshoot demonstrations
        * Statistics tracking
        
        The trainer uses Docker containers to simulate network issues
        that you would encounter in real production environments.
        
        Use this tool to:
        * Prepare for network certifications
        * Practice troubleshooting methodology
        * Learn common network commands
        * Understand the OSI model in practice
        """
        
        print(textwrap.dedent(about_text))
    
    def save_scenario(self):
        """Save current scenario to history"""
        if self.current_issues:
            scenario = {
                "timestamp": datetime.now().isoformat(),
                "issues": len(self.current_issues),
                "layers": list(set(issue["layer"] for issue in self.current_issues)),
                "container": self.current_issues[0]["container"]
            }
            self.stats["history"].append(scenario)
            self.save_stats()
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def load_stats(self):
        """Load statistics from file"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    loaded = json.load(f)
                    self.stats.update(loaded)
        except:
            pass
    
    def main_menu(self):
        """Main menu"""
        while True:
            print("\n" + "="*70)
            print("Advanced OSI Troubleshooting Trainer")
            print("="*70)
            
            menu = [
                ("Practice by difficulty level", self.practice_by_difficulty),
                ("Generate targeted layer scenario", self.targeted_layer_scenario),
                ("Real-world simulations", self.real_world_simulations),
                ("Comprehensive diagnostics", self.comprehensive_diagnostics),
                ("Auto-troubleshoot demo", self.auto_troubleshoot_demo),
                ("Settings and tools", self.settings_and_tools),
                ("Statistics and history", self.statistics_and_history),
                ("Help and tutorials", self.help_and_tutorials),
                ("Exit", None)
            ]
            
            for i, (title, _) in enumerate(menu, 1):
                print(f"{i}. {title}")
            
            print("-" * 70)
            
            try:
                choice = input(f"\nSelect option (1-{len(menu)}): ").strip()
                if choice == str(len(menu)):
                    print("\nGoodbye! Happy troubleshooting!")
                    break
                elif 1 <= int(choice) <= len(menu) - 1:
                    menu[int(choice)-1][1]()
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                print("\n\nInterrupted.")
                break
            except:
                print("Invalid input.")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("Advanced OSI Troubleshooting Trainer - Clean Version")
    print("="*70)
    print("Initializing...")
    
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Docker is not running or not installed.")
            print("Please start Docker and try again.")
            return
    except FileNotFoundError:
        print("Docker is not installed.")
        print("Please install Docker and try again.")
        return
    
    trainer = AdvancedOsiTrainer()
    trainer.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        print("Please make sure your Docker setup is running correctly.")