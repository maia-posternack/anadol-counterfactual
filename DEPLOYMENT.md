# Deployment Guide - What the Dream Obscures

## 🚀 Deploy to Vercel

This project is configured to deploy to Vercel with minimal setup.

### Prerequisites
- GitHub account
- Vercel account (sign up at https://vercel.com)
- Replicate API token (for AI image generation)

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel will automatically detect the Flask app

3. **Configure Environment Variables**
   In Vercel dashboard, add:
   - `REPLICATE_API_TOKEN`: Your Replicate API key

4. **Deploy**
   - Click "Deploy"
   - Your app will be live at `https://your-project.vercel.app`

### Important Notes

⚠️ **Large Files Excluded**
The following large files are excluded from the repository:
- `outputs/latent_space/*.npy` (233MB + 30MB embeddings)
- `data/artworks/moma_data/*.json` (140MB MoMA data)
- `venv/` (virtual environment)

**To run locally**, you'll need to:
1. Generate the latent space: `python build_latent_space.py`
2. This will create the necessary embedding files

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "REPLICATE_API_TOKEN=your_token_here" > .env

# Build latent space (required first time)
python build_latent_space.py

# Run the app
python app.py
```

### File Structure for Deployment
```
windsurf-project/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel configuration
├── templates/         # HTML templates
├── static/           # CSS, JS, assets
└── .gitignore        # Excludes large files
```

### Troubleshooting

**"No latent space found" error on Vercel:**
- This is expected! The latent space files are too large for Git
- You'll need to either:
  1. Use Vercel's storage solutions (Vercel Blob/KV)
  2. Host embeddings on external storage (S3, etc.)
  3. Generate smaller embeddings or use a sample dataset

**Environment variables:**
- Make sure `REPLICATE_API_TOKEN` is set in Vercel dashboard
- Go to Project Settings → Environment Variables

