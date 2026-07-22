# Linux Firewall Simulation Lab



## Objective

Configure a Linux container firewall using `iptables` to:

* Allow HTTP (80)
* Allow HTTPS (443)
* Block SSH (22)

---

## Container Setup

Run Ubuntu container with network administration privileges:

```bash
docker run -it --rm --cap-add=NET_ADMIN --name firewall-demo ubuntu bash
```

Install required packages:

```bash
apt update
apt install -y iptables nginx openssh-server
```

Start services:

```bash
service nginx start
service ssh start
```

---

## Firewall Rules

```bash
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

iptables -A INPUT -p tcp --dport 22 -j DROP

iptables -P INPUT DROP
```

Verify rules:

```bash
iptables -L -n -v
```

<img width="850" height="272" alt="Image" src="https://github.com/user-attachments/assets/7ade2cb7-6763-4b0b-8843-5b302616066f" />

---

## Testing

### HTTP Access Allowed

```bash
docker run --rm curlimages/curl -I http://172.17.0.2
```

**Result:**

```text
HTTP/1.1 200 OK
```

This confirms Port 80 is accessible.

<img width="850" height="341" alt="Image" src="https://github.com/user-attachments/assets/d173ff2a-3d9d-4c77-a882-60716a646751" />

---

### SSH Access Blocked

```bash
docker run --rm alpine nc -zv -w 5 172.17.0.2 22
```

**Result:**

```text
Operation timed out
```

This confirms Port 22 is blocked by the firewall.

<img width="850" height="255" alt="Image" src="https://github.com/user-attachments/assets/25cd7fd6-382d-48dc-a769-d45c271520fe" />
---

## Conclusion

The firewall was successfully configured using `iptables`. HTTP traffic was allowed, while SSH access was blocked, meeting all assignment requirements.
