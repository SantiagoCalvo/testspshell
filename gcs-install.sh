#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -yq git supervisor python3.7 python3-pip python3-distutils
pip3 install --upgrade pip virtualenv

sudo apt-get install -y chromium
# sudo apt-get install -y libgbm-dev

python3.7 -m virtualenv py37
source py37/bin/activate




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