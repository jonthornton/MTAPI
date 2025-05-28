# NYC Subway Real-Time Map 🚇

A modern, real-time web application displaying live NYC subway train locations using MTA's GTFS feeds.

## 🚀 Quick Deploy (Recommended)

### Deploy to Railway (Free)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/D9dJhq?referralCode=bonus)

**Steps:**
1. Click the button above
2. Sign in with GitHub
3. Click "Deploy Now"
4. Wait 2-3 minutes for deployment
5. Your live subway map will be ready!

### Deploy to Render (Free)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/dantraynor/subwaymap&branch=production-deploy)

### Deploy to Heroku (Free)
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/dantraynor/subwaymap/tree/production-deploy)

---

## 🌟 Features

- 🚇 **Real-time train data** from all MTA subway lines
- 🗺️ **Interactive map** with live train locations
- 📱 **Responsive design** for mobile and desktop
- 🔄 **Auto-refresh** every 30 seconds
- 🎨 **Color-coded subway lines** matching MTA standards
- ⚡ **No API key required** - uses free MTA feeds
- 🌍 **Custom domain support**

## 📸 Screenshots

*Live map showing real-time train positions across NYC*

## 🔧 Local Development

### Prerequisites
- Node.js 14+
- npm or yarn

### Setup
```bash
# Clone repository
git clone https://github.com/dantraynor/subwaymap.git
cd subwaymap

# Switch to production branch
git checkout production-deploy

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## 📊 API Endpoints

- `GET /api/mta/feeds/all` - All real-time train data
- `GET /api/mta/feed/:feedId` - Specific line group data
- `GET /health` - Health check

### Available Feed IDs:
- `1234567` - Lines 1,2,3,4,5,6,7
- `ace` - Lines A,C,E
- `bdfm` - Lines B,D,F,M
- `g` - Line G
- `jz` - Lines J,Z
- `l` - Line L
- `nqrw` - Lines N,Q,R,W
- `si` - Staten Island Railway

## 🏠 Project Structure

```
subwaymap/
├── backend/
│   ├── api/mta.js         # MTA API routes
│   ├── server.js          # Express server
│   └── package.json       # Backend dependencies
├── frontend/
│   ├── index.html         # Main webpage
│   ├── style.css          # Styling
│   ├── script.js          # App logic
│   └── map.js             # Map functionality
├── package.json           # Root package.json
└── README.md              # This file
```

## 🔧 Technologies

- **Backend**: Node.js, Express.js
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Map**: Leaflet.js
- **Data**: MTA GTFS-realtime feeds
- **Deployment**: Railway, Render, Heroku

## 🌍 Custom Domain Setup

### For Railway:
1. Deploy your app
2. Go to Railway dashboard → Settings → Domains
3. Add your custom domain
4. Update your DNS with provided CNAME

### For Your Spaceship Domain:
1. Deploy to Railway (or another host)
2. In Spaceship DNS settings, add:
   ```
   Type: CNAME
   Name: subway (or www)
   Value: your-app.up.railway.app
   ```
3. Access at `subway.yourdomain.com`

## 📈 Performance

- **Fast loading**: Optimized static assets
- **Real-time updates**: 30-second refresh cycle
- **Mobile optimized**: Responsive design
- **Low resource usage**: Minimal server requirements

## 🐛 Troubleshooting

### Common Issues:
1. **No train data**: Check MTA feed status
2. **Map not loading**: Verify internet connection
3. **Deployment fails**: Check build logs

### Debug Steps:
1. Open browser developer tools (F12)
2. Check Console for errors
3. Verify API endpoints return data
4. Check network requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 Data Sources

- **Real-time**: [MTA GTFS-realtime feeds](https://api.mta.info/#/subwayRealTimeFeeds)
- **Static**: [MTA GTFS static data](https://new.mta.info/developers)

## 📝 License

MIT License - feel free to use this project!

## ⭐ Support

If this project helps you, please star it on GitHub!

---

**Built with ❤️ for NYC transit enthusiasts**
