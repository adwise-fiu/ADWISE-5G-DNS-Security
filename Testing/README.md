# Getting started

After setting up the 5G environment, DNS server, and adding DNS security capabilities, it's time to test our approach. 

## Start the gNB and UE simulation 

### gNB

Access the gNB machine, and run the following

* Change directory to UERANSIM 

```bash
cd UERANSIM
```

* Run the gNB script 

```bash
sudo ./build/nr-ue -c config/open5gs-ue1.yaml
```


### UE

Access the UE machine, and run the following

* Change directory to UERANSIM 

```bash
cd UERANSIM
```

* Run the UE script 

```bash
sudo ./build/nr-ue -c config/open5gs-ue1.yaml
```


## Start the ryu script at the gNB

Open a new terminal or ssh session to run the following command 

```bash
sudo ryu-manager dnsedge.py
```

You should see the following: 

```bash
loading app dnsedge.py

Flow 1 of 3 added

Flow 2 of 3 added

Flow 3 of 3 added
loading app ryu.controller.ofp_handler
instantiating app dnsedge.py of L2Switch
instantiating app ryu.controller.ofp_handler of OFPHandler
```

Only run this for the experiments with the SDN controller. If you want to test the environment without redirecting the DNS packets from the gNB to the DNS server, just stop the script. 


## Testing from the UE sim 

Our experiments consist of using the **kdig** utility to add the *+dnssec* option, anr/or *+tls* option


### UE

Open a new terminal or an ssh session to the UE machine. 



* To run any dns query, do the following:

```bash
 kdig -b 10.45.0.3 @10.102.211.201  +tls +dnssec netfuture.ch
```

-b is to specify the UE IP address
@ it's the DNS IP address (Local DNS)
+tls +dnssec are optional. Add it depending on the experiment
Add at the end the domain name


* Without any security 


```bash
 kdig -b 10.45.0.3 @10.102.211.201  netfuture.ch
```

* With DNSSEC only


```bash
 kdig -b 10.45.0.3 @10.102.211.201  +dnssec netfuture.ch
```

* With DoT (TLS) 


```bash
 kdig -b 10.45.0.3 @10.102.211.201  +tls netfuture.ch
```

* With DNSSEC and DoT


```bash
 kdig -b 10.45.0.3 @10.102.211.201  +tls +dnssec netfuture.ch
```

We also added some bash scripts which allows us to make automate the DNS queries. They are in the bashscripts folder. 


You can modify the domains and the DNS IP address. You can use  Google DNS server, Cloudflare, etc






