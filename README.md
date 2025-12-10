# What the Dream Obscures

An interactive AI art project exploring MoMA's collection through latent space visualization and generative AI.

## 🎨 Features

- **Latent Space Navigation**: Explore 158,822 artworks from MoMA's collection in an AI-generated embedding space
- **AI Visualization**: Generate abstract "machine art" visualizations of artworks using Replicate
- **Interactive UI**: Beautiful, modern interface for discovering art through AI's perspective
- **Semantic Search**: Find artworks by meaning, not just metadata

## 🚀 Local Setup

### Prerequisites

- Python 3.9+
- Replicate API key ([get one here](https://replicate.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maia-posternack/what-the-dream-obscures.git
   cd what-the-dream-obscures
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   echo "REPLICATE_API_TOKEN=your_token_here" > .env
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5001
   ```

## 📁 Project Structure

```
├── app.py                    # Flask application
├── templates/
│   └── index.html           # Main UI
├── static/
│   ├── css/style.css        # Styling
│   └── js/main.js           # Frontend logic
├── data/
│   └── artworks/moma_data/  # MoMA collection data
└── outputs/
    └── latent_space/        # Pre-computed embeddings (468MB, Git LFS)
```

## 🗃️ Dataset

The project uses MoMA's public collection dataset with pre-computed embeddings:
- **158,822 artworks** with full metadata
- **CLIP embeddings** for semantic search
- **PCA-reduced** 2D space for visualization
- Total size: ~468MB (stored via Git LFS)

## 🛠️ How It Works

1. **Data Processing**: MoMA artwork metadata is embedded using OpenAI's CLIP model
2. **Dimensionality Reduction**: High-dimensional embeddings are reduced to 2D using PCA
3. **Visualization**: Each artwork's position in latent space is visualized
4. **AI Generation**: Replicate API generates abstract visualizations based on the latent vectors

## 📝 License

Data from MoMA's collection is used under their public dataset license.

## 🎓 About

Created as an exploration of how AI "sees" and organizes art, questioning the boundaries between human and machine perception in the context of artistic creation and curation.
