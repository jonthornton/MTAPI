# Railway Deployment Guide

## 🚇 Deploy Your Real-Time NYC Subway Map to Railway

### Step 1: Sign Up for Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Verify your account (you get $5 free credit)

### Step 2: Deploy Your App

1. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `dantraynor/subwaymap` repository
   - Select the `production-deploy` branch

2. **Configure Deployment**
   - Railway will automatically detect it's a Node.js app
   - Root directory: `/` (leave as default)
   - Build command: `npm install` (automatic)
   - Start command: `npm start` (automatic)

3. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (2-3 minutes)

### Step 3: Get Your Live URL
1. Once deployed, Railway will give you a URL like:
   ```
   https://your-app-name.up.railway.app
   ```
2. Click on it to see your live subway map! 🎉

### Step 4: Connect Your Custom Domain
1. In Railway dashboard, go to your project
2. Click "Settings" → "Domains"
3. Click "Custom Domain"
4. Enter your domain (e.g., `subway.yourdomain.com`)
5. Update your DNS with the CNAME Railway provides

## 🔧 Configuration

### Environment Variables (Optional)
Railway automatically sets `PORT`, but you can add:
- `NODE_ENV=production`

### Auto-Deploy
Railway automatically redeploys when you push to the `production-deploy` branch!

## 📊 Usage & Limits

### Free Tier:
- ✅ 500 execution hours/month
- ✅ Custom domains
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub

### Your App Usage:
- Should use ~1-2 hours per day if actively used
- Well within free limits for personal use

## 🚀 Alternative: One-Click Deploy

I can also create a "Deploy to Railway" button for instant deployment!

## 🔄 Updates

To update your live site:
1. Make changes to your code
2. Push to the `production-deploy` branch
3. Railway automatically redeploys!

## 🐛 Troubleshooting

### Common Issues:
1. **Build fails**: Check the build logs in Railway dashboard
2. **App crashes**: Check the deployment logs
3. **API errors**: MTA feeds are free and should work immediately

### View Logs:
1. Go to Railway dashboard
2. Click your project
3. Click "Deployments" → View logs

## 🌟 Success!

Once deployed, your app will:
- ✅ Show real-time MTA train data
- ✅ Update every 30 seconds
- ✅ Work on mobile and desktop
- ✅ Be accessible worldwide
- ✅ Have automatic HTTPS

Your live NYC Subway Map will be ready! 🗽🚇
