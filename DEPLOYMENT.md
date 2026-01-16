# 🚀 TRIBED Deployment Guide

## Quick Start Options

### Option 1: Local Development (Recommended for Testing)

#### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB 5.0+ (or use MongoDB Atlas free tier)

#### Steps

1. **Clone and setup**:
```bash
cd /home/user/tribed
./start.sh
```

This will:
- Set up Python virtual environment
- Install all dependencies
- Run content scraper
- Start backend on port 8000
- Start frontend on port 3000

2. **Access the app**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Docker Compose (Easiest)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Services:
- MongoDB: localhost:27017
- Backend: localhost:8000
- Frontend: localhost:3000

### Option 3: Cloud Deployment

## Backend Deployment

### Deploy to Render.com

1. **Create Render account**: https://render.com

2. **Create new Web Service**:
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   ```
   MONGODB_URL=<your-mongodb-atlas-url>
   SECRET_KEY=<generate-secure-key>
   PYTHON_VERSION=3.9.0
   ```

4. **Create MongoDB Atlas database**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Create free cluster
   - Get connection string
   - Add to Render env vars

### Deploy to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy backend
cd backend
flyctl launch
flyctl deploy

# Set secrets
flyctl secrets set MONGODB_URL="your-mongodb-url"
flyctl secrets set SECRET_KEY="your-secret-key"
```

### Deploy to Railway

1. **Install Railway CLI**:
```bash
npm i -g @railway/cli
```

2. **Deploy**:
```bash
cd backend
railway login
railway init
railway up
```

3. **Add MongoDB**:
   - Railway Dashboard > New > Database > MongoDB
   - Environment variables auto-configured

## Frontend Deployment

### Deploy to Vercel (Recommended)

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
cd frontend
vercel --prod
```

3. **Set Environment Variable**:
   - Vercel Dashboard > Settings > Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=<your-backend-url>`

4. **Redeploy**:
```bash
vercel --prod
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build
cd frontend
npm run build

# Deploy
netlify deploy --prod --dir=out
```

Add environment variable in Netlify dashboard:
- `NEXT_PUBLIC_API_URL=<your-backend-url>`

## Database Setup

### MongoDB Atlas (Free Tier)

1. **Create Account**: https://www.mongodb.com/cloud/atlas

2. **Create Cluster**:
   - Choose M0 (Free)
   - Select region close to your backend
   - Create cluster

3. **Database Access**:
   - Database Access > Add New User
   - Choose password authentication
   - Save credentials

4. **Network Access**:
   - Network Access > Add IP Address
   - Choose "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add specific IPs

5. **Get Connection String**:
   - Clusters > Connect > Connect Your Application
   - Copy connection string
   - Replace `<password>` with your password

## Environment Variables Reference

### Backend (.env)
```bash
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/tribed
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## Production Checklist

- [ ] Use strong SECRET_KEY (32+ characters, random)
- [ ] Enable MongoDB authentication
- [ ] Set up CORS properly for production domains
- [ ] Enable HTTPS (Render/Vercel/Fly.io do this automatically)
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Configure rate limiting
- [ ] Set up backups for MongoDB
- [ ] Add custom domain
- [ ] Set up CDN for static assets
- [ ] Enable gzip compression
- [ ] Configure caching headers

## Initial Data Setup

After deployment, seed initial content:

```bash
# SSH into backend server or run locally pointing to prod DB
python scrapers/scraper.py
```

This will populate your database with initial content from:
- Reddit
- Medium
- GitHub
- YouTube (RSS)

## Monitoring & Maintenance

### Backend Health Check
```bash
curl https://your-backend-url.com/
# Should return: {"message": "TRIBED API v1.0", "status": "running"}
```

### API Documentation
https://your-backend-url.com/docs

### Logs
- Render: Dashboard > Logs
- Fly.io: `flyctl logs`
- Railway: Dashboard > Logs

## Scaling

### Backend
- **Render**: Upgrade to Standard plan, add auto-scaling
- **Fly.io**: `flyctl scale count 2`
- **Railway**: Automatic scaling on Pro plan

### Database
- **MongoDB Atlas**: Upgrade cluster tier (M10, M20, etc.)
- Add read replicas for better performance
- Enable sharding for large datasets

### Frontend
- Vercel/Netlify handle auto-scaling
- Add CDN for global performance

## Custom Domain

### Backend (Render)
1. Settings > Custom Domain
2. Add your domain
3. Update DNS records (CNAME)

### Frontend (Vercel)
```bash
vercel domains add yourdomain.com
```

Update DNS:
- Type: CNAME
- Name: @
- Value: cname.vercel-dns.com

## Troubleshooting

### Backend won't start
- Check MongoDB connection string
- Verify SECRET_KEY is set
- Check Python version (3.9+)
- Review logs for errors

### Frontend can't connect to backend
- Verify NEXT_PUBLIC_API_URL is correct
- Check CORS settings in backend
- Ensure backend is running and accessible

### MongoDB connection issues
- Check network access whitelist
- Verify credentials
- Test connection string locally

### Content not loading
- Run scraper: `python scrapers/scraper.py`
- Check ML engine initialized: verify content_db.json exists
- Check API endpoint: `/feed/generate`

## Performance Tips

1. **Enable caching**: Add Redis for feed caching
2. **Optimize images**: Use Next.js Image component
3. **CDN**: Use Cloudflare for static assets
4. **Database indexes**: Add indexes on frequently queried fields
5. **Lazy loading**: Implement infinite scroll for feeds

## Security Best Practices

1. **JWT Secret**: Use cryptographically secure random string
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Sanitize user inputs
5. **CORS**: Configure allowed origins properly
6. **MongoDB**: Enable authentication, use specific user permissions
7. **Environment Variables**: Never commit secrets to git

## Support

- Documentation: /docs
- Issues: GitHub Issues
- Community: Discord/Slack

---

**Need help?** Open an issue on GitHub or contact support@tribed.app
