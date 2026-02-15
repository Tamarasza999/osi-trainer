#!/bin/bash
echo "========================================"
echo "OSI LAB CAPABILITY TEST"
echo "========================================"

echo ""
echo "1. CONTAINER STATUS:"
echo "--------------------"
for c in server client router attacker osi-server; do
    status=$(docker ps --filter "name=$c" --format "{{.Status}}" 2>/dev/null)
    if [ -n "$status" ]; then
        echo "  $c: RUNNING ($status)"
    else
        echo "  $c: NOT RUNNING"
    fi
done

echo ""
echo "2. REQUIRED TOOLS:"
echo "------------------"
for c in server client router attacker osi-server; do
    echo "  $c:"
    for tool in ip iptables ping curl python3; do
        docker exec $c which $tool >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "    $tool: OK"
        else
            echo "    $tool: MISSING"
        fi
    done
done

echo ""
echo "3. OSI LAYER COMMANDS:"
echo "----------------------"
# Layer 1 - Physical
echo -n "  Layer 1 (ip link): "
docker exec client ip link set eth0 down 2>/dev/null && docker exec client ip link set eth0 up 2>/dev/null && echo "OK" || echo "FAIL"

# Layer 2 - Data Link (using ip neigh instead of arp)
echo -n "  Layer 2 (ip neigh): "
docker exec client ip neigh show 2>/dev/null | head -1 && echo "OK" || echo "FAIL"

# Layer 3 - Network
echo -n "  Layer 3 (ip route): "
docker exec client ip route add 10.0.0.0/24 via 172.19.0.99 2>/dev/null && docker exec client ip route del 10.0.0.0/24 via 172.19.0.99 2>/dev/null && echo "OK" || echo "FAIL"

# Layer 4 - Transport
echo -n "  Layer 4 (iptables): "
docker exec client iptables -A INPUT -p tcp --dport 9999 -j REJECT 2>/dev/null && docker exec client iptables -D INPUT -p tcp --dport 9999 -j REJECT 2>/dev/null && echo "OK" || echo "FAIL"

# Layer 5 - Session (using file write instead of sysctl)
echo -n "  Layer 5 (keepalive): "
docker exec client sh -c "echo 7200 > /proc/sys/net/ipv4/tcp_keepalive_time 2>/dev/null" && echo "OK" || echo "FAIL"

# Layer 7 - Application
echo -n "  Layer 7 (curl): "
docker exec client curl -s -o /dev/null http://172.19.0.2 --connect-timeout 3 && echo "OK" || echo "FAIL"

echo ""
echo "4. CONNECTIVITY:"
echo "----------------"
echo -n "  Client -> Server ping: "
docker exec client ping -c 1 -W 1 172.19.0.2 >/dev/null 2>&1 && echo "OK" || echo "FAIL"
echo -n "  Client -> Server HTTP: "
docker exec client curl -s -o /dev/null -w "%{http_code}" http://172.19.0.2 --connect-timeout 3 2>/dev/null | grep -q "200" && echo "OK" || echo "FAIL"
echo -n "  Client -> OSI-Server ping: "
docker exec client ping -c 1 -W 1 172.18.0.4 >/dev/null 2>&1 && echo "OK" || echo "FAIL"
echo -n "  Client -> OSI-Server HTTP: "
docker exec client curl -s -o /dev/null -w "%{http_code}" http://172.18.0.4:8080 --connect-timeout 3 2>/dev/null | grep -q "200" && echo "OK" || echo "FAIL"

echo ""
echo "5. SUMMARY:"
echo "-----------"
total_ok=0
total_fail=0

echo "  Container tools:"
for c in server client router attacker osi-server; do
    ok=0
    fail=0
    for tool in ip iptables ping curl python3; do
        docker exec $c which $tool >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            ok=$((ok + 1))
        else
            fail=$((fail + 1))
        fi
    done
    echo "    $c: $ok tools OK, $fail missing"
    total_ok=$((total_ok + ok))
    total_fail=$((total_fail + fail))
done

echo ""
echo "  Overall: $total_ok tools OK, $total_fail missing"
echo "========================================"