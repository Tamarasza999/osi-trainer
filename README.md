# OSI Troubleshooting Trainer  
*A Docker based network troubleshooting simulator for practicing OSI layer diagnostics*

> Practice real network troubleshooting by generating realistic failures across all 7 OSI layers. The trainer injects problems into isolated Docker containers, then allows you to diagnose and fix them inside a controlled lab environment.

## Architecture Concepts

***Container Isolation***  
Each network role (client, server, router, attacker, osi-server) runs inside its own Alpine Linux container. This creates a clean and reproducible lab every time.

```python
self.containers = {
    "server": "172.19.0.2",
    "client": "172.19.0.3",
    "router": "172.19.0.4",
    "attacker": "172.19.0.5",
    "osi-server": "172.18.0.4"
}
```

***OSI Layer Modeling***  
Issues are predefined for every OSI layer from Layer 1 to Layer 7. Each issue includes the command that creates the fault and a matching fix.

```python
self.all_issues = {
    1: [{"name": "Interface Down", "cmd": "ip link set eth0 down"}],
    3: [{"name": "IP Conflict", "cmd": "ip addr add 172.19.0.2/24 dev eth0"}],
    4: [{"name": "HTTP Port Blocked", "cmd": "iptables -A INPUT -p tcp --dport 80 -j REJECT"}]
}
```

***Automated Diagnostics and Fixes***  
The trainer executes `docker exec` commands inside containers. Fixes are stored either as direct commands or lambda functions for context aware corrections.

```python
fix = self.get_fix_command(issue)
if callable(fix):
    return fix(issue)
```

***Persistent Statistics***  
Training sessions are saved locally so you can track performance by layer and review previous scenarios.

```python
self.stats = {
    "scenarios_created": 0,
    "issues_fixed": 0,
    "by_layer": {i: {"created": 0, "fixed": 0} for i in range(1, 8)},
    "history": []
}
```

## Deployment

### 1. Prerequisites

Docker installed and running  
Python 3.6 or newer  

### 2. Clone and Setup

```bash
git clone https://github.com/yourusername/osi-troubleshooting-trainer.git
cd osi-troubleshooting-trainer
```

### 3. Create the Docker network and containers

**Option A: Using the automated setup script**

```bash
chmod +x setup.sh
./setup.sh setup
```

**Option B Manual one liner setup**

```bash
cat setup.txt
```

### 4. Run the Trainer

```bash
python3 osi_trainer.py
```

## Core Implementation

***Issue Creation and Execution***  
The trainer selects random issues from selected layers and executes the command inside the target container. If the command succeeds or reports an already existing state, the issue is recorded.

```python
success, out, err = self.exec_container(container, issue['cmd'])
if success or "File exists" in err or "already exists" in err:
    self.current_issues.append({...})
```

***Auto Troubleshoot with Context Aware Fixes***  
Fix commands can dynamically calculate the correct IP address for the affected container.

```python
fixes = {
    "IP Conflict": lambda issue: f"ip addr flush dev eth0 && ip addr add {self.containers[issue['container']]}/24 dev eth0",
    "Subnet Flushed": lambda issue: f"ip addr add {self.containers[issue['container']]}/24 dev eth0"
}
```

***Comprehensive Diagnostics***  
A diagnostic function checks connectivity, routing, interfaces, and services to provide a clear pass or fail result.

```python
def comprehensive_diagnostics(self):
    print("Client to Server ping:", self.test_ping("client", "172.19.0.2"))
    print("Client HTTP server:", self.test_http("client", "172.19.0.2", 80))
```

***Statistics Tracking***  
All results are stored in `~/.osi_trainer_stats.json` so you can review performance over time.

```json
{
  "scenarios_created": 12,
  "issues_fixed": 28,
  "by_layer": {
    "1": {"created": 5, "fixed": 4},
    "2": {"created": 3, "fixed": 3}
  }
}
```
