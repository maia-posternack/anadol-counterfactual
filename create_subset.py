#!/usr/bin/env python3
"""
Create a smaller subset of the latent space for Vercel deployment
Reduces from ~150k to 10k artworks to stay under size limits
"""

import json
import numpy as np
import pickle
from pathlib import Path

# Configuration
SUBSET_SIZE = 10000  # Reduce to 10k artworks
LATENT_DIR = Path('outputs/latent_space')
SUBSET_DIR = Path('outputs/latent_space_subset')

print(f"Creating subset of {SUBSET_SIZE} artworks...")

# Create subset directory
SUBSET_DIR.mkdir(parents=True, exist_ok=True)

# Load original data
print("Loading original embeddings...")
embeddings_full = np.load(LATENT_DIR / 'embeddings_full.npy')
embeddings_reduced = np.load(LATENT_DIR / 'embeddings_reduced.npy')

print(f"Original size: {len(embeddings_full)} artworks")

# Load JSON data
with open(LATENT_DIR / 'artworks.json', 'r') as f:
    artworks = json.load(f)

with open(LATENT_DIR / 'descriptions.json', 'r') as f:
    descriptions = json.load(f)

# Create random subset (or first N for consistency)
indices = np.random.choice(len(embeddings_full), SUBSET_SIZE, replace=False)
indices = np.sort(indices)  # Keep sorted for consistency

# Subset embeddings
print("Creating subset embeddings...")
embeddings_full_subset = embeddings_full[indices]
embeddings_reduced_subset = embeddings_reduced[indices]

# Subset JSON data
print("Creating subset JSON data...")
artworks_subset = [artworks[i] for i in indices]
descriptions_subset = [descriptions[i] for i in indices]

# Save subset
print("Saving subset...")
np.save(SUBSET_DIR / 'embeddings_full.npy', embeddings_full_subset)
np.save(SUBSET_DIR / 'embeddings_reduced.npy', embeddings_reduced_subset)

with open(SUBSET_DIR / 'artworks.json', 'w') as f:
    json.dump(artworks_subset, f)

with open(SUBSET_DIR / 'descriptions.json', 'w') as f:
    json.dump(descriptions_subset, f)

# Copy other files
print("Copying metadata files...")
import shutil
for file in ['metadata.json', 'statistics.json', 'pca_model.pkl']:
    src = LATENT_DIR / file
    if src.exists():
        shutil.copy(src, SUBSET_DIR / file)

# Update metadata
metadata_path = SUBSET_DIR / 'metadata.json'
if metadata_path.exists():
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    metadata['num_artworks'] = SUBSET_SIZE
    metadata['note'] = f'Subset of {SUBSET_SIZE} artworks for deployment'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

# Print sizes
import os
subset_size = sum(f.stat().st_size for f in SUBSET_DIR.glob('**/*') if f.is_file())
print(f"\n✓ Subset created successfully!")
print(f"  Original: {len(embeddings_full)} artworks")
print(f"  Subset: {SUBSET_SIZE} artworks")
print(f"  Subset directory size: {subset_size / 1024 / 1024:.1f} MB")
print(f"  Location: {SUBSET_DIR}")

