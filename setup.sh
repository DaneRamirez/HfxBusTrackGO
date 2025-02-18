#!/bin/bash
# Generate self-signed certs
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt