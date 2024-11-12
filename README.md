# For setting up certificate

https://docs.mitmproxy.org/stable/concepts-certificates/#Quick%20Setup

chatgpt
https://chatgpt.com/c/66e5b2b0-47c8-8013-8dac-3580b1a5376c

# Install the mitmproxy certificate:

- For Browsers:
  - Open your browser settings and go to the certificates section (varies by browser, but usually under "Privacy & Security").
  - Import the mitmproxy-ca-cert.cer file and mark it as trusted for websites.
- For System-wide use:
  - On Windows:
    Open the certmgr.msc tool and import the .cer file under "Trusted Root Certification Authorities."
  - On Linux:
    Copy the certificate to /usr/local/share/ca-certificates/ and run sudo update-ca-certificates. - mv mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt - sudo update-ca-certificates

# To Run the script

- Before running make sure to set proxy to 127.0.0.01:8080

mitmdump -s proxy.py
python GUI_proxy.py
