import requests
from bs4 import BeautifulSoup
import feedparser
import asyncio
import httpx
from typing import List, Dict
from datetime import datetime
import hashlib
import re

class ContentScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def scrape_reddit(self, subreddit: str = "all", limit: int = 50) -> List[Dict]:
        """Scrape Reddit public posts (JSON API, no auth needed)"""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10)
                data = response.json()
                
                content_items = []
                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})
                    
                    content_id = hashlib.md5(post_data.get("url", "").encode()).hexdigest()
                    
                    item = {
                        "id": content_id,
                        "title": post_data.get("title", ""),
                        "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                        "thumbnail": post_data.get("thumbnail") if post_data.get("thumbnail", "").startswith("http") else None,
                        "source": "reddit",
                        "content_type": "text" if not post_data.get("is_video") else "video",
                        "preview": post_data.get("selftext", "")[:500],
                        "tags": [subreddit, "community"],
                        "created_at": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat()
                    }
                    content_items.append(item)
                
                return content_items
        except Exception as e:
            print(f"Reddit scraping error: {e}")
            return []
    
    async def scrape_youtube_rss(self, channel_id: str = None, query: str = None) -> List[Dict]:
        """Scrape YouTube via RSS feeds (no API key needed)"""
        content_items = []
        
        try:
            if channel_id:
                # Channel RSS feed
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:20]:
                    content_id = hashlib.md5(entry.link.encode()).hexdigest()
                    
                    item = {
                        "id": content_id,
                        "title": entry.title,
                        "url": entry.link,
                        "thumbnail": entry.get("media_thumbnail", [{}])[0].get("url") if "media_thumbnail" in entry else None,
                        "source": "youtube",
                        "content_type": "video",
                        "preview": entry.get("summary", "")[:500],
                        "tags": ["video", "youtube"],
                        "created_at": entry.get("published", datetime.utcnow().isoformat())
                    }
                    content_items.append(item)
        except Exception as e:
            print(f"YouTube RSS scraping error: {e}")
        
        return content_items
    
    async def scrape_medium(self, tag: str = "technology", limit: int = 30) -> List[Dict]:
        """Scrape Medium public articles"""
        url = f"https://medium.com/tag/{tag}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                content_items = []
                articles = soup.find_all('article', limit=limit)
                
                for article in articles:
                    try:
                        title_elem = article.find('h2') or article.find('h3')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        link_elem = article.find('a', href=True)
                        if not link_elem:
                            continue
                        
                        url = link_elem['href']
                        if url.startswith('/'):
                            url = f"https://medium.com{url}"
                        
                        content_id = hashlib.md5(url.encode()).hexdigest()
                        
                        preview_elem = article.find('p')
                        preview = preview_elem.get_text(strip=True) if preview_elem else ""
                        
                        item = {
                            "id": content_id,
                            "title": title,
                            "url": url,
                            "thumbnail": None,
                            "source": "medium",
                            "content_type": "article",
                            "preview": preview[:500],
                            "tags": [tag, "article", "blog"],
                            "created_at": datetime.utcnow().isoformat()
                        }
                        content_items.append(item)
                    except Exception as e:
                        continue
                
                return content_items
        except Exception as e:
            print(f"Medium scraping error: {e}")
            return []
    
    async def scrape_podcasts(self, term: str = "technology", limit: int = 20) -> List[Dict]:
        """Scrape podcasts from PodcastIndex API (free)"""
        # Note: In production, use actual PodcastIndex API with key
        # For demo, we'll simulate podcast data
        content_items = []
        
        try:
            # Simulate podcast results
            for i in range(min(limit, 10)):
                content_id = hashlib.md5(f"podcast_{term}_{i}".encode()).hexdigest()
                
                item = {
                    "id": content_id,
                    "title": f"Podcast Episode: {term.title()} Insights #{i+1}",
                    "url": f"https://example.com/podcast/{content_id}",
                    "thumbnail": None,
                    "source": "podcast",
                    "content_type": "audio",
                    "preview": f"Deep dive into {term} with industry experts. Covering latest trends and insights.",
                    "tags": [term, "podcast", "audio"],
                    "created_at": datetime.utcnow().isoformat()
                }
                content_items.append(item)
        except Exception as e:
            print(f"Podcast scraping error: {e}")
        
        return content_items
    
    async def scrape_github_repos(self, topic: str = "machine-learning", limit: int = 20) -> List[Dict]:
        """Scrape trending GitHub repositories"""
        url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page={limit}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10)
                data = response.json()
                
                content_items = []
                for repo in data.get("items", []):
                    content_id = hashlib.md5(repo.get("html_url", "").encode()).hexdigest()
                    
                    item = {
                        "id": content_id,
                        "title": repo.get("full_name", ""),
                        "url": repo.get("html_url", ""),
                        "thumbnail": repo.get("owner", {}).get("avatar_url"),
                        "source": "github",
                        "content_type": "repository",
                        "preview": repo.get("description", "")[:500],
                        "tags": [topic, "code", "github", "opensource"],
                        "created_at": repo.get("created_at", datetime.utcnow().isoformat())
                    }
                    content_items.append(item)
                
                return content_items
        except Exception as e:
            print(f"GitHub scraping error: {e}")
            return []
    
    async def scrape_all(self) -> List[Dict]:
        """Scrape content from all sources"""
        all_content = []
        
        # Scrape different sources in parallel
        tasks = [
            self.scrape_reddit("technology", 30),
            self.scrape_reddit("startups", 20),
            self.scrape_reddit("Entrepreneur", 20),
            self.scrape_medium("technology", 20),
            self.scrape_medium("startup", 15),
            self.scrape_medium("productivity", 15),
            self.scrape_github_repos("machine-learning", 15),
            self.scrape_github_repos("web-development", 15),
            self.scrape_podcasts("technology", 10),
            self.scrape_podcasts("business", 10),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_content.extend(result)
        
        return all_content

# Standalone scraper runner
async def run_scraper():
    scraper = ContentScraper()
    print("Starting content scraper...")
    
    content = await scraper.scrape_all()
    print(f"Scraped {len(content)} content items")
    
    # Import ML service and add content
    import sys
    sys.path.append('/home/user/tribed/backend')
    from ml_service import add_scraped_content
    
    add_scraped_content(content)
    print("Content added to ML engine")

if __name__ == "__main__":
    asyncio.run(run_scraper())
