# 🚂 Deploy to Railway - Step by Step

Your project is ready to deploy with the **full 158k artwork dataset**! Railway can handle it no problem.

## ✅ What's Ready

- ✅ All code committed to Git  
- ✅ Full latent space dataset included (447MB)
- ✅ `Procfile` configured
- ✅ `railway.json` configured
- ✅ `requirements.txt` with all dependencies
- ✅ Port configuration for Railway

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
cd "/Users/maiaposternack/Desktop/afvs 222/CascadeProjects/windsurf-project"

# Create a new GitHub repository at https://github.com/new
# Then run:

git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

**Note:** GitHub has a 100MB file size limit. Your `embeddings_full.npy` is 233MB, so the push will fail. See "Fixing GitHub Push" below.

### Step 2: Deploy on Railway

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will automatically:
   - Detect your Flask app
   - Install dependencies from `requirements.txt`
   - Use the `Procfile` to start your app
   - Assign a public URL

5. **Add Environment Variable:**
   - Click on your deployed service
   - Go to **Variables** tab
   - Add: `REPLICATE_API_TOKEN` = `your_token_here`

6. **Deploy!**
   - Railway will build and deploy
   - You'll get a URL like: `https://your-project.up.railway.app`

## 🔧 Fixing GitHub Push (File Too Large Error)

GitHub blocks files over 100MB. You have two options:

### Option A: Use Git LFS (Recommended)

```bash
# Install Git LFS
brew install git-lfs  # or: sudo port install git-lfs
git lfs install

# Track large files
git lfs track "*.npy"
git lfs track "outputs/latent_space/artworks.json"
git lfs track "outputs/latent_space/descriptions.json"

# Add .gitattributes
git add .gitattributes

# Recommit
git add -A
git commit --amend -m "Prepare for Railway deployment with full dataset (using LFS)"

# Push (this will upload large files to LFS)
git push -u origin main
```

### Option B: Deploy Without GitHub

You can upload directly to Railway without GitHub:

1. Go to https://railway.app/new
2. Click **"Deploy from a Template"** → **"Empty Project"**  
3. In your project, add a **"New"** → **"GitHub Repo"**
4. Or use Railway CLI (after logging in through browser):
   ```bash
   railway login  # Opens browser
   railway init
   railway up
   ```

## 📊 Expected Deploy Time & Size

- **Repository size:** ~450MB
- **Install size (with dependencies):** ~1.5GB
- **Build time:** 5-10 minutes (first deploy)
- **Deploy time:** 1-2 minutes
- **Monthly cost:** Free tier available (500 hours), then ~$5/month

## 🎯 After Deployment

Your app will be live at a URL like:
```
https://windsurf-project-production.up.railway.app
```

You can:
- ✅ Navigate the full 158k artwork dataset
- ✅ Generate AI visualizations with Replicate
- ✅ Explore the latent space
- ✅ All features working with full dataset!

## 🐛 Troubleshooting

**Build fails with "Out of memory":**
- Railway free tier: 8GB RAM
- Your app needs ~2GB for numpy/sklearn + 450MB data
- Should work fine, but if not, upgrade to Hobby plan ($5/month with 16GB RAM)

**"Module not found" errors:**
- Check that `requirements.txt` is in the root directory
- Railway reads this automatically

**App doesn't start:**
- Check Railway logs in the dashboard
- Verify `REPLICATE_API_TOKEN` is set in Variables

**Port binding errors:**
- The app auto-detects Railway's PORT environment variable
- No configuration needed!

