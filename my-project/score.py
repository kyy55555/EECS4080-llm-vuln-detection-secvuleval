import json
import os
import pandas as pd

key = pd.read_csv("blind_key.csv")
results_dir = os.path.join("..", "blind-run", "results")

predictions = []
for sample in key["sample"]:
    name = sample.replace(".c", ".json")
    with open(os.path.join(results_dir, name)) as f:
        answer = json.load(f)
    predictions.append(answer["is_vulnerable"])

key["predicted"] = predictions
key["actual"] = key["label"] == "vulnerable"

tp = ((key["predicted"] == True) & (key["actual"] == True)).sum()
fp = ((key["predicted"] == True) & (key["actual"] == False)).sum()
fn = ((key["predicted"] == False) & (key["actual"] == True)).sum()
tn = ((key["predicted"] == False) & (key["actual"] == False)).sum()

precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * precision * recall / (precision + recall)

print("TP:", tp, "FP:", fp, "FN:", fn, "TN:", tn)
print(f"Precision: {precision:.2%}")
print(f"Recall:    {recall:.2%}")
print(f"F1:        {f1:.2%}")

key.to_csv("function_level_results.csv", index=False)