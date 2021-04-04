#!/bin/bash

git pull
docker-compose build --pull
docker-compose up -d
