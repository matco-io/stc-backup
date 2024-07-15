#!/bin/bash

# Download Kubo v0.29.0
wget https://dist.ipfs.tech/kubo/v0.29.0/kubo_v0.29.0_linux-amd64.tar.gz

# Extract the downloaded tarball
tar -xvzf kubo_v0.29.0_linux-amd64.tar.gz

# Change directory to the extracted folder
cd kubo

# Run the install script with sudo
sudo bash install.sh

# Check the IPFS version
ipfs --version

# Initialize IPFS
ipfs init

# Cat specific IPFS files
ipfs cat /ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/readme
ipfs cat /ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/quick-start

# Start the IPFS daemon in the background and disown the process
ipfs daemon & disown

# Connect to various peers
ipfs swarm connect /ip6/::1/tcp/41722/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip4/127.0.0.1/udp/41722/quic-v1/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip6/::1/udp/41722/quic-v1/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip4/127.0.0.1/udp/41722/quic-v1/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /dnsaddr/bootstrap.libp2p.io/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6

# Retrieve a specific IPFS object with progress indication
ipfs get --progress=true bafyb4iadbza7ckc3djc2k5lfaorwaufcjurzxzkjsj5e7qt2wrguqs7ywm
