# Getting started 

For the DNS, create a separate VM, and follow the below steps. For our setup, we are using Bind9 open source project to deploy our DNS server. Also, we have created our zone: dns-adwise

**Install this on the DNS server VM**

Step 1: Update your system

```bash
sudo apt update
sudo apt upgrade -y
```

Step 2: Install Bind9

```bash 
sudo apt install bind9 -y
```

Step 3: Configure Bind9
Edit the Bind9 configuration file using a text editor. In this example, we'll use nano:


```bash
sudo nano /etc/bind/named.conf.options
```

Replace the contents of the file with the following configuration:


```bash
options {
        directory "/var/cache/bind";
        recursion yes;
        allow-query { any; };
        forwarders {
                8.8.8.8;
                8.8.4.4;
        };
};
```

This configuration enables DNS recursion, allows queries from any IP address, and sets up Google's public DNS servers (8.8.8.8 and 8.8.4.4) as forwarders.

Save and close the file (Ctrl+X, then Y, then Enter).

Step 4: Create a zone file
Create a new zone file for your domain:


```bash
sudo nano /etc/bind/db.dns-adwise
```

Add the following content to the file:

Replace the IP for your actual DNS IP address


```bash 
$TTL 604800
@       IN      SOA     ns1.dns-adwise. admin.dns-adwise. (
                              1         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns1.dns-adwise.
@       IN      A        10.102.211.101
ns1     IN      A        10.102.211.101
```

Make sure to replace 10.102.211.101 with your actual IP address.

Save and close the file.

Step 5: Configure Bind9 to use the zone file
Edit the Bind9 configuration file again:


```bash
sudo nano /etc/bind/named.conf.local
```

Add the following content to the file:


```bash
zone "dns-adwise" {
        type master;
        file "/etc/bind/db.dns-adwise";
};
```

Save and close the file.

Step 6: Restart Bind9


```bash
sudo systemctl restart bind9
```


Step 7: Test the DNS server
You can now test your DNS server by running the following command:

```bash
nslookup dns-adwise
```

You should see your IP address (10.102.211.101) listed in the output.

That's it! You have successfully set up a DNS server using Bind9 on your Ubuntu 20.04 laptop with the domain name "dns-adwise."


* Change your dns server in the resolv.conf file

```bash
sudo nano /etc/resolv.conf
```

as below 

```diff
# This file is managed by man:systemd-resolved(8). Do not edit.
#
# This is a dynamic resolv.conf file for connecting local clients to the
# internal DNS stub resolver of systemd-resolved. This file lists all
# configured search domains.
#
# Run "resolvectl status" to see details about the uplink DNS servers
# currently in use.
#
# Third party programs must not access this file directly, but only through the
# symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a different way,
# replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.
- nameserver 127.0.0.53
+ nameserver 10.102.211.101
options edns0 trust-ad
search fiu.edu
```


* Test that the DNS server is working 

```bash 
nslookup dns-adwise
```

You should get something similar as the output below 

```bash
nslookup dns-adwise
Server:         10.102.211.101
Address:        10.102.211.101#53

Name:   dns-adwise
Address: 10.102.211.101
```


**Modify the corresponding information related to your setup, such as domain, IP address, etc**












