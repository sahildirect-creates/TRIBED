from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Optional
import json
import os
from datetime import datetime

class MLFeedEngine:
    def __init__(self):
        # Load sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.content_metadata = []
        
        # Load or create content database
        self.load_content_db()
    
    def load_content_db(self):
        """Load content database from file"""
        db_path = "/home/user/tribed/ml-engine/content_db.json"
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                data = json.load(f)
                self.content_metadata = data.get("metadata", [])
                
                # Rebuild FAISS index
                if self.content_metadata:
                    embeddings = [item["embedding"] for item in self.content_metadata]
                    self.index = faiss.IndexFlatL2(self.dimension)
                    self.index.add(np.array(embeddings).astype('float32'))
    
    def save_content_db(self):
        """Save content database to file"""
        db_path = "/home/user/tribed/ml-engine/content_db.json"
        with open(db_path, 'w') as f:
            json.dump({"metadata": self.content_metadata}, f)
    
    def add_content(self, content_items: List[Dict]):
        """Add new content to the database with embeddings"""
        for item in content_items:
            # Create text representation for embedding
            text = f"{item['title']} {item.get('preview', '')} {' '.join(item.get('tags', []))}"
            
            # Generate embedding
            embedding = self.model.encode(text)
            
            # Add to index
            self.index.add(np.array([embedding]).astype('float32'))
            
            # Store metadata
            self.content_metadata.append({
                "id": item["id"],
                "title": item["title"],
                "url": item["url"],
                "thumbnail": item.get("thumbnail"),
                "source": item["source"],
                "content_type": item["content_type"],
                "preview": item.get("preview", ""),
                "tags": item.get("tags", []),
                "created_at": item.get("created_at", datetime.utcnow().isoformat()),
                "embedding": embedding.tolist()
            })
        
        self.save_content_db()
    
    def search_by_prompt(self, prompt: str, top_k: int = 30, filters: Optional[Dict] = None) -> List[Dict]:
        """Search content using natural language prompt"""
        # Generate embedding for prompt
        prompt_embedding = self.model.encode(prompt)
        
        # Search in FAISS
        D, I = self.index.search(np.array([prompt_embedding]).astype('float32'), min(top_k * 2, len(self.content_metadata)))
        
        # Retrieve results
        results = []
        for idx in I[0]:
            if idx < len(self.content_metadata):
                item = self.content_metadata[idx].copy()
                del item["embedding"]  # Remove embedding from response
                
                # Apply filters if provided
                if filters:
                    if "content_type" in filters and item["content_type"] != filters["content_type"]:
                        continue
                    if "source" in filters and item["source"] not in filters.get("source", []):
                        continue
                
                results.append(item)
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def classify_content(self, text: str) -> List[str]:
        """Classify content into categories"""
        categories = {
            "psychology": ["psychology", "mental health", "mindfulness", "therapy", "cognitive"],
            "founder_story": ["founder", "startup", "entrepreneur", "business", "company"],
            "lifestyle": ["lifestyle", "wellness", "fitness", "health", "travel"],
            "tech": ["technology", "AI", "software", "coding", "developer"],
            "product": ["product", "design", "UX", "interface", "features"],
            "finance": ["finance", "investing", "money", "crypto", "stocks"],
            "education": ["learning", "education", "tutorial", "course", "teaching"],
            "entertainment": ["entertainment", "movie", "music", "gaming", "art"]
        }
        
        text_lower = text.lower()
        detected_tags = []
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_tags.append(category)
        
        return detected_tags if detected_tags else ["general"]

# Global engine instance
ml_engine = MLFeedEngine()

async def generate_feed_from_prompt(prompt: str, filters: Dict = {}) -> List[Dict]:
    """Generate feed based on user prompt"""
    return ml_engine.search_by_prompt(prompt, top_k=30, filters=filters)

def add_scraped_content(content_items: List[Dict]):
    """Add newly scraped content to ML engine"""
    ml_engine.add_content(content_items)
