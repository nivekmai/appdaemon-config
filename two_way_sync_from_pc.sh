#!/bin/bash

rsync -auv \
	--exclude '__pycache__' \
	--exclude '.git' \
	./ pi:/home/homeassistant/appdaemon

rsync -auv \
	--exclude '__pycache__' \
	--exclude '.git' \
	pi:/home/homeassistant/appdaemon/ ./
