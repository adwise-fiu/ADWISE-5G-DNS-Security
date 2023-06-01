## Acknowledgments ##

This version of 5G-SDN testbed demo was possible by merging open-source projects: 

- [OpenvSwitch](https://github.com/openvswitch/ovs "OpenvSwitch")

- [Ryu](https://github.com/faucetsdn/ryu "Ryu")

- [Open5Gs](https://github.com/open5gs/open5gs "Open5Gs")

- [UERANSIM](https://github.com/aligungr/UERANSIM "UERANSIM")




# Design Open-Source SDN-based 5G Standalone Testbed #

## Project Description ##
This project focuses on utilizing SDN capabilities to allow DNS service at the edge for 5G networks. In addition to DNS, we enabled DNSSEC and DoT to enhance the security and privacy of DNS operations for 5G networks. Our implementation focused on integrating these technologies at the base station in a real 5G testbet, utilizing SDN to facilitate DNS services while ensuring enhanced security and privacy.

## Getting started ##
This project consists of several steps based on building several projects to deploy a secure DNS within a 5G-SDN testbed, which are the following: 

1. Setup the 5G environment
2. Modify the gNB to allow SDN service
3. Deploy and Configure DNS  
4. Enable DNS security extensions (DNSSEC)
5. Enable DNS over TLS (DoT)
6. Start the 5G environment with a secure DNS 
