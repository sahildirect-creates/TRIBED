# 🚀 TRIBED - Prompt-Based Social Discovery Platform

A next-generation social platform that lets users create personalized content feeds using natural language prompts.

## ✨ Features

- **🎯 Prompt-Based Discovery**: Describe your interests in natural language
- **🤖 AI-Powered Matching**: ML embeddings match prompts with relevant content
- **👥 Tribes System**: Join interest-based communities
- **📤 Shareable Feeds**: Create and share curated content feeds
- **📱 Mobile-First Design**: Responsive UI optimized for all devices
- **🔒 Secure Authentication**: JWT-based auth with OAuth support

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **ML Engine**: Sentence Transformers + FAISS
- **Auth**: JWT with bcrypt

### Frontend
- **Framework**: Next.js 14 + React 18
- **Styling**: TailwindCSS
- **State**: Zustand
- **Animations**: Framer Motion

### Content Sources (Legal Scraping)
- Reddit public JSON API
- YouTube RSS feeds
- Medium public articles
- GitHub repositories
- Podcast RSS feeds

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB 5.0+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URL="mongodb://localhost:27017"
export SECRET_KEY="your-secret-key-here"

# Run content scraper (first time)
cd ../scrapers
python scraper.py

# Start backend server
cd ../backend
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📦 Deployment

### Backend Deployment (Render/Fly.io)

1. **Dockerfile** (backend):
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Deploy:
```bash
# Render
render deploy

# Fly.io
fly deploy
```

### Frontend Deployment (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Environment Variables

**Backend**:
- `MONGODB_URL`: MongoDB connection string
- `SECRET_KEY`: JWT secret key

**Frontend**:
- `NEXT_PUBLIC_API_URL`: Backend API URL

## 🎨 Design System

### Colors
- **Primary**: `#06D6A0` (Aqua)
- **Secondary**: `#FF6B6B` (Coral)
- **Accent**: `#00D9FF` (Cyan)
- **Dark**: `#0D1117`
- **Card**: `#161B22`

### Typography
- Font Family: Inter, system-ui

## 📱 Pages

1. **Landing** (`/`): Auth (login/signup)
2. **Home** (`/home`): Personalized feed with editable prompt
3. **Discover** (`/discover`): Trending tribes and feeds
4. **Tribes** (`/tribes`): Browse and join communities
5. **Share** (`/share`): Create shareable feed links
6. **Profile** (`/profile`): User dashboard and stats

## 🔧 API Endpoints

### Auth
- `POST /register`: Create account
- `POST /token`: Login
- `GET /me`: Get current user

### Feed
- `POST /feed/generate`: Generate feed from prompt
- `POST /feed/share`: Share feed
- `GET /feed/{share_id}`: Get shared feed

### Tribes
- `GET /tribes`: List all tribes
- `POST /tribes`: Create tribe
- `POST /tribes/{id}/follow`: Follow tribe
- `GET /tribes/{id}/feed`: Get tribe feed

### Discovery
- `GET /discover`: Get trending content

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🎯 Roadmap

- [ ] Advanced analytics dashboard
- [ ] Time tracking & mindful consumption metrics
- [ ] Creator monetization (tips/premium feeds)
- [ ] Mobile native apps (iOS/Android)
- [ ] Real-time collaborative tribes
- [ ] AI-powered content recommendations v2

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 👥 Team

Built by Genspark AI

## 📞 Support

- Email: support@tribed.app
- Discord: discord.gg/tribed
- Twitter: @tribedapp

---

**Made with ❤️ using AI-powered development**
# TRIBED
