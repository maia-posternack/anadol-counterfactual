#!/usr/bin/env python3
"""
Build Latent Space from MoMA Collection

Creates a neural network-based latent space from artwork metadata.
Users can then navigate this space to explore the collection.
"""

import json
import numpy as np
import pickle
from pathlib import Path
from tqdm import tqdm

import torch
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize

print("=" * 70)
print("BUILDING LATENT SPACE FROM MOMA COLLECTION")
print("=" * 70)
print()

# Load MoMA data
print("1. Loading MoMA data...")
with open('data/artworks/moma_data/Artworks.json', 'r') as f:
    artworks = json.load(f)

with open('data/artworks/moma_data/Artists.json', 'r') as f:
    artists_data = json.load(f)

# Create artist lookup
artists = {a['ConstituentID']: a for a in artists_data}

print(f"   ✓ Loaded {len(artworks):,} artworks")
print(f"   ✓ Loaded {len(artists):,} artists")
print()

# Filter to artworks with sufficient metadata
print("2. Filtering artworks with metadata...")
valid_artworks = []

for artwork in tqdm(artworks, desc="   Processing"):
    # Must have at least title and artist
    if not artwork.get('Title') or not artwork.get('Artist'):
        continue
    
    # Skip if marked as not curator approved
    if artwork.get('CuratorApproved') == 'N':
        continue
    
    valid_artworks.append(artwork)

print(f"   ✓ Filtered to {len(valid_artworks):,} valid artworks")
print()

# Create text descriptions from metadata
print("3. Creating text descriptions from metadata...")

def create_description(artwork):
    """Convert artwork metadata to descriptive text"""
    parts = []
    
    # Title
    if artwork.get('Title'):
        parts.append(f"Title: {artwork['Title']}")
    
    # Artist info
    artist_names = artwork.get('Artist', 'Unknown')
    parts.append(f"Artist: {artist_names}")
    
    # Get artist details if available
    if artwork.get('ConstituentID'):
        const_ids = artwork['ConstituentID']
        if isinstance(const_ids, list) and const_ids:
            artist_id = const_ids[0]
            if artist_id in artists:
                artist = artists[artist_id]
                if artist.get('Nationality'):
                    parts.append(f"Nationality: {artist['Nationality']}")
                if artist.get('Gender'):
                    parts.append(f"Gender: {artist['Gender']}")
                if artist.get('BeginDate'):
                    parts.append(f"Artist born: {artist['BeginDate']}")
    
    # Date
    if artwork.get('Date'):
        parts.append(f"Date created: {artwork['Date']}")
    
    # Medium
    if artwork.get('Medium'):
        parts.append(f"Medium: {artwork['Medium']}")
    
    # Dimensions
    if artwork.get('Dimensions'):
        parts.append(f"Dimensions: {artwork['Dimensions']}")
    
    # Classification
    if artwork.get('Classification'):
        parts.append(f"Classification: {artwork['Classification']}")
    
    # Department
    if artwork.get('Department'):
        parts.append(f"Department: {artwork['Department']}")
    
    # Date acquired
    if artwork.get('DateAcquired'):
        parts.append(f"Acquired by MoMA: {artwork['DateAcquired']}")
    
    # Credit line (reveals acquisition context)
    if artwork.get('CreditLine'):
        parts.append(f"Credit: {artwork['CreditLine']}")
    
    return ". ".join(parts)

descriptions = []
for artwork in tqdm(valid_artworks, desc="   Creating descriptions"):
    desc = create_description(artwork)
    descriptions.append(desc)

print(f"   ✓ Created {len(descriptions):,} descriptions")
print()
print("   Sample description:")
print(f"   {descriptions[0][:200]}...")
print()

# Create embeddings using neural network
print("4. Creating neural network embeddings...")
print("   Loading sentence transformer model...")

model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast and good quality
print("   ✓ Model loaded")

print("   Encoding descriptions (this may take a few minutes)...")
embeddings = model.encode(
    descriptions,
    show_progress_bar=True,
    batch_size=32,
    convert_to_numpy=True
)

print(f"   ✓ Created embeddings: shape {embeddings.shape}")
print()

# Normalize embeddings for better similarity computation
print("5. Normalizing embeddings...")
embeddings_normalized = normalize(embeddings, norm='l2')
print("   ✓ Normalized")
print()

# Reduce dimensionality for visualization (optional but helpful)
print("6. Creating lower-dimensional representation...")
pca = PCA(n_components=50)  # Reduce to 50D for faster nearest neighbor search
embeddings_reduced = pca.fit_transform(embeddings_normalized)
print(f"   ✓ Reduced to {embeddings_reduced.shape[1]} dimensions")
print(f"   ✓ Explained variance: {pca.explained_variance_ratio_.sum():.2%}")
print()

# Save everything
print("7. Saving latent space...")
output_dir = Path('outputs/latent_space')
output_dir.mkdir(parents=True, exist_ok=True)

# Save embeddings
np.save(output_dir / 'embeddings_full.npy', embeddings_normalized)
np.save(output_dir / 'embeddings_reduced.npy', embeddings_reduced)

# Save artworks and descriptions
with open(output_dir / 'artworks.json', 'w') as f:
    json.dump(valid_artworks, f)

with open(output_dir / 'descriptions.json', 'w') as f:
    json.dump(descriptions, f)

# Save PCA model
with open(output_dir / 'pca_model.pkl', 'wb') as f:
    pickle.dump(pca, f)

# Save metadata
metadata = {
    'n_artworks': len(valid_artworks),
    'embedding_dim_full': embeddings_normalized.shape[1],
    'embedding_dim_reduced': embeddings_reduced.shape[1],
    'model_name': 'all-MiniLM-L6-v2',
    'pca_variance_explained': float(pca.explained_variance_ratio_.sum())
}

with open(output_dir / 'metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"   ✓ Saved to {output_dir}/")
print()

# Compute some statistics
print("8. Computing statistics...")

# Nationality distribution
nationalities = {}
for artwork in valid_artworks:
    if artwork.get('ConstituentID'):
        const_ids = artwork['ConstituentID']
        if isinstance(const_ids, list) and const_ids:
            artist_id = const_ids[0]
            if artist_id in artists:
                nat = artists[artist_id].get('Nationality', 'Unknown')
                nationalities[nat] = nationalities.get(nat, 0) + 1

top_nationalities = sorted(nationalities.items(), key=lambda x: x[1], reverse=True)[:10]

print("   Top 10 Nationalities:")
for nat, count in top_nationalities:
    pct = (count / len(valid_artworks)) * 100
    print(f"     {nat}: {count:,} ({pct:.1f}%)")

print()

# Gender distribution
genders = {}
for artwork in valid_artworks:
    if artwork.get('ConstituentID'):
        const_ids = artwork['ConstituentID']
        if isinstance(const_ids, list) and const_ids:
            artist_id = const_ids[0]
            if artist_id in artists:
                gender = artists[artist_id].get('Gender', 'Unknown')
                genders[gender] = genders.get(gender, 0) + 1

print("   Gender Distribution:")
for gender, count in sorted(genders.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(valid_artworks)) * 100
    print(f"     {gender}: {count:,} ({pct:.1f}%)")

print()

# Save statistics
stats = {
    'nationalities': dict(top_nationalities),
    'genders': genders,
    'total_artworks': len(valid_artworks)
}

with open(output_dir / 'statistics.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("=" * 70)
print("✓ LATENT SPACE BUILT SUCCESSFULLY!")
print("=" * 70)
print()
print(f"Artworks in latent space: {len(valid_artworks):,}")
print(f"Embedding dimensions: {embeddings_reduced.shape[1]}")
print()
print("Next step: Launch the interactive website")
print("  ./venv/bin/python app.py")
print()
