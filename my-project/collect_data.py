from datasets import load_dataset
import pandas as pd

df = load_dataset("arag0rn/SecVulEval")["train"].to_pandas()
linux = df[df["project"] == "linux"]
vuln = linux[linux["is_vulnerable"] == True].sort_values("idx")

all_cves = []
for cves in vuln["cve_list"]:
    cve = ";".join(cves)
    if cve not in all_cves:
        all_cves.append(cve)
print("All Linux CVEs:", len(all_cves))

def cve_number(cve):
    first = cve.split(";")[0]
    parts = first.split("-")
    return (int(parts[1]), int(parts[2]))

newest = sorted(all_cves, key=cve_number, reverse=True)[:100]
print("Newest 5:", newest[:5])
print("Last 5 of the 100:", newest[-5:])

keys = []
for cves in vuln["cve_list"]:
    keys.append(";".join(cves))
vuln = vuln.copy()
vuln["cve"] = keys

picked = vuln[vuln["cve"].isin(newest)]
print("Rows picked:", len(picked))
print(picked["cve"].value_counts().head(5))

body_by_idx = dict(zip(df["idx"], df["func_body"]))

picked = picked.copy()
fixed = []
missing = 0
for i in picked["fixed_func_idx"]:
    if pd.isna(i):
        fixed.append("")
        missing += 1
    else:
        fixed.append(body_by_idx[i])
picked["fixed_func_body"] = fixed
print("No fixed version:", missing)
cwes = []
for c in picked["cwe_list"]:
    cwes.append(";".join(c))
picked["cwe"] = cwes

columns = ["cve", "cwe", "idx", "filepath", "func_name", "commit_id",
           "changed_lines", "func_body", "fixed_func_body"]
picked[columns].to_csv("secvuleval_linux_newest100.csv", index=False)
print("Saved", len(picked), "rows")

per_cve = picked.groupby("cve", sort=False).agg(
    cwe=("cwe", "first"),
    n_functions=("func_name", "count"),
    functions=("func_name", "; ".join),
    files=("filepath", lambda s: "; ".join(sorted(set(s)))),
)
per_cve.to_csv("secvuleval_linux_newest100_by_cve.csv")
print("CVEs:", len(per_cve))
print(per_cve["cwe"].value_counts())