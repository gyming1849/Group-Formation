#!/bin/bash

# number of total servers
N=90

USERNAME="ubuntu"

# Path to the aws key pair (.pem file) on your machine
KEY_PATH="~/PATH_TO/example.pem"

# Path to the aws key pair (.pem file) on the primary server.
# Remember to upload the key pair file to the primary server.
LOCAL_KEY_PATH="~/PATH_TO_LOCAL/example.pem"

REPO_PATH="Group-Formation"

HOSTNAMES=(
# Put the private ip addresses of the N servers here
# The first should be the address of the primary server and should equal to SERVER_ADDRESS in the constants.py
# example:
#"10.0.7.242"
#"10.0.4.240"
#"10.0.12.238"
)
