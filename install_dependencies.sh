#!/bin/sh
# chmod +x install_dependencies.sh

pip install -r ./crawler/requirements.txt
npm install --prefix ./dashboard-frontend
npm install --prefix ./dashboard-api