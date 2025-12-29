# 🌍 Eco-Sync MVP

**AI-Driven Circular Barter Agent for Campus Sustainability**

Transform campus waste into a circular economy through intelligent AI-powered multi-party swaps.

---

## 🎯 Project Overview

Eco-Sync is an autonomous barter platform that uses **Gemini Vision AI** to identify items and an **intelligent matching engine** to orchestrate complex 2-way and 3-way circular swaps. Every completed swap awards **Eco-Credits**, gamifying sustainability on campus.

### Key Features

✅ **AI Vision Analysis** - Upload photos, Gemini identifies items automatically  
✅ **Smart Matching** - Finds 2-way and 3-way circular swap opportunities  
✅ **Eco-Credits** - Gamification through reward points  
✅ **Lost & Found** - Community item recovery system  
✅ **Leaderboard** - Top sustainability contributors  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- A Gemini API key (optional - works with mock data)

### Installation

1. **Clone/Navigate to project:**
```bash
cd eco-sync-mvp
```

2. **Set up backend:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment:**
Edit `backend/.env` and add your Gemini API key (optional):
```
GEMINI_API_KEY=your_actual_api_key_here
```

4. **Initialize database:**
```bash
python create_tables.py
```

5. **Seed demo data (optional but recommended):**
```bash
python seed_demo.py
```

6. **Start backend server:**
```bash
python uvicorn_run.py
```

Backend will run at: `http://localhost:8000`

7. **Start frontend (in new terminal):**
```bash
cd frontend
python -m http.server 3000
```

### Live Demo & Code
- **Live Demo**: [https://eco-sync-mvp.vercel.app](https://eco-sync-mvp.vercel.app)
- **Repository**: [https://github.com/JSR2406/GDG-Hackathon-](https://github.com/JSR2406/GDG-Hackathon-)
- **Design**: [Figma Prototype](https://wool-night-00859449.figma.site/)

---

## 📖 Usage Guide

### 1. Register Users
- Navigate to **Register** tab
- Fill in user details (name, email, semester, department, hostel)
- Click **Register**

### 2. Upload Items
- Go to **Upload Item** tab
- Select user and upload item photo
- Gemini AI will analyze and auto-populate fields
- Review AI analysis (confidence, eco-value, suggested swaps)

### 3. Create Barter Intent
- Navigate to **Barter** tab
- Select user and their item
- Specify what you want in exchange
- Click **Find Matches**
- System automatically finds 2-way or 3-way swaps!

### 4. Accept Matches
- Go to **Matches** tab
- View all your pending matches
- See swap flow visualization
- Click **Accept Match**
- When all participants accept, eco-credits are awarded!

### 5. View Leaderboard
- Navigate to **Leaderboard** tab
- See top contributors ranked by eco-credits
- Track your sustainability impact

---

## 🎬 Demo Flow (5-Minute Pitch)

### Perfect 3-Way Cycle Demo

If you ran `seed_demo.py`, you have a perfect 3-way cycle ready:

1. **Users Created:**
   - Arun (Mechanical) - Has: Drafter → Wants: Textbook
   - Priya (Mechanical) - Has: Textbook → Wants: Lab Coat
   - Ravi (Computer Science) - Has: Lab Coat → Wants: Drafter

2. **Test the Matching:**
   - Go to Barter tab
   - Select any user (e.g., Arun)
   - Select their item
   - Enter what they want
   - Click **Find Matches**
   - **BOOM!** 3-way circular swap detected instantly! 🎉

3. **Complete the Swap:**
   - Go to Matches tab
   - All three users accept the match
   - Eco-credits awarded to all participants
   - Check Leaderboard to see updated rankings

---

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── routers/          # API endpoints
│   │   ├── users.py      # User management
│   │   ├── items.py      # Item upload & Gemini analysis
│   │   ├── barter.py     # Barter intent & matching
│   │   ├── matches.py    # Match acceptance
│   │   ├── lost_found.py # Lost & found items
│   │   └── eco_credits.py # Credits & leaderboard
│   ├── services/
│   │   ├── gemini_agent.py    # AI vision analysis
│   │   └── matching_engine.py # 2-way & 3-way matching
│   ├── database.py       # SQLAlchemy setup
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   └── crud.py           # Database operations
```

### Frontend (Vanilla HTML/CSS/JS)
```
frontend/
├── index.html   # Tabbed interface
├── styles.css   # Premium gradient design
└── app.js       # API integration & UI logic
```

### Database (SQLite)
- **Users** - Student profiles
- **Items** - Available items for barter
- **BarterEdges** - What users want to swap
- **Matches** - Detected swap opportunities
- **EcoCredits** - Reward transactions
- **LostFound** - Lost & found postings

---

## 🧠 Matching Algorithm

### 2-Way Direct Match
```
A has X, wants Y
B has Y, wants X
→ Perfect 2-way swap!
```

### 3-Way Circular Match
```
A has X, wants Y
B has Y, wants Z
C has Z, wants X
→ A→B→C→A circular swap!
```

**Scoring Factors:**
- Department match (+2 points)
- Semester proximity (+1 point)
- Hostel match (+3 points for emergency)
- Emergency flag (+5 points)

---

## 🎨 Design Philosophy

- **Purple Gradient Theme** - Modern, vibrant, eco-friendly
- **Smooth Animations** - Micro-interactions for engagement
- **Responsive Design** - Works on all devices
- **Clear Visual Hierarchy** - Easy navigation
- **Success Feedback** - Immediate user confirmation

---

## 🔧 API Documentation

Once backend is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/` | Register new user |
| POST | `/api/v1/items/users/{id}/items/upload-photo` | Upload & analyze item |
| POST | `/api/v1/barter/barter-intents` | Create intent & find matches |
| GET | `/api/v1/matches/{user_id}` | Get user's matches |
| POST | `/api/v1/matches/{id}/accept` | Accept a match |
| GET | `/api/v1/eco-credits/leaderboard/top` | Get leaderboard |

---

## 🌟 Unique Selling Points

1. **Autonomous Matching** - No manual searching, AI finds optimal swaps
2. **Multi-Party Swaps** - Solves complex 3-way cycles automatically
3. **Vision AI Integration** - Photo upload → instant item identification
4. **Gamification** - Eco-credits make sustainability fun
5. **Campus-Specific** - Designed for student lifecycle (semester transitions)

---

## 🚢 Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Heroku
```bash
# Create app
heroku create eco-sync-app

# Deploy
git push heroku main
```

---

## 🐛 Troubleshooting

**Issue:** Gemini API errors  
**Solution:** Check `.env` file has valid API key, or use mock mode (automatic fallback)

**Issue:** Database errors  
**Solution:** Delete `eco_sync.db` and run `python create_tables.py` again

**Issue:** CORS errors  
**Solution:** Ensure backend is running on port 8000 and frontend on 3000

**Issue:** No matches found  
**Solution:** Run `seed_demo.py` to create perfect 3-way cycle scenario

---

## 📊 Success Metrics

- ✅ Users can register with campus details
- ✅ Items upload with Gemini auto-analysis
- ✅ 2-way and 3-way swaps detected automatically
- ✅ Matches display all participants and flow
- ✅ Users can accept matches
- ✅ Eco-credits awarded on completion
- ✅ Leaderboard shows top contributors
- ✅ Lost & found posts can be created
- ✅ Frontend is functional and beautiful
- ✅ Demo data creates perfect 3-way cycle in <1 minute

---

## 🎓 Hackathon Pitch Script

**Opening (30s):**  
"Eco-Sync is an AI-driven autonomous barter agent that transforms campus waste into a circular economy. Every semester, students discard perfectly reusable items. We solve this with intelligent multi-party swap orchestration."

**Live Demo (3 mins):**  
1. Show Swagger UI → create users
2. Upload item photo → Gemini analysis
3. Create barter intents → 3-way cycle detection
4. Accept match → eco-credits awarded
5. Show leaderboard → gamification working

**Closing (30s):**  
"Unlike generic marketplaces, Eco-Sync autonomously orchestrates complex swaps through AI vision and graph-based matching, turning every transaction into an environmental win."

---

## 🤝 Contributing

This is a hackathon MVP. For production:
- Add authentication (JWT)
- Implement real-time notifications
- Add chat between swap participants
- Deploy with PostgreSQL
- Add mobile app
- Implement blockchain for credit verification

---

## 📄 License

MIT License - Built for hackathon demonstration

---

## 🙏 Acknowledgments

- **Gemini AI** - Vision analysis
- **FastAPI** - Lightning-fast backend
- **SQLAlchemy** - Robust ORM
- **Inter Font** - Beautiful typography

---

**Built with ❤️ for campus sustainability**

🌍 **Reduce. Reuse. Eco-Sync.**
