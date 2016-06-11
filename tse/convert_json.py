import csv
import json

f = open("cand_2014.csv")
reader = csv.DictReader(f, delimiter=";")
out = "\n".join(json.dumps(t, encoding="latin1") for t in reader)
f.close()
f = open("tse_2014.json", 'w')
f.write(out)
f.close()
