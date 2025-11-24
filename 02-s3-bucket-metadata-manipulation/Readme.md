---

# 🌩️ AWS S3 Cloud Storage Optimization Analyzer — README

---

## 🏁 Overview

This project is a **Python-based AWS S3 Metadata Analyzer and Cost Report Generator**.

It allows you to:

* Retrieve S3 bucket metadata (region, size, versioning, tags, last accessed date)
* Inject **dummy data** for testing all conditions
* Calculate estimated storage costs
* Identify **cleanup candidates**, **deletion queue**, and **Glacier archival suggestions**
* Generate **CSV, JSON, and chart outputs**
* Analyze costs by **Region + Department**

This guide assumes you are using **Windows**, but Linux/macOS users can adapt commands.

---

## 🧭 STEP 1 — Prerequisites

| Requirement                     | Purpose                                         |
| ------------------------------- | ----------------------------------------------- |
| AWS Account                     | Access S3 buckets                               |
| IAM User with S3 permissions    | Secure programmatic access                      |
| AWS CLI                         | Authenticate and test connectivity              |
| Python 3.x                      | Run automation scripts                          |
| `boto3`, `pandas`, `matplotlib` | Interact with AWS, process data, visualize cost |

---

## 🪟 STEP 2 — Verify Python Installation

```bash
python --version
pip --version
```

If not installed:

1. Download Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Check **“Add Python to PATH”** during installation

---

## 🧰 STEP 3 — Setup Project Directory

```bash
cd PATH
mkdir AWS_S3_Optimization
cd AWS_S3_Optimization
# Clone my repo
```

---

## 🧱 STEP 4 — Virtual Environment (Recommended)

```bash
python -m venv s3bucket-optimisation
s3bucket-optimisation\Scripts\activate
```

Prompt changes:

```
(venv) PATH>
```

---

## 🧩 STEP 5 — Install Python Libraries

```bash
pip install boto3 pandas matplotlib tabulate
```

Optional (for colored terminal output):

```bash
pip install colorama
```

---

## ☁️ STEP 6 — Install and Configure AWS CLI

### Install AWS CLI

Download latest version: [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/)

Verify:

```bash
aws --version
```

### Configure Credentials

```bash
aws configure
```

Provide:

```
AWS Access Key ID: <YourAccessKey>
AWS Secret Access Key: <YourSecretKey>
Default region name: us-east-1
Default output format: json
```

Verify:

```bash
aws s3 ls
```

---

## 🧑‍💼 STEP 7 — IAM Permissions

Attach this policy to your IAM user:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetBucketVersioning",
                "s3:GetBucketTagging",
                "s3:ListBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

Optional for extended analysis:

* `s3:GetBucketAnalyticsConfiguration`
* `s3:GetBucketMetricsConfiguration`
* `cloudtrail:LookupEvents` (for last accessed date)

---

## 📦 STEP 8 — Test Bucket Setup (Optional)

```bash
aws s3 mb s3://test-bucket-sre-demo
aws s3 cp PATH\testfile.txt s3://test-bucket-sre-demo/
aws s3api put-bucket-tagging --bucket test-bucket-sre-demo --tagging "{\"TagSet\":[{\"Key\":\"Department\",\"Value\":\"Engineering\"}]}"
aws s3api put-bucket-versioning --bucket test-bucket-sre-demo --versioning-configuration Status=Enabled
```

---

## 🧠 STEP 9 — Script Logic Overview

Your **`s3_optimizer.py`** script:

1. Connects via `boto3.client('s3')`

2. Fetches all buckets (AWS + dummy)

3. Retrieves:

   * Region
   * Versioning status
   * Department (from tags)
   * Size (GB)
   * LastAccessed date

4. Applies rules:

   * **Cleanup** → Size >50 GB
   * **Deletion Queue** → Size >100 GB & LastAccessed >20 days
   * **Archive (Glacier)** → GLACIER or DEEP_ARCHIVE
   * **Unused buckets >80GB and >90 days**

5. Calculates costs per bucket and aggregates by **Region + Department**

6. Generates:

   * **CSV** cost report
   * **JSON** full metadata
   * **Chart** per region

---

## 🧾 STEP 10 — Recommended File Structure

```
C:\Users\hp\OneDrive\Desktop\AWS_S3_Optimization
│
├── s3bucket-optimisation\
├── s3_optimizer.py          <-- Main script
└── report_output\           <-- Generated CSV/JSON/Chart
```

---

## ✅ STEP 11 — Run the Script

Activate virtual environment and run:

```bash
python s3_optimizer.py
```

Output:

* Bucket summary printed in terminal
* Cost report CSV: `report_output/s3_cost_report_<timestamp>.csv`
* Metadata JSON: `buckets.json`
* Chart PNG: `report_output/s3_cost_chart_<timestamp>.png`

---

## ⚡ STEP 12 — Interpreting Results

* **Recommendation column**:

  * `"Cleanup suggested"` → Consider cleaning up files
  * `"Add to deletion queue"` → Candidate for deletion
  * `"Consider archival"` → Move to Glacier

* **Deletion Queue**: final list of buckets for potential removal

* **Charts**: visualize estimated costs by AWS region

* **CSV**: can be imported into Excel for further analysis

---

## 🧪 STEP 13 — Testing Dummy Data

Dummy buckets cover:

* Small buckets (<50GB)
* Large buckets (>50GB) → cleanup suggested
* Very large buckets (>100GB, unused >20 days) → deletion queue
* Glacier/Deep Archive → archival recommendations
* Buckets unused >90 days → flagged for special review

You can modify in `s3_optimizer.py` to test more edge cases.

---

## 📝 STEP 14 — Next Steps

1. Enhance reporting (e.g., department-based pie charts)
2. Schedule script via **Windows Task Scheduler** or **cron**
3. Integrate **Slack/email notifications** for deletion queue
4. Expand **cost calculations** using AWS pricing API

---

### 🎯 Summary

This README guides you **end-to-end**:

* Environment setup
* AWS CLI & IAM configuration
* Python dependencies
* Running the S3 metadata analyzer
* Interpreting outputs for **cleanup, deletion, and archival**

---

