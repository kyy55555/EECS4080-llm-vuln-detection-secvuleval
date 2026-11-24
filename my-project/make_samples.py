import os
import random
import pandas as pd

data = pd.read_csv("secvuleval_linux_newest100.csv")

items = []
for _, row in data.iterrows():
    items.append({"code": row["func_body"], "label": "vulnerable",
                  "cve": row["cve"], "cwe": row["cwe"],
                  "func_name": row["func_name"], "idx": row["idx"]})
    if isinstance(row["fixed_func_body"], str) and row["fixed_func_body"] != "":
        items.append({"code": row["fixed_func_body"], "label": "fixed",
                      "cve": row["cve"], "cwe": row["cwe"],
                      "func_name": row["func_name"], "idx": row["idx"]})

random.seed(4080)
random.shuffle(items)

out_dir = os.path.join("..", "blind-run", "samples")
os.makedirs(out_dir, exist_ok=True)

key_rows = []
for n, item in enumerate(items, start=1):
    name = f"s{n:03d}.c"
    with open(os.path.join(out_dir, name), "w") as f:
        f.write(item["code"])
    key_rows.append({"sample": name, "label": item["label"], "cve": item["cve"],
                     "cwe": item["cwe"], "func_name": item["func_name"], "idx": item["idx"]})

key = pd.DataFrame(key_rows)
key.to_csv("blind_key.csv", index=False)
print("Wrote", len(items), "samples")
print(key["label"].value_counts())