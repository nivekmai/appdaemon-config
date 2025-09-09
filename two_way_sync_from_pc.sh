#!/bin/bash

rsync -auv \
	--exclude '__pycache__' \
	--exclude '.git' \
	./ hassio@192.168.1.2:/root/addon_configs/a0d7b954_appdaemon/

rsync -auv \
	--exclude '__pycache__' \
	--exclude '.git' \
	hassio@192.168.1.2:/root/addon_configs/a0d7b954_appdaemon/ ./
