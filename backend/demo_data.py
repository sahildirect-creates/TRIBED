#!/usr/bin/env python3
"""
TRIBED Demo Server - Simplified version for testing
Runs backend with in-memory storage for quick demo
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict
import hashlib

# Mock data storage
USERS = {}
TRIBES = []
SHARED_FEEDS = []
CONTENT_DB = []

# Sample content data
def generate_sample_content():
    """Generate sample content for demo"""
    content = [
        {
            "id": hashlib.md5("content1".encode()).hexdigest(),
            "title": "Building a Startup in 2024: Lessons from Y Combinator",
            "url": "https://example.com/startup-lessons",
            "thumbnail": "https://via.placeholder.com/400x300/06D6A0/ffffff?text=Startup",
            "source": "medium",
            "content_type": "article",
            "preview": "A comprehensive guide on building successful startups in the modern era...",
            "tags": ["startup", "business", "entrepreneurship"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content2".encode()).hexdigest(),
            "title": "The Future of AI: GPT-4 and Beyond",
            "url": "https://example.com/ai-future",
            "thumbnail": "https://via.placeholder.com/400x300/FF6B6B/ffffff?text=AI",
            "source": "youtube",
            "content_type": "video",
            "preview": "Exploring the latest developments in artificial intelligence and machine learning...",
            "tags": ["AI", "technology", "machine-learning"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content3".encode()).hexdigest(),
            "title": "React Performance Optimization: A Deep Dive",
            "url": "https://example.com/react-performance",
            "thumbnail": "https://via.placeholder.com/400x300/00D9FF/ffffff?text=React",
            "source": "github",
            "content_type": "repository",
            "preview": "Learn how to optimize React applications for maximum performance...",
            "tags": ["react", "javascript", "performance"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content4".encode()).hexdigest(),
            "title": "Product Management: From Idea to Launch",
            "url": "https://example.com/product-management",
            "thumbnail": "https://via.placeholder.com/400x300/06D6A0/ffffff?text=Product",
            "source": "medium",
            "content_type": "article",
            "preview": "A practical guide to product management and launching successful products...",
            "tags": ["product", "management", "startup"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content5".encode()).hexdigest(),
            "title": "The Tech Founder's Podcast: Episode 42",
            "url": "https://example.com/podcast-42",
            "thumbnail": None,
            "source": "podcast",
            "content_type": "audio",
            "preview": "Interview with successful tech founders about their journey...",
            "tags": ["podcast", "founder", "interview"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content6".encode()).hexdigest(),
            "title": "Minimalist Design: Less is More",
            "url": "https://example.com/minimalist-design",
            "thumbnail": "https://via.placeholder.com/400x300/FF6B6B/ffffff?text=Design",
            "source": "medium",
            "content_type": "article",
            "preview": "Exploring the principles of minimalist design and how to apply them...",
            "tags": ["design", "minimalism", "UX"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content7".encode()).hexdigest(),
            "title": "Gen Z Startup Culture: What's Different?",
            "url": "https://example.com/genz-startup",
            "thumbnail": "https://via.placeholder.com/400x300/00D9FF/ffffff?text=GenZ",
            "source": "youtube",
            "content_type": "video",
            "preview": "How Gen Z is changing the startup landscape with new approaches...",
            "tags": ["genz", "startup", "culture"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": hashlib.md5("content8".encode()).hexdigest(),
            "title": "Deep Work: How to Focus in a Distracted World",
            "url": "https://example.com/deep-work",
            "thumbnail": "https://via.placeholder.com/400x300/06D6A0/ffffff?text=Focus",
            "source": "medium",
            "content_type": "article",
            "preview": "Strategies for maintaining focus and productivity in modern life...",
            "tags": ["productivity", "focus", "lifestyle"],
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    return content

# Initialize sample data
CONTENT_DB = generate_sample_content()

# Sample tribes
TRIBES = [
    {
        "id": "tribe1",
        "name": "Builder Vlogs",
        "description": "For indie makers and builders sharing their journey",
        "prompt": "Indie maker vlogs, building in public, startup journeys",
        "tags": ["builder", "indie", "vlog"],
        "creator_id": "demo_user",
        "followers": ["demo_user"],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "tribe2",
        "name": "Deep Tech",
        "description": "Cutting-edge technology and research",
        "prompt": "AI research, machine learning, quantum computing, advanced tech",
        "tags": ["AI", "research", "technology"],
        "creator_id": "demo_user",
        "followers": [],
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "tribe3",
        "name": "Product Nerds",
        "description": "Product management, design, and UX",
        "prompt": "Product design, UX research, product management insights",
        "tags": ["product", "design", "UX"],
        "creator_id": "demo_user",
        "followers": [],
        "created_at": datetime.utcnow().isoformat()
    }
]

def simple_search(prompt: str, content_db: List[Dict]) -> List[Dict]:
    """Simple keyword-based search for demo"""
    prompt_lower = prompt.lower()
    keywords = prompt_lower.split()
    
    results = []
    for item in content_db:
        score = 0
        text = f"{item['title']} {item['preview']} {' '.join(item['tags'])}".lower()
        
        for keyword in keywords:
            if keyword in text:
                score += 1
        
        if score > 0:
            results.append((score, item))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in results[:20]]

print("✅ TRIBED Demo Server Ready!")
print(f"📊 Loaded {len(CONTENT_DB)} content items")
print(f"👥 Loaded {len(TRIBES)} sample tribes")
print("\nDemo Data:")
print("- Username: demo@tribed.app")
print("- Password: demo123")
print("\n🚀 Start the actual server with: python main.py")
