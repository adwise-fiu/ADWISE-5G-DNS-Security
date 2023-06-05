To configure BIND9 to use DNS over TLS (DoT) using Stunnel, you can follow these steps:

Install it for the server and server machine

* Install Stunnel 

Stunnel is a utility that allows you to create secure encrypted connections between clients and servers. 

```bash
sudo apt install stunnel4 -y
```
* Verify the version of Stunnel 

```bash
stunnel4 -version
```



1. Generate the SSL/TLS certificates using OpenSSL
2. Generate a self-signed SSL/TLS certificate 

* The following command generates a self-signed certificate (stunnel.pem) and a private key (keystunnel.pem) using OpenSSL. 

```bash
sudo openssl req -new -x509 -nodes -out /etc/stunnel/stunnel.pem -keyout /etc/stunnel/keystunnel.pem -days 3650
```




* Configure Stunnel 

```bash
sudo nano /etc/stunnel/stunnel.conf
```

## Server side 

* Add the following configuration:

Replace and Specify the IP address and port of the Stunnel server and the cert, key, and CAfile directory. 

```file

pid = /run/stunnel4/stunnel.pid
#----------Certs--------
cert = /etc/stunnel/stunnel.pem
key = /etc/stunnel/keystunnel.pem
options = NO_SSLv2
options = NO_SSLv3
options = NO_TLSv1
options = NO_TLSv1.1
options = SINGLE_ECDH_USE
options = SINGLE_DH_USE
ciphers = HIGH:!aNULL:!eNULL:!SSLv2:!SSLv3
[dot]
accept = 853
connect = 127.0.0.1:53
```

* Restart the stunnel4 service

```bash
sudo systemctl restart stunnel4
```

* Test the setup. @10.102.211.201 is our DNS server IP address. 

```bash
kdig @10.102.211.201 google.com +tls
```

