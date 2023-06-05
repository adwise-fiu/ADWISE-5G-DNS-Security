# Getting Started 

For our approach, we are doing configuring a Linux machine to act as an SDN switch using Open vSwitch (OVS) and connect it between the NIC (ens160) and the br0 interface.

In order to allow this, it is necessary to install OpenvSwitch, and the RYU controller which will run the script to redirect the DNS packets. 

## Install openvswitch 

* Install the OpenvSwitch package by running the following command:

```bash
sudo apt install openvswitch-switch -y
```

* Verify that OpenvSwitch is installed and running correctly: 

```bash
sudo ovs-vsctl show
```

### Create a bridge

* Create a new bridge by running the following command:

```bash
sudo ovs-vsctl add-br br0
```

* Verify that the bridge is created successfully by running the following command:

```bash
sudo ovs-vsctl show
```


* Create the following bash script. Please replace with the corresponding IP address of the gNB host, gateway, and management interface name. In our case, it's the following:

gNB host IP address: 10.102.211.66
Gateway: 10.102.211.1
Mgmt interface name: ens160


```bash
#!/bin/bash
sudo ovs-vsctl add-port br0  ens160
sudo ip route del default via 10.102.211.1
sudo ip add del 10.102.211.66/24 dev ens160
sudo ip addr add 10.102.211.66/24 dev br0
sudo ip link set dev br0 up
sudo ip route add default via 10.102.211.66
```

**Breakdown of the commands**

**sudo ip route del default via 10.102.211.1:**  It removes the existing default route from the routing table.

**sudo ip add del 10.102.211.66/24 dev ens160:** This command deletes the IP address 10.102.211.66 with a subnet mask of /24 (equivalent to 255.255.255.0) from the network interface ens160. It removes the assigned IP address from the interface.

**sudo ip addr add 10.102.211.66/24 dev br0:** This command adds the IP address 10.102.211.66 with a subnet mask of /24 to the network interface br0. It assigns the specified IP address to the interface.

**sudo ip link set dev br0 up:** This command brings up the network interface br0. It activates the interface, allowing it to send and receive network traffic.

**sudo ip route add default via 10.102.211.1:** This command adds a new default route that points to the IP address 10.102.211.1. It sets the default gateway for the system, specifying where the network traffic should be sent if there is no specific route for a destination.



## Install ryu controller 

* Install pip for Python3 by executing the following command:

```bash
sudo apt install python-pip3
```

* Install Ryu: Open a terminal or command prompt and use the following command to install Ryu using pip3, the Python package installer:

```bash
sudo pip3 install ryu
```


### Add the ryu application

* Change the directory where the application is 

```bash
cd /scripts
```

the script name is *dnsedge.py*


* To run a Ryu controller application using ryu-manager, you can use the following command:

```bash
sudo ryu-manager dnsedge.py
```

For this script, substitute the MAC address and IP address of the GNB, UPF, and DNS




































