#!/usr/bin/env python3
import calendar
import os
import decimal
import datetime
import collections
import json
import pprint
import sys

from config_map import MAP

NEGATIVE = os.environ.get("NEGATIVE") == "1"

with open(sys.argv[1], "r") as fd:
    data = json.load(fd, parse_float=decimal.Decimal)

start_date_str = [int(x) for x in sys.argv[2].split("-")]
try:
    end_date_str = [int(x) for x in sys.argv[3].split("-")]
except IndexError:
    end_date_str = None

start_date = datetime.datetime(
    year=start_date_str[0],
    month=start_date_str[1],
    day=start_date_str[2],
    tzinfo=datetime.timezone.utc,
)
if end_date_str is not None:
    end_date = datetime.datetime(
        year=end_date_str[0],
        month=end_date_str[1],
        day=end_date_str[2],
        hour=23,
        minute=59,
        second=59,
        tzinfo=datetime.timezone.utc,
    )
else:
    end_date = datetime.datetime(
        start_date.year,
        start_date.month,
        calendar.monthrange(start_date.year, start_date.month)[1],
        23,
        59,
        59,
        tzinfo=datetime.timezone.utc,
    )
print("from", start_date, "to", end_date, file=sys.stderr)


transactions = {}
currencies = collections.defaultdict(lambda: collections.Counter())
transactions_by_tag = collections.defaultdict(lambda: list())


for transaction in data:
    date = datetime.datetime.fromisoformat(transaction["date"])
    if date < start_date:
        continue
    if date > end_date:
        continue

    if NEGATIVE:
        transaction["amount"] = -transaction["amount"]

    if transaction["amount"] < 0:
        continue

    transaction["tags"] = set()
    for match_data, tag in MAP.items():
        payment_data = transaction.get("paymentData") or {}
        payer = payment_data.get("payer") or {}
        receiver = payment_data.get("receiver") or {}
        document_number_payer = (payer.get("documentNumber") or {}).get("value") or ""
        document_number_receiver = (receiver.get("documentNumber") or {}).get(
            "value"
        ) or ""

        if isinstance(match_data, tuple):
            date_query, match = match_data
            if date_query[0] == "account":
                account_id = date_query[1]
                if transaction["accountId"] != account_id:
                    continue
            else:
                if not transaction["date"].startswith(date_query):
                    continue
        else:
            match = match_data

        if match in transaction["description"].lower():
            transaction["tags"].add(tag)
        if match in (transaction.get("merchant") or {}).get("businessName", "").lower():
            transaction["tags"].add(tag)

        if match in document_number_payer:
            transaction["tags"].add(tag)
        if match in document_number_receiver:
            transaction["tags"].add(tag)

        # only match on proper uuid
        if "-" in match and match in transaction["id"]:
            transaction["tags"].add(tag)
    transactions[transaction["id"]] = transaction
    for tag in transaction["tags"]:
        transactions_by_tag[tag].append(transaction)

print(len(transactions), "transactions", file=sys.stderr)
for transaction in transactions.values():
    if not transaction["tags"]:
        transaction["tags"].add("other")
        transactions_by_tag["other"].append(transaction)
    for tag in transaction["tags"]:
        currencies[transaction["currencyCode"]][tag] += decimal.Decimal(
            transaction["amount"]
        )

condensed = collections.Counter()
for currency, counter in currencies.items():
    print(currency, file=sys.stderr)
    pprint.pprint(counter.most_common(100), stream=sys.stderr)
    for tag in counter:
        condensed[tag] += counter[tag]

for tag, value in condensed.most_common():
    print(f"{start_date.year}-{start_date.month},{tag},{value}")


sys.stderr.flush()
print(len(transactions_by_tag["other"]), "as other", file=sys.stderr)
for transaction in transactions_by_tag["other"][:10]:
    pprint.pprint(transaction, stream=sys.stderr)
