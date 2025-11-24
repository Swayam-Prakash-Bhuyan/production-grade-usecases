import os, boto3, pandas as pd, matplotlib.pyplot as plt
from datetime import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "buckets.json")
REPORT_DIR = os.path.join(BASE_DIR, "report_output")
os.makedirs(REPORT_DIR, exist_ok=True)

# -------------------------------
# Load existing JSON
# -------------------------------
if os.path.exists(INPUT_FILE):
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"buckets": []}

# -------------------------------
# Fetch AWS S3 Buckets
# -------------------------------
def fetch_aws():
    try:
        s3 = boto3.client("s3")
        aws_list = []
        for b in s3.list_buckets().get("Buckets", []):
            name = b["Name"]
            try:
                region = s3.get_bucket_location(Bucket=name)["LocationConstraint"] or "us-east-1"
                versioning = s3.get_bucket_versioning(Bucket=name).get("Status","Disabled") == "Enabled"
                
                # Calculate size
                size = 0
                paginator = s3.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=name):
                    for obj in page.get("Contents", []):
                        size += obj["Size"]
                
                aws_list.append({
                    "name": name,
                    "region": region,
                    "versioning": versioning,
                    "sizeGB": round(size/1e9, 2)
                })
            except Exception as e:
                print(f"⚠️ Could not process bucket {name}: {e}")
                continue
                
        return aws_list
    except (NoCredentialsError, PartialCredentialsError):
        print("⚠️ AWS credentials not found.")
        return []
    except Exception as e:
        print(f"⚠️ AWS fetch error: {e}")
        return []

aws_buckets = fetch_aws()

# -------------------------------
# Merge AWS info into JSON structure
# -------------------------------
existing_names = {b["name"] for b in data["buckets"]}
for aws_bucket in aws_buckets:
    for b in data["buckets"]:
        if b["name"] == aws_bucket["name"]:
            b["region"] = aws_bucket["region"]
            b["versioning"] = aws_bucket["versioning"]
            b["sizeGB"] = aws_bucket["sizeGB"]
            break
    else:
        # Add new bucket if not present
        data["buckets"].append({
            "name": aws_bucket["name"],
            "region": aws_bucket["region"],
            "createdOn": datetime.now().strftime("%Y-%m-%d"),
            "tags": {},
            "policies": [],
            "versioning": aws_bucket["versioning"],
            "sizeGB": aws_bucket["sizeGB"]
        })

# Save updated JSON
with open(INPUT_FILE, "w") as f:
    json.dump(data, f, indent=4)
print("✅ AWS bucket info merged into JSON successfully!")

# -------------------------------
# Generate Report
# -------------------------------
report_df = pd.json_normalize(data["buckets"])
report_df["createdOn"] = pd.to_datetime(report_df["createdOn"], errors="coerce")
report_df["sizeGB"] = pd.to_numeric(report_df["sizeGB"], errors="coerce")
report_df["versioning"] = report_df["versioning"].astype(bool)

# SINGLE OPTIMAL RECOMMENDATION LOGIC
def get_optimal_recommendation(row):
    """Return single best recommendation based on priority"""
    size = row["sizeGB"] or 0
    age_days = (datetime.now() - (row["createdOn"] or datetime.now())).days
    region = str(row["region"] or "")
    
    # Priority: Delete > Cleanup > Archive > None
    if size > 100 and age_days > 365:
        return "Delete"
    elif size > 50:
        return "Cleanup"
    elif "us" in region.lower() or "eu" in region.lower():
        return "Archive"
    else:
        return "None"

report_df["Recommendation"] = report_df.apply(get_optimal_recommendation, axis=1)
report_df["DeleteQueue"] = report_df["Recommendation"] == "Delete"
report_df["ArchiveGlacier"] = report_df["Recommendation"] == "Archive"

# Cost Calculation
report_df["EstimatedCostUSD"] = report_df["sizeGB"] * 0.023  # example cost

# CSV Export
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
report_df.to_csv(os.path.join(REPORT_DIR,f"s3_report_{ts}.csv"), index=False)

# -------------------------------
# Enhanced Chart with Single Recommendation
# -------------------------------
region_summary = report_df.groupby("region").agg({
    "EstimatedCostUSD": "sum",
    "Recommendation": lambda x: x.mode()[0] if not x.mode().empty else "None"
}).reset_index()

color_map = {"Delete":"red", "Cleanup":"orange", "Archive":"blue", "None":"green"}
region_summary["color"] = region_summary["Recommendation"].map(color_map)

plt.figure(figsize=(18,8))
bars = plt.bar(region_summary["region"], region_summary["EstimatedCostUSD"], 
               color=region_summary["color"])

# Add labels on top
for bar, cost, rec in zip(bars, region_summary["EstimatedCostUSD"], region_summary["Recommendation"]):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height*1.01, 
             f"${cost:,.2f}\n{rec}",
             ha="center", va="bottom", fontsize=10, fontweight="bold")

plt.title("S3 Estimated Cost by Region with Single Optimal Recommendation", fontsize=16)
plt.xlabel("Region", fontsize=14)
plt.ylabel("Estimated Cost (USD)", fontsize=14)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(REPORT_DIR,f"s3_cost_chart_{ts}.png"))
plt.close()

print(f"\n✅ Full report generated with {len(report_df)} buckets analyzed!")
print(f"✅ {len([r for r in report_df['Recommendation'] if r != 'None'])} buckets have recommendations")
print(f"✅ Files saved in: {REPORT_DIR}")
print(f"   - s3_report_{ts}.csv")
print(f"   - s3_cost_chart_{ts}.png") 