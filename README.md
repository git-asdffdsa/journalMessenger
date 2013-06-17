journalMessenger
================

alter output of journalctl (or any other json source) and forward it to different destinations

Currently, the systemd python module may be broken for some (actually fixed by now, see http://cgit.freedesktop.org/systemd/systemd/commit/?id=0a0c35d151570), in which case you can workaround it by using `journalctl -f -n 0 --output=json | ./journalMessenger.py --input stdin`
