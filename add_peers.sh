#!/bin/bash

# Check if the required arguments are provided
if [ -z "$1" ]; then
  echo "Usage: $0 <ticket> [download] [timeout] [sleep_time]"
  exit 1
fi

# Assign the ticket argument to a variable
ticket=$1

# Assign the download argument to a variable, default to false
download=${2:-false}

# Assign the timeout argument to a variable, default to 3000 milliseconds (3 seconds)
timeout=${3:-3000}

# Assign the sleep_time argument to a variable, default to 30000 milliseconds (30 seconds)
sleep_time=${4:-10000}

# Function to connect to providers with a timeout
connect_providers() {
  # Get the list of providers for the specified CID
  echo "Finding providers for the specified CID..."
  providers=$(ipfs routing findprovs "$ticket")

  # Connect to each provider with a timeout
  echo "Connecting to providers..."
  for provider in $providers; do
    echo "Connecting to $provider with timeout ${timeout}ms..."
    timeout $((timeout / 1000)) ipfs swarm connect /p2p/$provider
  done
}

# Check if the IPFS daemon is already running
if ! pgrep -x "ipfs" > /dev/null; then
  echo "Starting IPFS daemon..."
  ipfs daemon & disown
  
  # Sleep for a few seconds to allow the daemon to start
  sleep 10
else
  echo "IPFS daemon is already running."
fi

Connect to the first five predefined peers
echo "Connecting to predefined peers..."
ipfs swarm connect /ip6/::1/tcp/41722/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip4/127.0.0.1/udp/41722/quic-v1/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip6/::1/udp/41722/quic-v1/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip4/127.0.0.1/udp/41722/quic-v1/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /dnsaddr/bootstrap.libp2p.io/p2p/12D3KooWBpyEfsPpPaHw5s9Q8ssA4SgrbqeohPLmwoVVAXGmrSh6
ipfs swarm connect /ip4/5.79.71.26/tcp/4001/p2p/12D3KooWBGREX75Tnx8YG58DdGSHWDnFzGGpB7uuBPC4vzSHZSMi
ipfs swarm connect /ip4/5.79.71.26/udp/4001/quic-v1/p2p/12D3KooWBGREX75Tnx8YG58DdGSHWDnFzGGpB7uuBPC4vzSHZSMi
ipfs swarm connect /ip4/5.79.71.26/udp/4001/quic-v1/webtransport/certhash/uEiCXkJPv8f6k5JEIrqbP_ySfqUcugDPLh95QORbIsC9Ejg/certhash/uEiBsDSo3nu5j5M7xyZJVDU2K7kh14WRMRbCTiBLt6-0WMw/p2p/12D3KooWBGREX75Tnx8YG58DdGSHWDnFzGGpB7uuBPC4vzSHZSMi

# Start downloading the specified IPFS object in the background if download is true
if [ "$download" = true ]; then
  echo "Retrieving the specified IPFS object in the background..."
  ipfs get --progress=true "$ticket" & disown
else
  echo "Download flag is set to false. Skipping download."
fi

# Main loop to keep getting providers every sleep_time milliseconds
while true; do
  connect_providers
  sleep $((sleep_time / 1000))
done
