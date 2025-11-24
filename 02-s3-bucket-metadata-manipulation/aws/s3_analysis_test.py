# Certainly this one is something 
# I tested while creating the actual file and it's 
# the goto one for low level testing and if you don't need csv or charts

import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
buckets = s3.list_buckets().get("Buckets", [])

def cost_optimisation(buckets):
    for bucket in buckets:
        name = bucket["Name"]
        region = s3.get_bucket_location(Bucket=name)["LocationConstraint"] or "us-east-1"
        versioning = s3.get_bucket_versioning(Bucket=name).get("Status","Disabled") == "Enabled"
        size = 0
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=name):
            for obj in page.get("Contents", []):
                size += obj["Size"]
        size_gb = size / (1024 ** 3)
        days_unused = None
        try:
            response = s3.list_objects_v2(Bucket=name)
            if "Contents" in response:
                last_modified = max(obj["LastModified"] for obj in response["Contents"])
                days_unused = (datetime.now(timezone.utc) - last_modified).days
            else:
                days_unused = (datetime.now(timezone.utc) - bucket["CreationDate"]).days
        except Exception as e:
            print(f"⚠️ Could not determine last used date for bucket {name}: {e}")
        print(f"Bucket: {name}\n")
        print(f"Region: {region}\n")
        print(f"Size (GB): {size_gb}\n")
        print(f"Versioning Enabled: {versioning}\n")
        print(f"Days Unused: {days_unused}\n")
        if size_gb > 50:
            print("Cleanup Recommendation: Consider archiving or deleting old data to reduce costs.\n")
        elif size_gb > 100 and days_unused > 20:
            print("Archival Recommendation: Move data to Glacier or Deep Archive for cost savings.\n")
if __name__ == "__main__":
    cost_optimisation(buckets)