#!/bin/bash
echo "Creating virtual enviroment ..."
python3 -m venv aws_lb_venv 
echo "Installing dependencies ..."
pip install -q boto3, time
echo "Initiating gitea cloud deploy ..."
chmod +x a.py
python3 a.py