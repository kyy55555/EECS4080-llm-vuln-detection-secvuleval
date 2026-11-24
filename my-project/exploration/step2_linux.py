from datasets import load_dataset

df = load_dataset("arag0rn/SecVulEval")["train"].to_pandas()

linux = df[df["project"] == "linux"]
print("Linux rows:", len(linux))
print(linux["is_vulnerable"].value_counts())

vuln = linux[linux["is_vulnerable"] == True]
row = vuln.iloc[0]
print("CVE:", row["cve_list"])
print("CWE:", row["cwe_list"])
print("File:", row["filepath"])
print("Function:", row["func_name"])
print("Changed lines:", row["changed_lines"])