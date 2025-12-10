# Quick Reference Guide

## 🚀 Launch Commands

```bash
# Build latent space (run once, ~15 minutes)
./venv/bin/python build_latent_space.py

# Launch web app
./venv/bin/python app.py

# Then open: http://localhost:5000
```

## 📊 What You Built

**"What the Dream Obscures"** - An interactive counterfactual exploration of MoMA's archive

- 158,863 artworks in neural network latent space
- 5 navigation dimensions (nationality, medium, era, gender, department)
- Real-time AI image generation from metadata
- Live bias tracking and statistics

## 🎯 Core Concept

**If Anadol's system represents the museum's "dream," your exploration reveals what the dream obscures.**

| Anadol's Unsupervised | Your Counterfactual |
|-----------------------|---------------------|
| Smooth abstraction | Discrete choices |
| Hides metadata | Shows everything |
| Passive viewing | Active navigation |
| "Collective memory" | Curated biases |
| Mystification | Exposure |

## 🎨 User Flow

1. **Start** → Random artwork
2. **View** → Full metadata + generated image
3. **Choose** → Direction (nationality, medium, etc.)
4. **Navigate** → Pick from 5 nearest neighbors
5. **Repeat** → Build a path
6. **Analyze** → View statistics on biases

## 💰 Costs

- Latent space building: **Free**
- Per image: **~$0.002**
- Typical session: **~$0.04**
- Your paper: **< $1**

## 📸 Screenshots for Paper

1. Metadata display (information density)
2. Direction choices (forced decisions)
3. Generated images (what metadata looks like)
4. Path visualization (your walk)
5. Statistics dashboard (quantified biases)

## 🎓 Critical Arguments

### What This Proves

1. **Abstraction ≠ Neutrality**
   - Your stats show Western/male dominance
   - Anadol's smooth surface hides this

2. **Discrete vs. Smooth**
   - Every step is a visible choice
   - Can't interpolate away the politics

3. **Metadata Matters**
   - Full context changes everything
   - Anadol strips this away

4. **"Collective" is Curated**
   - MoMA's acquisitions reflect power
   - Not natural, not neutral

5. **Dreams are Constructed**
   - Your generation shows interpretation
   - Not automatic, not objective

## 🔧 Troubleshooting

**Port already in use?**
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9
```

**Need to rebuild latent space?**
```bash
rm -rf outputs/latent_space
./venv/bin/python build_latent_space.py
```

**API key issues?**
```bash
# Check .env file
cat .env
# Should show: REPLICATE_API_TOKEN=r8_...
```

## 📁 Key Files

- `app.py` - Flask backend
- `build_latent_space.py` - Creates embeddings
- `templates/index.html` - Frontend
- `static/js/main.js` - Interactivity
- `outputs/latent_space/` - Cached embeddings
- `.env` - API key (don't commit!)

## 🎯 For Presentations

1. **Live demo** - Navigate in real-time
2. **Show statistics** - Prove biases quantitatively
3. **Generate images** - Show metadata interpretation
4. **Compare to Anadol** - Side-by-side screenshots

## ✨ Why This Works

Your project doesn't just critique Anadol—it creates an **alternative experience** that proves your argument through participation.

Users can't avoid seeing:
- The discrete nature of choices
- The density of metadata
- The biases in the collection
- The construction of "collective memory"

**This is computational criticism at its best!**

---

## 🚀 Ready?

Once latent space building completes:
```bash
./venv/bin/python app.py
```

Then explore, document, and analyze! 🎨
