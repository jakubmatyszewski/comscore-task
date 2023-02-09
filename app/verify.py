#!/usr/bin/env python3

import logging
import requests

ES7_URL="http://es_7:9200"
ES7_INDEX="my-index"
ES7_INDEX_TRANSFORMED="my-index-2"

log = logging.getLogger(__name__)


def test_document_count():
    resp = requests.get(f"{ES7_URL}/{ES7_INDEX}/_search?size=1000")
    resp.raise_for_status()
    log.info(resp.json())
    assert len(resp.json()['hits']['hits']) == 1000

def test_document_transformation():
    resp = requests.get(f"{ES7_URL}/{ES7_INDEX_TRANSFORMED}/_search?size=10")
    resp.raise_for_status()
    log.info(resp.json())
    for doc in resp.json()['hits']['hits']:
        log.info("document: %s", doc)
        assert doc['_source']['calculated'] == 20
