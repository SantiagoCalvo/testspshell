#!/usr/bin/env bash

sudo apt update
sudo apt install software-properties-common

sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt install python3.7 -y

sudo apt install python3-pip -y

sudo apt-get install -yq git supervisor

sudo apt install chromium-chromedriver -y

git clone https://github.com/SantiagoCalvo/testspshell.git

cd testspshell/

python3.7 -m pip install pip

python3.7 -m pip install -r requirements.txt

