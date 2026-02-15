#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_current() {
    echo -e "\n${YELLOW}Current Docker Status:${NC}"
    echo -e "\nContainers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
    echo -e "\nNetworks:"
    docker network ls --format "table {{.Name}}\t{{.Driver}}" | grep -E "main-network|osi-network"
}

clean_all() {
    echo -e "\n${YELLOW}Current containers and networks:${NC}"
    show_current
    
    echo -e "\n${RED}WARNING: This will remove all containers and networks!${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [[ $confirm == "yes" ]]; then
        echo -e "\n${YELLOW}Stopping all containers...${NC}"
        docker stop $(docker ps -q) 2>/dev/null || true
        
        echo -e "\n${YELLOW}Removing all containers...${NC}"
        docker rm $(docker ps -aq) 2>/dev/null || true
        
        echo -e "\n${YELLOW}Pruning networks...${NC}"
        docker network prune -f
        
        echo -e "\n${GREEN}Cleanup complete!${NC}"
        echo -e "\n${YELLOW}Verifying cleanup:${NC}"
        docker ps -a
        docker network ls | grep -E "main-network|osi-network" || echo "All clean!"
    else
        echo -e "\n${GREEN}Cleanup cancelled.${NC}"
    fi
}

setup_lab() {
    echo -e "\n${YELLOW}Setting up OSI Troubleshooting Lab...${NC}"
    
    if docker network ls | grep -q "main-network"; then
        echo "Network main-network already exists. Skipping creation."
    else
        docker network create --subnet=172.19.0.0/16 main-network
    fi
    
    if docker network ls | grep -q "osi-network"; then
        echo "Network osi-network already exists. Skipping creation."
    else
        docker network create --subnet=172.18.0.0/16 osi-network
    fi
    
    echo "Creating containers..."
    
    docker run -d --name server --network=main-network --ip=172.19.0.2 --cap-add=NET_ADMIN alpine sh -c "apk add python3 curl iptables iproute2 procps --no-cache && python3 -m http.server 80 & tail -f /dev/null"
    echo "  server created: 172.19.0.2"
    
    docker run -d --name client --network=main-network --ip=172.19.0.3 --cap-add=NET_ADMIN alpine sh -c "apk add curl iptables iproute2 iputils python3 procps --no-cache && tail -f /dev/null"
    echo "  client created: 172.19.0.3"
    
    docker run -d --name router --network=main-network --ip=172.19.0.4 --cap-add=NET_ADMIN --privileged alpine sh -c "apk add iptables iproute2 curl python3 procps --no-cache && echo 1 > /proc/sys/net/ipv4/ip_forward && tail -f /dev/null"
    echo "  router created: 172.19.0.4"
    
    docker run -d --name attacker --network=main-network --ip=172.19.0.5 --cap-add=NET_ADMIN alpine sh -c "apk add nmap curl iptables iproute2 python3 procps --no-cache && tail -f /dev/null"
    echo "  attacker created: 172.19.0.5"
    
    docker run -d --name osi-server --network=osi-network --ip=172.18.0.4 --cap-add=NET_ADMIN alpine sh -c "apk add python3 curl iptables iproute2 procps --no-cache && python3 -m http.server 8080 & tail -f /dev/null"
    echo "  osi-server created: 172.18.0.4"
    
    docker network connect --ip 172.18.0.5 osi-network router
    docker network connect --ip 172.18.0.3 osi-network client
    echo "  networks connected"
    
    sleep 3
    
    docker exec client ip route add 172.18.0.0/16 via 172.19.0.4
    echo "  routing configured"

    echo "  applying compatibility fixes..."
    for c in server client router attacker osi-server; do 
        docker exec $c sh -c "apk add iproute2 procps --no-cache 2>/dev/null; echo 'alias arp=\"ip neigh\"' >> /etc/profile; echo 7200 > /proc/sys/net/ipv4/tcp_keepalive_time 2>/dev/null || true" && echo "    $c fixed" || echo "    $c failed"
    done
    
    echo -e "\n${GREEN}Setup complete!${NC}"
    show_current
}

case "$1" in
    setup)
        setup_lab
        ;;
    clean)
        clean_all
        ;;
    status)
        show_current
        ;;
    *)
        echo "Usage: $0 {setup|clean|status}"
        echo "  setup  - Create networks and containers"
        echo "  clean  - Remove all containers and networks (with confirmation)"
        echo "  status - Show current containers and networks"
        exit 1
        ;;
esac