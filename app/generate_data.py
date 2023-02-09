#!/usr/bin/env python3

import sys
import logging
import argparse


import json
import requests


log = logging.getLogger(__name__)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def generate_docs(elasticsearch_url, index, size):
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

    log.info("generating documents...")
    for _ in batch(range(size), 1000):
        docs = []
        for x in _:
            docs.append('{"index": {"_index": "'+index+'", "_id": "'+str(x)+'"}}''')
            docs.append(json.dumps(dict(
                document_number=str(x),
                # calculated=21
            )))
        data = "\n".join(docs)
        data += '\n'
        print(data)
        resp = requests.post(f"{elasticsearch_url}/{index}/_bulk", data=data,
                headers={'content-type': 'application/json'})
        resp.raise_for_status()
    log.info("documents generated.")


def main(args=sys.argv[1:]):
    logging.basicConfig(handlers=[logging.StreamHandler()])
    log.setLevel(logging.INFO)
    ap = argparse.ArgumentParser(description="Recreates index (delete and create) and push data into it")
    ap.add_argument('--elasticsearch-url', type=str)
    ap.add_argument('--index', type=str)
    args = ap.parse_args(args)
    log.info("parameters: %s", args)

    generate_docs(args.elasticsearch_url, args.index, 1_000_000)


if __name__ == '__main__':
    main()

