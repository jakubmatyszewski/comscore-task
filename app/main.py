#!/usr/bin/env python3

import argparse
import json
import logging
import sys

import requests

log = logging.getLogger(__name__)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


def recreate_index(elasticsearch_url: str, index: str) -> None:
    log.info("cleaning old index...")
    out = requests.delete(f"{elasticsearch_url}/{index}")
    log.info(out)
    log.info(out.json())
    log.info("OK")

    log.info("creaing new index...")
    out = requests.put(f"{elasticsearch_url}/{index}")
    out.raise_for_status()
    log.info(out)
    log.info(out.json())
    log.info("OK")


def transform(
    elasticsearch_url: str, index_from: str, index_to: str, size: int
) -> None:
    recreate_index(elasticsearch_url, index_to)

    for x in batch(range(size), 1000):
        docs = []
        data = json.dumps({"ids": [str(y) for y in x]})
        resp = requests.get(
            f"{elasticsearch_url}/{index_from}/_mget",
            data=data,
            headers={"content-type": "application/json"},
        )
        for doc in resp.json()["docs"]:
            docs.append(
                '{"index": {"_index": "' + index_to + '", "_id": "' + doc["_id"] + '"}}'
                ""
            )
            doc["_source"]["calculated"] = [
                len(str(k) + str(v)) for k, v in doc["_source"].items()
            ][0]
            docs.append(json.dumps(doc["_source"]))
        data = "\n".join(docs)
        data += "\n"
        resp = requests.post(
            f"{elasticsearch_url}/{index_to}/_bulk",
            data=data,
            headers={"content-type": "application/json"},
        )
        resp.raise_for_status()
    log.info(f"Transformed index {index_from} to new index {index_to}.")


def main(args=sys.argv[1:]):
    logging.basicConfig(handlers=[logging.StreamHandler()])
    log.setLevel(logging.WARNING)
    ap = argparse.ArgumentParser(description="Transforms index")
    ap.add_argument("--elasticsearch-url", type=str)
    ap.add_argument("--index_from", type=str)
    ap.add_argument("--index_to", type=str)
    args = ap.parse_args(args)
    log.info("parameters: %s", args)

    transform(args.elasticsearch_url, args.index_from, args.index_to, 1_000_000)


if __name__ == "__main__":
    main()
