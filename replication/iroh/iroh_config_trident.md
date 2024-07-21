
cd <TRIDENT_MOUNTPOINT>
mkdir trident
sudo systemctl start docker
sudo docker pull izihawa/trident:latest
sudo docker run izihawa/trident:latest generate-config /trident > trident/config.yaml
sudo docker run -e=RUST_LOG=info -i -t -p 7080:80 -p 11204:11204 -p 4919:4919 -v $(pwd)/trident:/trident izihawa/trident:latest serve --config-path /trident/config.yaml
curl -H "Content-Type: application/json" "http://localhost:7080/tables/dois/import/" \
--data '{"ticket": "docaaazizpbj2qzpiypglxuuou2hcnnhdkbzgcs5hciqnnxnp7uk5dekpabuvnmlzmtiw3z3gzski2rc6w3iw3nqbvotewswygdz7i5rpdaxbeaaaa", "storage": "default", "download_policy": {"NothingExcept": [{"Prefix": "10.1016/"}]}'

curl -H "Content-Type: application/json" "http://localhost:7080/tables/dois/import/" \
--data '{"ticket": "docaaazizpbj2qzpiypglxuuou2hcnnhdkbzgcs5hciqnnxnp7uk5dekpabuvnmlzmtiw3z3gzski2rc6w3iw3nqbvotewswygdz7i5rpdaxbeaaaa", "storage": "default", "download_policy": {"EverythingExcept": []}}'


curl -H "Content-Type: application/json" "http://localhost:7080/tables/dois/import/" \
--data '{"ticket": "docaaazizpbj2qzpiypglxuuou2hcnnhdkbzgcs5hciqnnxnp7uk5dekpabuvnmlzmtiw3z3gzski2rc6w3iw3nqbvotewswygdz7i5rpdaxbeaaaa", "storage": "default", "download_policy": {"NothingExcept": [{"Prefix": "10.1016/"}]}'