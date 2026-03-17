import boto3, json, feedparser, datetime, urllib.request, html

REGION    = 'ap-south-1'  # 🔴 CHANGE if needed
S3_BUCKET = 'ai-newsletter-archive-XYZ' # 🔴 CHANGE
SENDER    = 'sender@youremail.com'  # 🔴 CHANGE (must be SES verified)
MODEL_ID  = 'anthropic.claude-haiku-20240307-v1:0'

SUBSCRIBERS = [
    {"email": "receiver@youremail.com", "name": "Receiver"}, # 🔴 CHANGE
]

RSS_FEEDS = [
    'https://techcrunch.com/category/artificial-intelligence/feed/',
    'https://venturebeat.com/category/ai/feed/',
    'https://www.technologyreview.com/feed/',
    'https://openai.com/blog/rss.xml',
    'https://www.anthropic.com/rss.xml',
    'https://huggingface.co/blog/feed.xml',
    'https://bair.berkeley.edu/blog/feed.xml',
    'https://deepmind.google/blog/rss.xml',
    'https://blogs.microsoft.com/ai/feed/',
    'https://www.microsoft.com/en-us/research/blog/feed/',
    'https://ai.meta.com/blog/rss/',
    'https://blog.google/technology/ai/rss/',
    'https://export.arxiv.org/rss/cs.AI',
    'https://export.arxiv.org/rss/cs.LG',
]

def fetch_rss_content():
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                articles.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', '')[:300],
                    'link': entry.get('link', ''),
                    'source': feed.feed.get('title', url)
                })
        except Exception as e:
            print(f"Feed error {url}: {e}")
    return articles

def fetch_github_trending():
    articles = []
    try:
        req = urllib.request.Request(
            'https://github.com/trending?since=weekly&spoken_language_code=en',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('utf-8')
        import re
        repos = re.findall(r'href="/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"', content)
        descs = re.findall(r'<p class="col-9 color-fg-muted my-1 pr-4">\s*(.+?)\s*</p>', content)
        seen = []
        for repo in repos:
            if repo not in seen and 'trending' not in repo:
                seen.append(repo)
        for i, repo in enumerate(seen[:5]):
            desc = html.unescape(descs[i]) if i < len(descs) else 'Trending AI/ML repository'
            articles.append({
                'title': f'GitHub Trending: {repo}',
                'summary': desc[:300],
                'link': f'https://github.com/{repo}',
                'source': 'GitHub Trending'
            })
    except Exception as e:
        print(f"GitHub trending error: {e}")
    return articles

def summarize_with_bedrock(articles):
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    prompt = f"""You are an AI newsletter curator. Given these articles, create a weekly digest.
Return ONLY valid JSON in this exact format with no extra text or markdown:
{{
  "subject": "newsletter subject line",
  "top_headlines": [{{"title": "...", "summary": "2-3 sentence summary", "link": "..."}}],
  "new_tools": [{{"name": "...", "description": "what it does and why it matters"}}],
  "arxiv_papers": [{{"title": "...", "insight": "why this research matters in plain English"}}],
  "github_trending": [{{"repo": "...", "description": "...", "link": "..."}}],
  "key_quote": {{"quote": "...", "attribution": "Person, Company"}},
  "trend_of_week": {{"title": "...", "insight": "2-3 sentences"}}
}}
Articles:
{json.dumps(articles, indent=2)[:10000]}"""

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    result = json.loads(response['body'].read())
    raw = result['content'][0]['text'].strip()
    if raw.startswith('```'):
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
    return json.loads(raw.strip())

def build_html_email(digest, date_str):
    headlines_html = ''.join([
        f'<div style="margin-bottom:16px;"><a href="{h["link"]}" style="font-size:15px;font-weight:500;color:#0066cc;">{h["title"]}</a><p style="font-size:13px;color:#555;margin-top:4px;">{h["summary"]}</p></div>'
        for h in digest.get('top_headlines', [])
    ])
    tools_html = ''.join([
        f'<div style="margin-bottom:12px;"><strong>{t["name"]}</strong><p style="font-size:13px;color:#555;margin-top:4px;">{t["description"]}</p></div>'
        for t in digest.get('new_tools', [])
    ])
    papers_html = ''.join([
        f'<div style="margin-bottom:12px;"><strong>{p["title"]}</strong><p style="font-size:13px;color:#555;margin-top:4px;">{p["insight"]}</p></div>'
        for p in digest.get('arxiv_papers', [])
    ])
    github_html = ''.join([
        f'<div style="margin-bottom:12px;"><a href="{g["link"]}" style="font-size:14px;font-weight:500;color:#0066cc;">{g["repo"]}</a><p style="font-size:13px;color:#555;margin-top:4px;">{g["description"]}</p></div>'
        for g in digest.get('github_trending', [])
    ])
    quote = digest.get('key_quote', {})
    trend = digest.get('trend_of_week', {})

    return f"""<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
<h1 style="color:#111;font-size:22px;border-bottom:2px solid #eee;padding-bottom:12px;">AI Weekly — {date_str}</h1>

<h2 style="font-size:16px;color:#333;margin-top:24px;">🔥 Top Headlines</h2>
{headlines_html}

<h2 style="font-size:16px;color:#333;margin-top:24px;">🛠️ New AI Tools</h2>
{tools_html}

<h2 style="font-size:16px;color:#333;margin-top:24px;">📄 Research Papers (ArXiv)</h2>
{papers_html}

<h2 style="font-size:16px;color:#333;margin-top:24px;">🐙 GitHub Trending</h2>
{github_html}

<div style="background:#f8f8f8;padding:16px;border-left:3px solid #0066cc;margin:24px 0;">
  <p style="font-style:italic;font-size:14px;">"{quote.get('quote','')}"</p>
  <p style="font-size:12px;color:#777;margin-top:8px;">— {quote.get('attribution','')}</p>
</div>

<h2 style="font-size:16px;color:#333;">📈 Trend of the Week</h2>
<p style="font-size:14px;font-weight:500;">{trend.get('title','')}</p>
<p style="font-size:13px;color:#555;">{trend.get('insight','')}</p>

<hr style="margin-top:32px;border:none;border-top:1px solid #eee;">
<p style="font-size:11px;color:#aaa;text-align:center;">AI Weekly Newsletter</p>
</body></html>"""

def send_emails(html_body, subject):
    ses = boto3.client('ses', region_name=REGION)
    sent, failed = 0, 0
    for sub in SUBSCRIBERS:
        try:
            ses.send_email(
                Source=SENDER,
                Destination={'ToAddresses': [sub['email']]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Html': {'Data': html_body}}
                }
            )
            print(f"Sent to {sub['name']} ({sub['email']})")
            sent += 1
        except Exception as e:
            print(f"Failed {sub['email']}: {e}")
            failed += 1
    return sent, failed

def lambda_handler(event, context):
    date_str = datetime.datetime.now().strftime('%B %d, %Y')
    file_key = f"newsletters/{datetime.datetime.now().strftime('%Y-%m-%d')}.html"

    print("Fetching RSS feeds...")
    articles = fetch_rss_content()

    print("Fetching GitHub trending...")
    articles += fetch_github_trending()

    print(f"Got {len(articles)} total articles. Calling Bedrock...")
    digest = summarize_with_bedrock(articles)
    print("Bedrock done. Building HTML...")

    html = build_html_email(digest, date_str)

    print("Archiving to S3...")
    boto3.client('s3', region_name=REGION).put_object(
        Bucket=S3_BUCKET, Key=file_key,
        Body=html.encode('utf-8'), ContentType='text/html'
    )

    print("Sending emails...")
    sent, failed = send_emails(html, digest.get('subject', f'AI Weekly — {date_str}'))
    print(f"Done. Sent: {sent}, Failed: {failed}")

    return {"statusCode": 200, "sent": sent, "failed": failed, "archive": file_key}