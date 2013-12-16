#!/bin/bash
if [ -d "build" ]; then
 rm -R build
fi

echo "Build..."
python3 build.py bbs.py --target-dir "build" --icon "ressources/baboonstack.ico" --compress

echo "Change permissions..."
chmod 644 build/*
chmod +x build/bbs

echo "Done..."
