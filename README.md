# What the Dream Obscures
## A Counterfactual Exploration of MoMA's Archive

> "If Anadol's system represents the museum's 'dream,' a counterfactual exploration of the archive's latent structure reveals what the dream obscures."

---

## 🎯 Project Overview

This project creates an interactive counter-narrative to Refik Anadol's *Unsupervised* (2022) at MoMA.

**Anadol's Approach**:
- Smooth, hypnotic abstraction
- Hides metadata and context
- Passive viewing experience
- "Collective memory" rhetoric
- Propaganda through seduction

**Your Counterfactual**:
- Discrete, confrontational navigation
- Foregrounds all metadata
- Active user choices required
- Reveals curatorial biases
- Counter-propaganda through exposure

---

## 🏗️ How It Works

### 1. Data: MoMA's Complete Collection
- 160,104 artworks with full metadata
- Title, Artist, Nationality, Gender, Date, Medium, Dimensions
- Acquisition date, Department, Classification
- **No images** - only metadata (this is the point!)

### 2. Latent Space from Metadata
- Convert metadata to text descriptions
- Create embeddings using sentence transformers
- Build navigable space based on curatorial categories
- Cluster by nationality, medium, era, gender, department

### 3. Interactive Navigation
Users must actively choose direction:
- "Show me similar nationality"
- "Show me similar medium"
- "Show me similar era"
- "Show me same gender"
- "Show me similar acquisition date"

**Key**: Can't smooth over choices. Every step is discrete and consequential.

### 4. Visual Generation
For each artwork visited, generate an image from metadata alone:
- Input: Full metadata text
- Process: Text-to-image API (DALL-E, Stable Diffusion, etc.)
- Output: What the metadata "looks like"

**Reveals**: How much information is lost in Anadol's abstraction

### 5. Bias Tracking
Real-time statistics on user's path:
- % Western vs. non-Western artists
- % Male vs. Female vs. Non-binary
- Acquisition date patterns (Cold War era dominance?)
- Department distribution
- Medium biases

**Exposes**: Colonial patterns, gender biases, curatorial choices

---

## 🎨 User Experience

```
1. Start at random artwork (or choose)
   ↓
2. See full metadata displayed
   ↓
3. See generated image from metadata
   ↓
4. Choose direction (nationality, medium, era, etc.)
   ↓
5. System shows nearest neighbors
   ↓
6. Pick next artwork
   ↓
7. Repeat - building a "walk"
   ↓
8. See statistics on your path's biases
```

---

## 🚀 Quick Start

### 1. Get MoMA Data
Download from: https://github.com/MuseumofModernArt/collection
- `Artworks.csv` → save to `data/Artworks.csv`
- `Artists.csv` → save to `data/Artists.csv`

### 2. Get API Key
Choose one:
- **Replicate** (recommended): https://replicate.com/account/api-tokens
- **OpenAI**: https://platform.openai.com/api-keys
- **Stability AI**: https://platform.stability.ai/

### 3. Create `.env` File
```bash
# For Replicate
REPLICATE_API_TOKEN=r8_your_token_here

# OR for OpenAI
OPENAI_API_KEY=sk-your_key_here
```

### 4. Install Dependencies
```bash
./venv/bin/pip install python-dotenv replicate openai sentence-transformers
```

### 5. Test Setup
```bash
./venv/bin/python test_setup.py
```

### 6. Build Latent Space
```bash
./venv/bin/python build_latent_space.py
```

### 7. Launch App
```bash
./venv/bin/python app.py
```

Open: http://localhost:5000

---

## 📊 What This Reveals

### 1. Discrete vs. Smooth
- **Anadol**: Smooth interpolation hides choices
- **You**: Every step is a visible, consequential choice

### 2. Metadata vs. Abstraction
- **Anadol**: Strips all context
- **You**: Foregrounds every detail

### 3. Passive vs. Active
- **Anadol**: Viewer is hypnotized
- **You**: User must actively navigate

### 4. Collective vs. Curated
- **Anadol**: "Collective memory" mystification
- **You**: Reveals curatorial biases

### 5. Dream vs. Archive
- **Anadol**: "Machine dreams" rhetoric
- **You**: Archive as constructed, political

---

## 🎓 For Your Paper

### Critical Framework

**Your Argument**:
Anadol's *Unsupervised* functions as propaganda by using AI's novel medium to create hypnotic abstraction that obscures:
- Discrete curatorial choices
- Colonial acquisition histories
- Gender and nationality biases
- The labor of classification
- The politics of "collective memory"

**This Project Provides**:
- Visual evidence of what abstraction hides
- Interactive demonstration of forced choices
- Quantitative data on biases
- Counterfactual: what if we couldn't smooth over?

### Visual Components

1. **Screenshots of navigation** - Show forced choices
2. **Path visualizations** - User walks through latent space
3. **Generated images** - What metadata looks like
4. **Statistics dashboards** - Quantified biases
5. **Comparison grids** - Anadol's smooth vs. your discrete

### Theoretical Connections

- **Cockcroft**: Cold War propaganda through abstraction
- **Crawford & Joler**: Extraction and colonial data practices
- **Davis**: Capitalism, novelty, and AI aesthetics
- **Lossin**: Critique of Unsupervised

---

## 💻 Technical Stack

### Backend
- Python/Flask
- pandas (data processing)
- sentence-transformers (text embeddings)
- scikit-learn (clustering, nearest neighbors)
- Replicate/OpenAI/Stability AI (image generation)

### Frontend
- React or Vue.js
- Three.js or D3.js (latent space visualization)
- Tailwind CSS (styling)

### Data Flow
```
MoMA CSV 
  → Text from Metadata 
  → Embeddings 
  → Latent Space 
  → User Navigation 
  → Selected Artwork 
  → Metadata → API → Generated Image
```

---

## 💰 Costs

### Development
- ~100 test images @ $0.002 = $0.20
- With Replicate free tier: $0

### Final Project
- ~1000 user interactions @ $0.002 = $2.00

### Your Paper
- 20-30 key screenshots @ $0.002 = $0.06

**Total: < $5 for entire project**

---

## 📁 Project Structure

```
windsurf-project/
├── data/
│   ├── Artworks.csv          # MoMA artworks (download)
│   └── Artists.csv           # MoMA artists (download)
├── src/
│   ├── build_latent_space.py # Create embeddings
│   ├── navigation.py         # Navigation logic
│   ├── generation.py         # Image generation
│   └── app.py                # Flask server
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   └── App.jsx           # Main app
│   └── public/
├── outputs/
│   ├── embeddings/           # Cached embeddings
│   ├── generated_images/     # Generated visuals
│   └── user_paths/           # Tracked navigation
├── .env                      # API keys (create this)
├── test_setup.py             # Setup checker
└── README_NEW.md             # This file
```

---

## 🎯 Next Steps

1. **Download MoMA data** (see SETUP_NEW_PROJECT.md)
2. **Get API key** (Replicate recommended)
3. **Run test_setup.py** to verify
4. **Build latent space** with build_latent_space.py
5. **Launch app** and start exploring
6. **Document findings** for your paper

---

## 🤝 Contributing to the Critique

This project is designed to be:
- **Reusable** for other AI art critiques
- **Extensible** for other museum collections
- **Educational** about AI art's ideological dimensions
- **Open** to collaboration and improvement

---

## 📚 Further Reading

- **NEW_PROJECT_PLAN.md** - Detailed architecture
- **SETUP_NEW_PROJECT.md** - Step-by-step setup
- **PROJECT_GUIDE.md** - Original de-abstraction project
- **EXAMPLES.md** - Sample outputs and interpretations

---

## ✨ Key Insight

> "Abstraction ≠ Neutrality"

This project proves it by making visible what Anadol's abstraction hides.

---

**Ready to build? Start with SETUP_NEW_PROJECT.md!**
