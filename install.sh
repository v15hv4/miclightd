#!/bin/bash

REPO_URL=https://github.com/v15hv4/miclightd

git clone $REPO_URL /tmp/miclightd

mv /tmp/miclightd/miclightd ~/.local/bin
mv /tmp/miclightd/miclightd.service ~/.config/systemd/user

systemctl --user enable --now miclightd.service

echo "Done!"
