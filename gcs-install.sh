#!/usr/bin/env bash

bucket='gs://web-scraper-config/config.json'

set -v

sudo apt-get update
sudo apt-get install -y chromium
sudo apt-get install -y libgbm-dev

# curl -sL https://deb.nodesource.com/setup_12.x | bash -
# apt-get install -yq git libgconf-2-4 nodejs
sudo apt-get install git
sudo apt-get install python-pip  # no sirvio
sudo apt install software-properties-common

git clone https://github.com/sahava/web-scraper-gcp.git

cd web-scraper-gcp
pip install requirements.txt

pyhton taxesNYscraper.py

shutdown -h now