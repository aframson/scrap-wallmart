import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_latest_news(base_url="https://yen.com.gh"):
    response = requests.get(base_url + "/latest/")
    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")

    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    print(f"{'Title':<80} | {'Posted':<20} | {'Link'}")
    print("-" * 150)

    for article in articles:
        # Extract title
        headline_tag = article.find("a", class_="c-article-card-no-border__headline") or \
                       article.find("a", class_="c-article-card-horizontal__headline")
        if not headline_tag:
            continue
        title = headline_tag.get_text(strip=True)

        # Extract link
        link = headline_tag.get("href")
        full_link = link if link.startswith("http") else base_url + link

        # Extract time
        time_tag = article.find("time")
        if time_tag and time_tag.has_attr("datetime"):
            try:
                post_time = datetime.strptime(time_tag["datetime"], "%Y-%m-%dT%H:%M:%SZ")
                if post_time > one_hour_ago:
                    print(f"{title[:78]:<80} | {post_time.strftime('%Y-%m-%d %H:%M')} | {full_link}")
            except Exception as e:
                continue

if __name__ == "__main__":
    get_latest_news()