#!/usr/bin/env fish
echo "month,category,amount" > files/credit_reports.csv
for n in (seq 1 12)
    python3 ./process.py ./files/credit_card_transactions.json 2023-$n-01 >> files/credit_reports.csv
end
echo "month,category,amount" > files/checking_reports.csv
for n in (seq 1 12)
    env NEGATIVE=1 python3 ./process.py ./files/checking_account_transactions.json 2023-$n-01 >> files/checking_reports.csv
end
