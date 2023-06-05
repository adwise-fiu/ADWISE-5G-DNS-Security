#!/bin/bash

domains=(
    "internetsociety.org"
    "dnssec-tools.org"
    "dnssec-deployment.org"
    "kumari.net"
    "huque.com"
    "bortzmeyer.org"
    "afnic.fr"
    "netfuture.ch"
)

for domain in "${domains[@]}"; do
    output=$(kdig -b 10.45.0.3 @10.102.211.201 "$domain" | tail -n 3)
#    echo "output: $output"
    latency=$(echo "$output" | grep -oP "(?<=in )[0-9.]+")
    received=$(echo "$output" | grep -oP "(?<=Received )[0-9]+")
    echo "Domain: $domain | Latency: $latency ms | Received Size: $received B"
    output=$(kdig -b 10.45.0.3 @10.102.211.201 "$domain" | tail -n 3)
    latency=$(echo "$output" | grep -oP "(?<=in )[0-9.]+")
    received=$(echo "$output" | grep -oP "(?<=Received )[0-9]+")
    echo "Domain: $domain | Latency: $latency ms | Received Size: $received B"
done
