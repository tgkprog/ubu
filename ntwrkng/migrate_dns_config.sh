#!/bin/bash
# Migrate reachme2.com entries from /etc/dnsmasq.conf to /etc/dnsmasq.d/lan.conf

echo "=== Migrating DNS entries to lan.conf ==="

# Add entries to lan.conf
echo "address=/reachme2.com/192.168.1.5" >> /etc/dnsmasq.d/lan.conf
echo "address=/client.reachme2.com/192.168.1.5" >> /etc/dnsmasq.d/lan.conf

# Remove from main config
sed -i '/address=\/reachme2.com\//d; /address=\/client.reachme2.com\//d' /etc/dnsmasq.conf

echo ""
echo "=== Verifying migration ==="
echo "--- /etc/dnsmasq.d/lan.conf ---"
cat /etc/dnsmasq.d/lan.conf

echo ""
echo "--- Checking main config ---"
grep -i reachme2 /etc/dnsmasq.conf || echo "✓ Confirmed: reachme2.com removed from main config"

echo ""
echo "=== Restarting dnsmasq ==="
systemctl restart dnsmasq
sleep 2

echo ""
echo "=== Service status ==="
systemctl status dnsmasq --no-pager -l | head -20

echo ""
echo "=== Testing DNS resolution ==="
dig @127.0.0.1 reachme2.com +short
dig @127.0.0.1 client.reachme2.com +short

echo ""
echo "✓ Migration complete!"
