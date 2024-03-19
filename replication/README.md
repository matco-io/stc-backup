# Replicate STC

The Standard Template Construct (STC) can be conveniently replicated on your personal computer or server. 
The STC consists of several critical components: dataset, search metadata,
and a web interface with a search engine (referred to as Web STC in subsequent references).

Replicating the search metadata and web interface can enhance your search performance. 
Simultaneously, replicating the dataset can convert your computer into a comprehensive, standalone library.

## Replicating the dataset of books and scholarly publications.

**Choose only 1a either 1b according to your needs and skills**

The STC is using a mixed scheme for dataset replication.
Replication between core seeders with higher technical skills is done with [Iroh](https://iroh.computer/docs).

### Step 0: Prepare Server

For better performance you should have CoW and reflink-aware filesystem (we are using BTRFS, but ZFS/XFS may also be suitable).
Other file systems are also okay, but you should keep in mind that Trident laying out files in a single directory 
(so check how many files your FS may put in a single directory without degrading) and using reflinks internally.

### Step 1a: Setting up Iroh replication using Trident server

Iroh allows high-performance replication by launching Docker image with the Trident application on the server.
Trident is laying out files in a plain folder, making them available for any further usage,
keep internal records for managing data and allowing to push data further to IPFS (no-copy mode) or S3.

#### Step 1a.1 (optional): Setup IPFS

Follow the <a href="https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions" target="_blank">official guide</a>. 
Ensure you select the correct binaries for your CPU architecture. 
Here are the recommended settings, which have proven effective in real-world use. Commands should be executed in your Terminal:

```bash 
# set to the amount of disk space you wish to use
ipfs config Datastore.StorageMax 10TB
# set to the amount of RAM you wish to use
ipfs config Swarm.ResourceMgr.MaxMemory 16GB
ipfs config Routing.Type 'dhtclient'
ipfs config --json Experimental.OptimisticProvide true
ipfs config --json Routing.AcceleratedDHTClient true
ipfs config Reprovider.Interval --json '"23h"'
```
Set the environment variable <code>GOMEMLIMIT=16GB</code> (choose right amount for your server) before launching the daemon to limit memory usage.

#### Step 1a.2: Configure Trident

For example, if you have your disks at /mnt/disk:

```bash
cd /mnt/disk
mkdir trident
docker pull izihawa/trident:latest
docker run izihawa/trident:latest generate-config /trident > trident/config.yaml
```

Now, `trident/config.yaml` has config for the Trident Server.
If you have done `Step 1a.1` and would like to additionally configure pushing data to IPFS network,
follow [Trident documentation section](https://github.com/izihawa/trident?tab=readme-ov-file#configure-ipfs-sink) on how to add IPFS pushing.
If you would like to configure pushing to S3, follow [Trident documentation section](https://github.com/izihawa/trident?tab=readme-ov-file#configure-s3-sink) on how to add S3 pushing.


#### Step 1a.3: Launch Trident

```bash
docker run -e=RUST_LOG=info -i -t -p 7080:80 -p 11204:11204 -p 4919:4919 -v $(pwd)/trident:/trident izihawa/trident:latest serve --config-path /trident/config.yaml
```

Now you will have Trident Server listening on 7080 port for commands.

#### Step 1a.4: Join the STC replication

Firstly, receive replication token using [Nexus bots](https://t.me/science_nexus4_bot) in Telegram by typing `/seed` there.
Then, add received token into the following command

```bash 
curl -H "Content-Type: application/json" "http://localhost:7080/tables/nexus_science/import/" \
--data '{"ticket": "token", "storage": "default", "download_policy": {"NothingExcept": []}}'
```

Trident will replicate metadata (list of available DOIs) entirely in any case,
but downloading the actual dataset is configured by the download policy and is done on-demand during requests for files via GET requests to Trident.
The example above sets the download policy to NothingExcept, indicating that no files will be downloaded by default.
If you have sufficient disk storage, you may consider changing it to EverythingExcept.
Furthermore, you might want to specify the exact PDFs you wish to replicate by their prefixes.

```json
{"NothingExcept": [{"Prefix": "10.1016/"}]}
```

**Initial import may take a long time!** Leave it alone for a while.

#### Step 1a.5

Try to read file:

```bash 
curl -H "Content-Type: application/json" "http://localhost:7080/tables/nexus_science/10.1016%2fj.scr.2021.102334.pdf/"
```

Congratulations, you have just configured Trident!

### Step 1b: Setting up Iroh replication using official Iroh CLI

ToDo.