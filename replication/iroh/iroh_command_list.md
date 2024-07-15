```bash
curl -fsSL https://sh.iroh.computer/install.sh | sh
echo 'export IROH_DATA_DIR=./' >> $HOME/.bashrc
iroh console --start
```

now on Iroh's console create a new author

```
author new --switch
```
Then join the ticket (data) you want to sync:

```
doc join --switch docaaazizpbj2qzpiypglxuuou2hcnnhdkbzgcs5hciqnnxnp7uk5dekpabuvnmlzmtiw3z3gzski2rc6w3iw3nqbvotewswygdz7i5rpdaxbeaaaa
```
Still on Iroh's console, check connections:

```
node connections
```

Check for doc keys (keys have hashes that point to a blob of data as values)

```
doc keys -m content
```

If the document is synced it should return *something*.

You can use `doc watch` to track events but it will block the console's IO:

```
doc watch
```

Now to check your connection with the node you've synced you can start another terminal and do:

```
iroh node connections
```

Iroh's data go to `IROH_DATA_DIR`. To check the Iroh's folder

```
cd $IROH_DATA_DIR
find . | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/"
```