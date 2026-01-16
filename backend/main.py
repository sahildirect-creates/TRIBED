from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from bson import ObjectId
import motor.motor_asyncio
import json

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "tribed-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days

# MongoDB setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.tribed

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="TRIBED API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class User(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserInDB(BaseModel):
    id: str
    email: str
    username: str
    hashed_password: str
    created_at: datetime
    saved_prompts: List[str] = []
    followed_tribes: List[str] = []
    shared_feeds: List[dict] = []

class Token(BaseModel):
    access_token: str
    token_type: str

class FeedPrompt(BaseModel):
    prompt: str
    filters: Optional[dict] = {}

class Tribe(BaseModel):
    name: str
    description: str
    prompt: str
    tags: List[str] = []
    
class TribeInDB(BaseModel):
    id: str
    name: str
    description: str
    prompt: str
    tags: List[str]
    creator_id: str
    followers: List[str] = []
    created_at: datetime
    
class SharedFeed(BaseModel):
    title: str
    prompt: str
    description: Optional[str] = ""
    
class ContentItem(BaseModel):
    id: str
    title: str
    url: str
    thumbnail: Optional[str]
    source: str
    content_type: str
    preview: str
    tags: List[str]
    created_at: datetime

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "TRIBED API v1.0", "status": "running"}

@app.post("/register", response_model=Token)
async def register(user: User):
    # Check if user exists
    existing = await db.users.find_one({"$or": [{"email": user.email}, {"username": user.username}]})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user_dict = {
        "email": user.email,
        "username": user.username,
        "hashed_password": get_password_hash(user.password),
        "created_at": datetime.utcnow(),
        "saved_prompts": [],
        "followed_tribes": [],
        "shared_feeds": []
    }
    
    result = await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "username": current_user["username"],
        "saved_prompts": current_user.get("saved_prompts", []),
        "followed_tribes": current_user.get("followed_tribes", []),
        "shared_feeds": current_user.get("shared_feeds", [])
    }

@app.post("/feed/generate")
async def generate_feed(feed_prompt: FeedPrompt, current_user: dict = Depends(get_current_user)):
    """Generate personalized feed based on prompt"""
    from ml_service import generate_feed_from_prompt
    
    # Generate feed using ML engine
    feed_items = await generate_feed_from_prompt(feed_prompt.prompt, feed_prompt.filters)
    
    # Save prompt to user history
    if feed_prompt.prompt not in current_user.get("saved_prompts", []):
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$push": {"saved_prompts": feed_prompt.prompt}}
        )
    
    return {"items": feed_items, "count": len(feed_items)}

@app.get("/tribes")
async def get_tribes(skip: int = 0, limit: int = 20):
    """Get all tribes"""
    tribes = await db.tribes.find().skip(skip).limit(limit).to_list(length=limit)
    return [
        {
            "id": str(tribe["_id"]),
            "name": tribe["name"],
            "description": tribe["description"],
            "prompt": tribe["prompt"],
            "tags": tribe["tags"],
            "creator_id": str(tribe["creator_id"]),
            "follower_count": len(tribe.get("followers", [])),
            "created_at": tribe["created_at"].isoformat()
        }
        for tribe in tribes
    ]

@app.post("/tribes")
async def create_tribe(tribe: Tribe, current_user: dict = Depends(get_current_user)):
    """Create a new tribe"""
    tribe_dict = {
        "name": tribe.name,
        "description": tribe.description,
        "prompt": tribe.prompt,
        "tags": tribe.tags,
        "creator_id": current_user["_id"],
        "followers": [str(current_user["_id"])],
        "created_at": datetime.utcnow()
    }
    
    result = await db.tribes.insert_one(tribe_dict)
    
    # Add to user's followed tribes
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$push": {"followed_tribes": str(result.inserted_id)}}
    )
    
    return {"id": str(result.inserted_id), "message": "Tribe created successfully"}

@app.post("/tribes/{tribe_id}/follow")
async def follow_tribe(tribe_id: str, current_user: dict = Depends(get_current_user)):
    """Follow a tribe"""
    tribe = await db.tribes.find_one({"_id": ObjectId(tribe_id)})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    user_id_str = str(current_user["_id"])
    
    # Add user to tribe followers
    if user_id_str not in tribe.get("followers", []):
        await db.tribes.update_one(
            {"_id": ObjectId(tribe_id)},
            {"$push": {"followers": user_id_str}}
        )
    
    # Add tribe to user's followed tribes
    if tribe_id not in current_user.get("followed_tribes", []):
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$push": {"followed_tribes": tribe_id}}
        )
    
    return {"message": "Tribe followed successfully"}

@app.post("/tribes/{tribe_id}/unfollow")
async def unfollow_tribe(tribe_id: str, current_user: dict = Depends(get_current_user)):
    """Unfollow a tribe"""
    user_id_str = str(current_user["_id"])
    
    await db.tribes.update_one(
        {"_id": ObjectId(tribe_id)},
        {"$pull": {"followers": user_id_str}}
    )
    
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$pull": {"followed_tribes": tribe_id}}
    )
    
    return {"message": "Tribe unfollowed successfully"}

@app.get("/tribes/{tribe_id}/feed")
async def get_tribe_feed(tribe_id: str):
    """Get feed for a specific tribe"""
    from ml_service import generate_feed_from_prompt
    
    tribe = await db.tribes.find_one({"_id": ObjectId(tribe_id)})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    feed_items = await generate_feed_from_prompt(tribe["prompt"], {})
    return {"items": feed_items, "tribe": tribe["name"]}

@app.post("/feed/share")
async def share_feed(shared_feed: SharedFeed, current_user: dict = Depends(get_current_user)):
    """Share a curated feed"""
    import secrets
    
    share_id = secrets.token_urlsafe(8)
    
    feed_dict = {
        "share_id": share_id,
        "title": shared_feed.title,
        "prompt": shared_feed.prompt,
        "description": shared_feed.description,
        "creator_id": str(current_user["_id"]),
        "creator_username": current_user["username"],
        "views": 0,
        "created_at": datetime.utcnow()
    }
    
    result = await db.shared_feeds.insert_one(feed_dict)
    
    # Add to user's shared feeds
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$push": {"shared_feeds": {"id": str(result.inserted_id), "share_id": share_id, "title": shared_feed.title}}}
    )
    
    return {"share_id": share_id, "url": f"/feed/{share_id}"}

@app.get("/feed/{share_id}")
async def get_shared_feed(share_id: str):
    """Get a shared feed by ID"""
    from ml_service import generate_feed_from_prompt
    
    feed = await db.shared_feeds.find_one({"share_id": share_id})
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    # Increment view count
    await db.shared_feeds.update_one(
        {"share_id": share_id},
        {"$inc": {"views": 1}}
    )
    
    # Generate feed content
    feed_items = await generate_feed_from_prompt(feed["prompt"], {})
    
    return {
        "title": feed["title"],
        "description": feed["description"],
        "creator_username": feed["creator_username"],
        "views": feed["views"] + 1,
        "items": feed_items
    }

@app.get("/discover")
async def discover_content(skip: int = 0, limit: int = 30):
    """Discover trending content and tribes"""
    # Get popular tribes
    tribes = await db.tribes.find().sort([("followers", -1)]).limit(10).to_list(length=10)
    
    # Get recent shared feeds
    shared_feeds = await db.shared_feeds.find().sort([("views", -1)]).limit(10).to_list(length=10)
    
    return {
        "popular_tribes": [
            {
                "id": str(tribe["_id"]),
                "name": tribe["name"],
                "description": tribe["description"],
                "follower_count": len(tribe.get("followers", []))
            }
            for tribe in tribes
        ],
        "trending_feeds": [
            {
                "share_id": feed["share_id"],
                "title": feed["title"],
                "creator": feed["creator_username"],
                "views": feed["views"]
            }
            for feed in shared_feeds
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
