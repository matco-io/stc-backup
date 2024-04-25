# Replicate STC

The Standard Template Construct (STC) can be conveniently replicated on your personal computer or server. 
The STC consists of several critical components: dataset, search metadata,
and a web interface with a search engine (referred to as Web STC in subsequent references).

Replicating the search metadata and web interface can enhance your search performance and is covered in other guides. 
Simultaneously, replicating the dataset can convert your computer into a comprehensive, standalone library, and we are going to replicate it.

## Replicating the dataset of books and scholarly publications.

The STC is using a mixed scheme for dataset replication.
Replication between core seeders with higher technical skills is done with [Iroh](https://iroh.computer/docs). Then, these seeders
re-publish the data using any other tools, including IPFS.

### Step 0: Prepare Server

For better performance you should have CoW and reflink-aware filesystem (we are using BTRFS, but ZFS/XFS may also be suitable).
Other file systems are also okay, but you should keep in mind that for 
re-publishing you should use Trident configured to lay out files in a disk directory with the possibility to utilize reflinks internally. 
So check how many files your FS may put in a single directory without degrading.

**Choose only 1a (easy) either 1b (hard) according to your needs and skills**

### Step 1a: Setting up Iroh replication using official Iroh CLI

ToDo.

### Step 1b: Setting up Iroh replication using Trident server

Iroh allows high-performance replication by launching Docker image with the Trident application on the server.
Trident is laying out files in a plain folder, making them available for any further usage,
keep internal records for managing data and allowing to push data further to IPFS (no-copy mode) or S3.

#### Step 1b.1: Configure Trident

For example, if you have your disks at /mnt/disk:

```bash
cd /mnt/disk
mkdir trident
docker pull izihawa/trident:latest
docker run izihawa/trident:latest generate-config /trident > trident/config.yaml
```

Now, `trident/config.yaml` has config for the Trident Server.

#### Step 1b.2: Launch Trident

```bash
docker run -e=RUST_LOG=info -i -t -p 7080:80 -p 11204:11204 -p 4919:4919 -v $(pwd)/trident:/trident izihawa/trident:latest serve --config-path /trident/config.yaml
```

Now you will have Trident Server listening on 7080 port for commands.

#### Step 1b.3: Join the STC replication

Further, you have two options: using internal storage or external storage.

- Internal storage allows you to replicate multiple collections without duplicating if collections are intersected.
- External storage lays out data files on the disk with readable names. It is harder to use with multiple collections but allows you to integrate Trident with any other system that may operate with files on disk. For example, you can seed the same files using IPFS/BitTorrent or set up your own web server that will use these files.

Also, you could configure an important attribute: the download policy.

Collections consist of two parts: metadata and blobs.
Metadata allows you to know what is stored in collections, and blobs are the files themselves.
The download policy defines what blobs should be automatically downloaded by your node.
Metadata takes only about tens of GBs right now, but blobs take up 100TB.

You also can download only things that have particular prefixes in the collection. 
As the DOIs collection has items named after DOIs, you can configure your download policy to download only particular publishers. 
For example: `{"NothingExcept": [{"Prefix": "10.1016/"}]}`.
If you want to download everything and have sufficient disk storage, you can use: `{"EverythingExcept": []}`.
The download policy may be changed later in the `config.yaml` file.

You should receive replication token using [Nexus bots](https://t.me/science_nexus4_bot) in Telegram by typing `/seed` there.
Then, add received token into the following command

#### Step 1b.3.1a: Use internal storage

```bash 
# Internal storage 
curl -H "Content-Type: application/json" "http://localhost:7080/tables/dois/import/" \
--data '{"ticket": "<token>", "download_policy": {"NothingExcept": []}}'
```

#### Step 1b.3.1b: Use external storage

```bash 
# Internal storage 
curl -H "Content-Type: application/json" "http://localhost:7080/tables/dois/import/" \
--data '{"ticket": "<token>", "storage": "default", "download_policy": {"NothingExcept": []}}'
```
**Initial import may take a long time (hours)!** Leave it alone for a while and check for 
```
INFO sync:accept: sync finished sent=0 recv=8606150 t_connect=12.008374125s t_process=6421.649626875s me=<...> peer=<...> namespace=srs6ctvbs6rq6mxp
```
log line in Terminal.

#### Step 1b.4

Try to read file:

```bash 
curl -H "Content-Type: application/json" "http://localhost:7080/tables/dois/10.1016/j.scr.2021.102334.pdf"
```

Congratulations, you have just configured Trident!

#### Step 1b.5. IPFS Configuring and mirroring (optional, only if you have used external storage)

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

Then, startup mirroring

```bash
inotifywait -e move -m --format "%w%f" trident/data/shard0/dois/ | xargs -I{} ipfs add --nocopy --hash=blake3 --pin --chunker=size-1048576 "{}"
```