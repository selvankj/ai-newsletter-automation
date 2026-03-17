# 🤖 AI Newsletter Automation (Serverless + LLM Powered)

An end-to-end serverless system that automatically curates, summarizes, and delivers a weekly AI newsletter using large language models and real-time data sources.

---
## 🚀 Project Highlights

- Fully automated AI newsletter pipeline (0 manual effort)
- Aggregates 10+ AI sources (news, blogs, research, GitHub)
- Uses AWS Bedrock (Claude) for structured summarization
- Generates production-ready HTML emails
- Sends via AWS SES + archives in S3
- End-to-end runtime: ~10–20 seconds

## 🚀 Overview

Keeping up with AI advancements is time-consuming. This project automates the entire workflow:

* Aggregates AI content from multiple sources
* Uses LLMs to generate structured insights
* Formats into a clean HTML newsletter
* Delivers via email and archives results

**Result:** A fully automated, zero-touch AI news pipeline.

---

## ✨ Key Features

* 📰 Multi-source aggregation (RSS feeds, research papers, blogs)
* 🐙 GitHub trending AI repository extraction
* 🧠 LLM-powered summarization (AWS Bedrock – Claude)
* 📊 Structured JSON output (not just raw text)
* 📧 HTML email generation with multiple sections
* ☁️ Serverless architecture (AWS Lambda)
* 🗄️ Automatic archival to S3
* ⏱️ Fully automated weekly execution

---

## 🏗️ Architecture

![Architecture](architecture.png)

### Pipeline Flow

1. Fetch RSS feeds (AI blogs, news, research)
2. Scrape GitHub trending repositories
3. Aggregate and clean content
4. Send to LLM (Bedrock Claude)
5. Generate structured JSON digest
6. Convert JSON → HTML email
7. Send via AWS SES
8. Archive in S3

---

## 🧠 AI Design

This project demonstrates practical LLM usage beyond simple prompts:

* Prompt engineering for **structured JSON output**
* Multi-source context aggregation
* Post-processing and validation of model output
* Converting AI output into production-ready UI (HTML email)

---

## 📊 Example Output Sections

* 🔥 Top Headlines
* 🛠️ New AI Tools
* 📄 Research Papers (ArXiv)
* 🐙 GitHub Trending
* 📈 Trend of the Week
* 💬 Key Quote

---

## ⚙️ Configuration (Important)

Update these before running:

```python
SENDER = "your-email@example.com"
S3_BUCKET = "your-bucket-name"
SUBSCRIBERS = [...]
```

Recommended (production):

```python
import os
SENDER = os.environ.get("SENDER")
S3_BUCKET = os.environ.get("S3_BUCKET")
```

---

## 🚀 Deployment

### AWS Lambda

1. Zip project
2. Upload to Lambda
3. Set handler:

```
lambda_function.lambda_handler
```

4. Add permissions:

* S3
* SES
* Bedrock

---

## 📸 Sample Output

![AI Newsletter](newsletter-sample.png)

### Schedule (Weekly)

Use EventBridge:

```
cron(0 9 ? * MON *)
```

---

## 📈 Performance

* Processes ~30–50 articles per run
* Generates newsletter in ~10–20 seconds
* Fully automated weekly pipeline

---

## 💡 Why This Project Matters

This system reduces hours of manual research into a fully automated pipeline.
It demonstrates how LLMs can be integrated into real-world workflows — not just demos.

---

## 🔧 Future Improvements

* Subscriber management (DynamoDB)
* Personalization using embeddings
* Web dashboard for archive browsing
* CI/CD deployment (Terraform / CDK)

---

## 🧑‍💻 Author

Built by Selvankj

---

## ⭐ If you found this useful

Star the repo and feel free to fork!
