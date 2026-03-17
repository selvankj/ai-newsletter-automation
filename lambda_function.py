import boto3, json, feedparser, datetime, urllib.request, html

REGION    = 'ap-south-1'  # 🔴 CHANGE if needed
S3_BUCKET = 'your-bucket-name'  # 🔴 CHANGE
SENDER    = 'your-email@example.com'  # 🔴 CHANGE (must be SES verified)
MODEL_ID  = 'anthropic.claude-haiku-20240307-v1:0'

SUBSCRIBERS = [
    {"email": "receiver@email.com", "name": "Receiver Name"},  # 🔴 CHANGE
]

RSS_FEEDS = [
    'https://techcrunch.com/category/artificial-intelligence/feed/',
    'https://venturebeat.com/category/ai/feed/',
    'https://www.technologyreview.com/feed/',
]

def fetch_rss_content():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            articles.append({
                'title': entry.get('title', ''),
                'summary': entry.get('summary', '')[:300],
                'link': entry.get('link', ''),
                'source': feed.feed.get('title', url)
            })
    return articles

def summarize_with_bedrock(articles):
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    prompt = f"Summarize these articles into a short AI newsletter: {json.dumps(articles)[:5000]}"

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        })
    )

    result = json.loads(response['body'].read())
    return result['content'][0]['text']

def lambda_handler(event, context):
    articles = fetch_rss_content()
    summary = summarize_with_bedrock(articles)

    html = f"<html><body><h1>AI Newsletter</h1><p>{summary}</p></body></html>"

    boto3.client('s3').put_object(
        Bucket=S3_BUCKET,
        Key='newsletter.html',
        Body=html.encode('utf-8'),
        ContentType='text/html'
    )

    return {"statusCode": 200}
