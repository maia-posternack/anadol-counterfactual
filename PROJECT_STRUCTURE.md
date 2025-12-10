# Project Structure

## What the Dream Obscures
### A Counterfactual Exploration of MoMA's Archive

---

## 📁 Clean Project Structure

```
windsurf-project/
├── README.md                    # Main documentation
├── NEW_PROJECT_PLAN.md          # Detailed architecture & concept
├── FINAL_SETUP.md               # Setup guide & usage
├── QUICK_REFERENCE.md           # Quick commands & tips
├── PROJECT_STRUCTURE.md         # This file
│
├── .env                         # API keys (not in git)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
│
├── build_latent_space.py        # Creates neural network embeddings
├── app.py                       # Flask web server
│
├── data/
│   └── artworks/
│       └── moma_data/
│           ├── Artworks.json    # 158,863 artworks
│           ├── Artworks.txt
│           ├── Artists.json     # 15,763 artists
│           └── Artists.txt
│
├── outputs/
│   └── latent_space/            # Generated embeddings (created by build script)
│       ├── embeddings_full.npy
│       ├── embeddings_reduced.npy
│       ├── artworks.json
│       ├── descriptions.json
│       ├── metadata.json
│       └── statistics.json
│
├── templates/
│   └── index.html               # Main web interface
│
├── static/
│   ├── css/
│   │   └── style.css            # Styling
│   └── js/
│       └── main.js              # Interactivity
│
└── venv/                        # Python virtual environment
```

---

## 🎯 Key Files Explained

### Core Application

**`app.py`** - Flask backend server
- API endpoints for navigation
- Image generation via Replicate
- Statistics computation
- Dimension-based filtering

**`build_latent_space.py`** - Data processing
- Loads MoMA collection
- Creates text descriptions from metadata
- Generates neural network embeddings
- Builds navigable latent space

### Frontend

**`templates/index.html`** - Web interface
- Interactive navigation UI
- Metadata display
- Image generation controls
- Statistics dashboard

**`static/js/main.js`** - JavaScript logic
- API calls
- User interactions
- Dynamic content updates

**`static/css/style.css`** - Styling
- Dark theme
- Responsive design
- Visual components

### Documentation

**`README.md`** - Main documentation
- Project overview
- Quick start guide
- Technical details

**`NEW_PROJECT_PLAN.md`** - Detailed plan
- Complete architecture
- Critical framework
- Implementation strategy

**`FINAL_SETUP.md`** - Setup guide
- Installation steps
- Usage instructions
- Troubleshooting

**`QUICK_REFERENCE.md`** - Quick reference
- Commands
- Key concepts
- Troubleshooting tips

### Configuration

**`.env`** - Environment variables
- `REPLICATE_API_TOKEN` - Your API key
- Not committed to git

**`requirements.txt`** - Python packages
- All dependencies listed
- Install with: `pip install -r requirements.txt`

---

## 🚀 Workflow

### 1. Setup (One Time)
```bash
# Install dependencies
./venv/bin/pip install -r requirements.txt

# Add API key to .env
echo "REPLICATE_API_TOKEN=your_token" > .env
```

### 2. Build Latent Space (One Time)
```bash
# Creates embeddings from MoMA data
./venv/bin/python build_latent_space.py

# Takes ~15-20 minutes
# Output: outputs/latent_space/
```

### 3. Run Application
```bash
# Launch web server
./venv/bin/python app.py

# Open: http://localhost:5000
```

---

## 📊 Data Flow

```
MoMA JSON Files
    ↓
build_latent_space.py
    ↓
Text Descriptions (metadata → text)
    ↓
Neural Network Embeddings (sentence-transformers)
    ↓
Latent Space (384D → 50D via PCA)
    ↓
Saved to outputs/latent_space/
    ↓
app.py loads embeddings
    ↓
User navigates via web interface
    ↓
API calls for navigation & generation
    ↓
Replicate generates images
    ↓
Statistics computed in real-time
```

---

## 🎨 User Journey

```
1. Visit http://localhost:5000
2. Click "Start Exploring"
3. See random artwork + metadata
4. Click "Generate Visual from Metadata"
5. Choose navigation direction
6. Select next artwork from neighbors
7. Repeat steps 3-6
8. Click "Show Statistics"
9. See biases in your path
```

---

## 💰 Costs

- **Setup**: Free
- **Building latent space**: Free (local compute)
- **Per image generation**: ~$0.002
- **Typical session**: ~$0.04 (20 images)
- **For paper**: < $1 (50 screenshots)

---

## 🔧 Maintenance

### Rebuild Latent Space
```bash
rm -rf outputs/latent_space
./venv/bin/python build_latent_space.py
```

### Update Dependencies
```bash
./venv/bin/pip install --upgrade -r requirements.txt
```

### Clear Cache
```bash
# Clear generated images cache
# (They're stored in memory, restart app.py)
```

---

## 📝 For Your Paper

### Files to Reference

1. **`NEW_PROJECT_PLAN.md`** - Cite architecture
2. **`app.py`** - Cite implementation
3. **`outputs/latent_space/statistics.json`** - Cite dataset stats
4. **Screenshots from web interface** - Visual evidence

### Key Statistics

From `outputs/latent_space/statistics.json`:
- Total artworks in latent space
- Nationality distribution
- Gender distribution
- Top represented countries/artists

---

## ✨ What Makes This Work

**Technical**:
- Neural network embeddings capture semantic similarity
- PCA reduces dimensions while preserving structure
- Cosine similarity finds nearest neighbors
- Dimension filtering reveals biases

**Critical**:
- Metadata visibility counters abstraction
- Discrete choices counter smooth interpolation
- Statistics quantify biases
- Generation shows interpretation

**Experiential**:
- Users actively participate
- Choices have consequences
- Biases become visible
- Archive becomes navigable

---

**This is your complete, clean project structure!** 🎨

All old files removed. Only the counterfactual exploration remains.
