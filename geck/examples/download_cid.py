import argparse
import asyncio

from libstc_geck.advices import format_document
from libstc_geck.client import StcGeck

DEFAULT_LIMIT = 5


async def main(limit: int):
    geck = StcGeck(
        ipfs_http_base_url='http://127.0.0.1:8080',
        timeout=300,
    )

    await geck.start()
    print("started downloading from CID")
    downloaded = await geck.download("bafyb4iadbza7ckc3djc2k5lfaorwaufcjurzxzkjsj5e7qt2wrguqs7ywm")
    print("finished downloading from CID")
    print(type(downloaded))
    await geck.stop()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--limit', type=int, default=DEFAULT_LIMIT)
    args = argparser.parse_args()

    asyncio.run(main(args.limit))
