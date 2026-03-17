"""
新闻资讯获取模块
"""
import os
import re
import requests
import feedparser
from typing import Dict, List
from datetime import datetime
from html import unescape


class NewsFetcher:
    """新闻资讯获取器"""

    def __init__(self, api_key: str = None):
        self.newsapi_key = api_key or os.getenv("NEWSAPI_KEY")

    def fetch_from_rss(self, url: str, source_name: str, max_items: int = 3) -> List[Dict]:
        """从RSS源获取新闻"""
        try:
            feed = feedparser.parse(url)
            news_items = []

            for entry in feed.entries[:max_items]:
                # 清理HTML标签
                title = re.sub(r'<[^>]+>', '', entry.get('title', ''))
                title = unescape(title)

                # 获取发布时间
                published = entry.get('published', '')
                if not published:
                    published = datetime.now().strftime("%m-%d")
                else:
                    # 简化日期格式
                    published = self._format_date(published)

                news_items.append({
                    "title": title,
                    "source": source_name,
                    "published": published,
                    "url": entry.get('link', '')
                })

            return news_items
        except Exception as e:
            print(f"RSS获取失败 {source_name}: {e}")
            return []

    def _format_date(self, date_str: str) -> str:
        """格式化日期为 MM-DD"""
        try:
            # 尝试解析常见格式
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dt = datetime.strptime(date_str[:19], fmt[:19])
                    return dt.strftime("%m-%d")
                except:
                    continue
            return datetime.now().strftime("%m-%d")
        except:
            return datetime.now().strftime("%m-%d")

    def fetch_cailianshe(self) -> List[Dict]:
        """获取财联社新闻 - 使用 RSSHub"""
        url = "https://rsshub.app/cls/telegraph"
        return self.fetch_from_rss(url, "财联社", max_items=3)

    def fetch_techcrunch(self) -> List[Dict]:
        """获取 TechCrunch 科技新闻"""
        url = "https://techcrunch.com/feed/"
        return self.fetch_from_rss(url, "TechCrunch", max_items=2)

    def fetch_the_verge(self) -> List[Dict]:
        """获取 The Verge 科技新闻"""
        url = "https://www.theverge.com/rss/index.xml"
        return self.fetch_from_rss(url, "The Verge", max_items=2)

    def fetch_wallstreetcn(self) -> List[Dict]:
        """获取华尔街见闻新闻 - 使用 RSS 源"""
        # 华尔街见闻实时快讯 RSS
        url = "https://rsshub.app/wallstreetcn/live"
        return self.fetch_from_rss(url, "华尔街见闻", max_items=3)

    def fetch_36kr(self) -> List[Dict]:
        """获取36氪新闻 - 使用 RSSHub"""
        url = "https://rsshub.app/36kr/newsflashes"
        return self.fetch_from_rss(url, "36氪", max_items=3)

    def fetch_newsapi(self, query: str = "finance") -> List[Dict]:
        """使用 NewsAPI 获取新闻"""
        if not self.newsapi_key:
            return []

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": self.newsapi_key,
            "category": "business",
            "language": "zh",
            "pageSize": 5
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            items = []

            for article in data.get("articles", [])[:3]:
                items.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "published": article.get("publishedAt", "")[5:10] if article.get("publishedAt") else "",
                    "url": article.get("url", "")
                })
            return items
        except Exception as e:
            print(f"NewsAPI获取失败: {e}")
            return []

    def get_all_news(self, max_items: int = 5) -> List[Dict]:
        """获取所有新闻源"""
        all_news = []

        # 尝试多个数据源（按优先级排序）
        sources = [
            ("财联社", self.fetch_cailianshe),
            ("华尔街见闻", self.fetch_wallstreetcn),
            ("36氪", self.fetch_36kr),
            ("TechCrunch", self.fetch_techcrunch),
            ("The Verge", self.fetch_the_verge),
            ("NewsAPI", self.fetch_newsapi),
        ]

        for name, fetch_func in sources:
            try:
                news = fetch_func()
                if news:
                    print(f"  ✅ {name}: {len(news)}条")
                    all_news.extend(news)
                else:
                    print(f"  ⚠️ {name}: 无数据")
            except Exception as e:
                print(f"  ❌ {name}: {e}")

        # 去重并限制数量
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title = item.get("title", "").strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)

        return unique_news[:max_items]
