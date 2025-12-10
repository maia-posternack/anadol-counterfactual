# What the Dream Obscures - Artistic Redesign

## 🎨 Overview

A stunning, interactive visualization of MoMA's collection in latent space - a critical counterfactual to Refik Anadol's "Unsupervised."

## ✨ New Features

### 1. **Connected Graph Visualization**
- **Interactive network map** showing your current artwork and all nearby artworks
- **Labeled edges** indicating why artworks are connected (similarity, nationality, medium, department, gender)
- **Visited path highlighting** - edges you've traversed turn green
- **Click to navigate** - click any node to jump to that artwork
- Uses vis.js for smooth, physics-based graph layout

### 2. **Automatic Dual Visualization**
Both visualizations generate automatically when you select an artwork:
- **Latent Space Coordinates**: Abstract visualization of the 50-dimensional embedding
  - Bar chart showing all 50 dimensions
  - Heatmap representation
  - Raw metadata overlay
  - **Free** - no API credits needed
  
- **AI's Dream**: FLUX Schnell interprets the metadata
  - Shows what AI "imagines" from text alone
  - Costs ~$0.003 per image
  - Falls back to latent visualization if credits run out

### 3. **Visual Path History**
- **Thumbnail gallery** at the bottom showing every artwork you've visited
- **Current artwork highlighted** in pink
- **Click to navigate back** to any previous point in your journey
- Thumbnails update as visualizations generate

### 4. **Beautiful Dark Theme**
- Deep blacks (#0a0a0f) with subtle gradients
- Neon accents (green #00ff88, pink #ff0088, blue #00aaff)
- Smooth animations and transitions
- Glassmorphism effects
- Custom scrollbars

### 5. **Enhanced Navigation**
- Start with a random artwork
- Graph automatically shows all possible next steps
- Multiple connection types visible simultaneously
- Smooth camera movements focus on current node

## 🎯 Conceptual Alignment

This design directly critiques Anadol's work:

1. **Discrete Choices vs. Smooth Abstraction**
   - You must *choose* which connection to follow
   - Each choice is recorded and visible
   - Cannot smooth over the decision

2. **Metadata Exposure vs. Obscurity**
   - All metadata displayed explicitly
   - Biases visible in statistics
   - Connection reasons labeled

3. **Path Tracking vs. Endless Loop**
   - Your journey is recorded
   - Can see where you've been
   - Patterns emerge from your choices

4. **Dual Visualization**
   - Raw data (latent space) alongside AI's interpretation
   - Shows the gap between representation and reality
   - Exposes the computational machinery

## 🚀 Usage

1. **Click "Begin Your Journey"** - Start with a random artwork
2. **Explore the graph** - See all connected artworks in the network map
3. **Click any node** to navigate there
4. **Watch your path** build up in the thumbnail gallery
5. **Click "📊 Statistics"** to see the biases in your journey
6. **Click "🔄 New Start"** to reset and explore differently

## 🎨 Design Philosophy

- **Dark & Immersive**: Deep space aesthetic emphasizing data points
- **Neon Highlights**: Critical, technical aesthetic (not natural/organic)
- **Explicit Connections**: Every relationship labeled and visible
- **Agency**: User has full control and can see consequences of choices
- **Transparency**: All processes visible and debuggable

## 🔧 Technical Stack

- **Frontend**: 
  - Vis.js Network for graph visualization
  - Vanilla JavaScript (no framework bloat)
  - CSS animations and transitions
  - Responsive grid layouts

- **Backend**:
  - Flask server
  - NumPy for latent space operations
  - Matplotlib for latent space visualization
  - Replicate API for AI generation

- **Data**:
  - 158,822 artworks from MoMA collection
  - 50-dimensional embeddings via sentence-transformers
  - PCA dimensionality reduction for performance

## 📊 Performance

- Graph can handle 100+ nodes simultaneously
- Smooth physics simulation
- Automatic stabilization
- Efficient neighbor queries
- Cached generations

## 🎓 For Your Paper

This tool demonstrates:
- How AI systems make hidden choices about connections
- The colonial/gender/temporal biases in "collective memory"
- The difference between smooth abstraction and discrete decision-making
- How metadata tells a different story than visual aesthetics

Each statistic you reveal is a critique of Anadol's claim to represent "collective memory" - it's curated, biased, and politically situated.

