#!/usr/bin/env python3
import os
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ACCOUNT_ID = os.environ["ACCOUNT_ID"]
API_KEY = os.environ["API_KEY"]

url = f"https://api.pluggy.ai/transactions?accountId={ACCOUNT_ID}"
headers = {
    "accept": "application/json",
    "X-API-KEY": API_KEY,
}

log.info("first for metadata...")
first_response = requests.get(url, headers=headers)
first_json = first_response.json()
transactions = []
page, total_pages = first_json["page"], first_json["totalPages"]
log.info("page: %d, total: %d, full: %d", page, total_pages, first_json["total"])
transactions.extend(first_json["results"])
for page in range(page + 1, total_pages + 1):
    log.info("%d", page)
    response = requests.get(url, headers=headers, params={"page": page})
    rjson = response.json()
    assert rjson["page"] == page
    transactions.extend(rjson["results"])

print(json.dumps(transactions))
