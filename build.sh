#! /bin/bash

pyinstaller --clean \
    --paths=./env/lib/python3.4/site-packages/pygments \
    --name=pugdebug \
    --onefile \
    --windowed \
    app.py
