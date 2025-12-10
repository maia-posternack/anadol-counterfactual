#!/usr/bin/env python3
"""
What the Dream Obscures - Interactive Web Application

Flask backend for navigating MoMA's latent space and generating artwork visualizations.
"""

import json
import numpy as np
import pickle
from pathlib import Path
import os
from dotenv import load_dotenv
import io
import base64

from flask import Flask, render_template, jsonify, request
from sklearn.metrics.pairwise import cosine_similarity
import replicate

# For generating metadata visualizations
try:
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️  Warning: PIL/matplotlib not available for metadata visualizations")

# Load environment variables
load_dotenv()

# Set up Replicate API
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
if REPLICATE_API_TOKEN:
    os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN
    print(f"✓ Replicate API token loaded")
else:
    print("⚠️  Warning: No Replicate API token found in .env file")

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Load latent space
print("Loading latent space...")
LATENT_DIR = Path('outputs/latent_space')

embeddings = np.load(LATENT_DIR / 'embeddings_reduced.npy')
with open(LATENT_DIR / 'artworks.json', 'r') as f:
    artworks = json.load(f)
with open(LATENT_DIR / 'descriptions.json', 'r') as f:
    descriptions = json.load(f)
with open(LATENT_DIR / 'metadata.json', 'r') as f:
    metadata = json.load(f)

# Load artists for additional info
with open('data/artworks/moma_data/Artists.json', 'r') as f:
    artists_data = json.load(f)
artists = {a['ConstituentID']: a for a in artists_data}

print(f"✓ Loaded {len(artworks):,} artworks")
print(f"✓ Embedding dimensions: {embeddings.shape[1]}")
print()

# Cache for generated images
generated_images = {}


def get_artwork_details(idx):
    """Get full details for an artwork"""
    artwork = artworks[idx]
    details = {
        'index': idx,
        'title': artwork.get('Title', 'Untitled'),
        'artist': artwork.get('Artist', 'Unknown'),
        'date': artwork.get('Date', 'Unknown'),
        'medium': artwork.get('Medium', 'Unknown'),
        'dimensions': artwork.get('Dimensions', 'Unknown'),
        'classification': artwork.get('Classification', 'Unknown'),
        'department': artwork.get('Department', 'Unknown'),
        'date_acquired': artwork.get('DateAcquired', 'Unknown'),
        'credit_line': artwork.get('CreditLine', 'Unknown'),
        'description': descriptions[idx]
    }
    
    # Add artist details
    if artwork.get('ConstituentID'):
        const_ids = artwork['ConstituentID']
        if isinstance(const_ids, list) and const_ids:
            artist_id = const_ids[0]
            if artist_id in artists:
                artist = artists[artist_id]
                details['nationality'] = artist.get('Nationality', 'Unknown')
                details['gender'] = artist.get('Gender', 'Unknown')
                details['birth_year'] = artist.get('BeginDate', 'Unknown')
                details['death_year'] = artist.get('EndDate', 'Unknown')
    
    return details


def find_nearest_by_dimension(current_idx, dimension, k=5):
    """
    Find nearest artworks along a specific dimension.
    
    Dimensions:
    - 'similar': Overall similarity
    - 'nationality': Same nationality
    - 'medium': Same medium
    - 'era': Similar time period
    - 'department': Same department
    - 'gender': Same gender
    """
    current_artwork = artworks[current_idx]
    current_emb = embeddings[current_idx]
    
    candidates = []
    
    for idx in range(len(artworks)):
        if idx == current_idx:
            continue
        
        artwork = artworks[idx]
        
        # Filter by dimension
        if dimension == 'nationality':
            # Check if same nationality
            curr_nat = None
            if current_artwork.get('ConstituentID'):
                const_ids = current_artwork['ConstituentID']
                if isinstance(const_ids, list) and const_ids:
                    artist_id = const_ids[0]
                    if artist_id in artists:
                        curr_nat = artists[artist_id].get('Nationality')
            
            art_nat = None
            if artwork.get('ConstituentID'):
                const_ids = artwork['ConstituentID']
                if isinstance(const_ids, list) and const_ids:
                    artist_id = const_ids[0]
                    if artist_id in artists:
                        art_nat = artists[artist_id].get('Nationality')
            
            if not curr_nat or not art_nat or curr_nat != art_nat:
                continue
        
        elif dimension == 'medium':
            if artwork.get('Medium') != current_artwork.get('Medium'):
                continue
        
        elif dimension == 'department':
            if artwork.get('Department') != current_artwork.get('Department'):
                continue
        
        elif dimension == 'gender':
            curr_gender = None
            if current_artwork.get('ConstituentID'):
                const_ids = current_artwork['ConstituentID']
                if isinstance(const_ids, list) and const_ids:
                    artist_id = const_ids[0]
                    if artist_id in artists:
                        curr_gender = artists[artist_id].get('Gender')
            
            art_gender = None
            if artwork.get('ConstituentID'):
                const_ids = artwork['ConstituentID']
                if isinstance(const_ids, list) and const_ids:
                    artist_id = const_ids[0]
                    if artist_id in artists:
                        art_gender = artists[artist_id].get('Gender')
            
            if not curr_gender or not art_gender or curr_gender != art_gender:
                continue
        
        # Compute similarity
        sim = cosine_similarity([current_emb], [embeddings[idx]])[0][0]
        candidates.append((idx, float(sim)))
    
    # Sort by similarity and return top k
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:k]


def generate_latent_space_visualization(artwork_details, artwork_idx):
    """
    Generate a fast HTML/SVG visualization of the artwork's latent space position.
    Much faster than matplotlib - returns JSON data instead of rendering image.
    """
    try:
        # Get the embedding for this artwork
        embedding = embeddings[artwork_idx].tolist()
        
        # Return the raw embedding data as JSON
        # Frontend will render it quickly with Canvas/SVG
        return {
            'type': 'latent_data',
            'embedding': embedding,
            'index': artwork_idx,
            'title': artwork_details['title'],
            'artist': artwork_details['artist']
        }
    
    except Exception as e:
        print(f"[ERROR] Failed to get latent space data: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_gan_from_latent(artwork_details, artwork_idx):
    """
    Generate an abstract visualization from the latent vector itself.
    This mimics what Anadol does - pure latent space generation.
    Returns a data URL with generated abstract art.
    """
    print(f"[DEBUG] Generating GAN-style visualization from latent vector...")
    
    try:
        # Get the embedding for this artwork
        embedding = embeddings[artwork_idx]
        
        if not VISUALIZATION_AVAILABLE:
            return None
        
        # Create abstract "machine art" from the latent vector
        # This is what StyleGAN-style models actually output
        fig = plt.figure(figsize=(8, 8), facecolor='#0a0a0f')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0a0a0f')
        ax.axis('off')
        
        # Create abstract patterns from embedding
        # Method 1: Circular visualization (like Anadol's fluid dynamics)
        theta = np.linspace(0, 2*np.pi, len(embedding))
        r = np.abs(embedding)
        
        # Normalize for better visualization
        r_norm = (r - r.min()) / (r.max() - r.min() + 1e-8)
        
        # Create spiral pattern
        num_spirals = 5
        for i in range(num_spirals):
            offset = (i / num_spirals) * 2 * np.pi
            x = r_norm * np.cos(theta + offset)
            y = r_norm * np.sin(theta + offset)
            
            # Color based on embedding values
            colors = plt.cm.viridis(np.linspace(0, 1, len(embedding)))
            
            # Draw flowing lines
            for j in range(len(embedding)-1):
                alpha = 0.3 + 0.4 * r_norm[j]
                ax.plot([x[j], x[j+1]], [y[j], y[j+1]], 
                       color=colors[j], linewidth=2, alpha=alpha)
        
        # Add some visual complexity - scatter points
        scatter_size = r_norm * 100 + 10
        scatter = ax.scatter(x, y, c=range(len(embedding)), 
                           cmap='plasma', s=scatter_size, alpha=0.6, edgecolors='white', linewidth=0.5)
        
        # Set equal aspect and limits
        ax.set_aspect('equal')
        max_r = r_norm.max()
        ax.set_xlim(-max_r*1.2, max_r*1.2)
        ax.set_ylim(-max_r*1.2, max_r*1.2)
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor='#0a0a0f', 
                   edgecolor='none', bbox_inches='tight', dpi=150, pad_inches=0)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        print(f"[SUCCESS] Generated GAN-style visualization from latent vector")
        return f"data:image/png;base64,{image_base64}"
    
    except Exception as e:
        print(f"[ERROR] Failed to generate GAN visualization: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_artwork_image(artwork_details, use_ai=True):
    """
    Generate an image from artwork metadata.
    
    Args:
        artwork_details: Artwork metadata dict
        use_ai: If True, try Replicate AI. If False, use latent space viz only.
    """
    
    print("\n" + "="*70)
    print("GENERATE_ARTWORK_IMAGE DEBUG")
    print("="*70)
    
    # Check cache
    cache_key = artwork_details['index']
    print(f"[DEBUG] Cache key: {cache_key}")
    if cache_key in generated_images:
        cached_value = generated_images[cache_key]
        print(f"[DEBUG] Found in cache, type: {type(cached_value)}")
        
        # Handle different cached value types
        if isinstance(cached_value, dict):
            # It's latent data - return as is
            print(f"[DEBUG] Returning cached latent data")
            return cached_value
        elif hasattr(cached_value, 'url'):
            # Convert FileOutput to string
            cached_value = str(cached_value.url)
            generated_images[cache_key] = cached_value
            print(f"[DEBUG] Converted cached FileOutput to URL: {cached_value}")
        elif not isinstance(cached_value, str):
            # Convert to string
            cached_value = str(cached_value)
            generated_images[cache_key] = cached_value
            print(f"[DEBUG] Converted cached value to string: {cached_value}")
        
        print(f"[DEBUG] Returning cached value")
        return cached_value
    
    # Try latent space visualization first (free and conceptually aligned)
    if not use_ai:
        print(f"[DEBUG] Generating latent space data (no AI)...")
        viz_data = generate_latent_space_visualization(artwork_details, cache_key)
        if viz_data:
            # Don't cache - generate fresh each time (it's fast)
            print(f"[SUCCESS] Generated latent space data: {type(viz_data)}")
            print("="*70 + "\n")
            return viz_data
    
    # Create prompt from metadata
    prompt = f"An artwork titled '{artwork_details['title']}' by {artwork_details['artist']}"
    
    if artwork_details.get('nationality') and artwork_details['nationality'] != 'Unknown':
        prompt += f" ({artwork_details['nationality']} artist)"
    
    if artwork_details.get('date') and artwork_details['date'] != 'Unknown':
        prompt += f", created in {artwork_details['date']}"
    
    if artwork_details.get('medium') and artwork_details['medium'] != 'Unknown':
        prompt += f", using {artwork_details['medium']}"
    
    if artwork_details.get('classification') and artwork_details['classification'] != 'Unknown':
        prompt += f", classified as {artwork_details['classification']}"
    
    prompt += ". Museum quality, high resolution, professional photography."
    
    print(f"[DEBUG] Full prompt: {prompt}")
    print(f"[DEBUG] Prompt length: {len(prompt)} characters")
    
    try:
        # Check if API token is available
        print(f"[DEBUG] Checking API token...")
        print(f"[DEBUG] Token exists: {bool(REPLICATE_API_TOKEN)}")
        if REPLICATE_API_TOKEN:
            print(f"[DEBUG] Token prefix: {REPLICATE_API_TOKEN[:10]}...")
        
        if not REPLICATE_API_TOKEN:
            print("[ERROR] No Replicate API token configured")
            return None
        
        # TEXT-TO-IMAGE MODEL OPTIONS
        # Note: StyleGAN2 (what Anadol uses) doesn't take text - it uses latent vectors
        # These models take text and generate images (diffusion models)
        
        # CURRENT: FLUX Schnell (fast, good quality, cheap)
        model = "black-forest-labs/flux-schnell"
        model_input = {
            "prompt": prompt,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "jpg",
            "output_quality": 80
        }
        
        # ALTERNATIVE 1: Stable Diffusion XL (slower but good)
        # model = "stability-ai/sdxl"
        # model_input = {
        #     "prompt": prompt,
        #     "width": 1024,
        #     "height": 1024,
        #     "num_outputs": 1
        # }
        
        # ALTERNATIVE 2: Playground v2.5 (Midjourney-style)
        # model = "playgroundai/playground-v2.5-1024px-aesthetic"
        # model_input = {
        #     "prompt": prompt,
        #     "width": 1024,
        #     "height": 1024
        # }
        
        print(f"[DEBUG] Calling replicate.run()...")
        print(f"[DEBUG] Model: {model}")
        print(f"[DEBUG] Input parameters: {model_input}")
        
        output = replicate.run(model, input=model_input)
        
        print(f"[DEBUG] replicate.run() completed successfully")
        print(f"[DEBUG] Output type: {type(output)}")
        print(f"[DEBUG] Output repr: {repr(output)}")
        
        # Get the image URL - Replicate can return different types
        raw_output = None
        if isinstance(output, list) and len(output) > 0:
            raw_output = output[0]
            print(f"[DEBUG] Extracted from list, type: {type(raw_output)}")
        else:
            raw_output = output
            print(f"[DEBUG] Using output directly, type: {type(raw_output)}")
        
        # Convert FileOutput or other objects to string URL
        image_url = None
        if hasattr(raw_output, 'url'):
            # FileOutput object has a .url attribute
            image_url = str(raw_output.url)
            print(f"[DEBUG] Extracted URL from FileOutput.url: {image_url}")
        elif isinstance(raw_output, str):
            image_url = raw_output
            print(f"[DEBUG] Already a string: {image_url}")
        else:
            # Try to convert to string directly
            image_url = str(raw_output)
            print(f"[DEBUG] Converted to string: {image_url}")
        
        # Ensure we have a valid string
        if not isinstance(image_url, str):
            print(f"[ERROR] image_url is not a string: {type(image_url)}")
            return None
        
        # Cache the string URL
        generated_images[cache_key] = image_url
        print(f"[DEBUG] Cached image URL (string) for key {cache_key}")
        
        print(f"[SUCCESS] Generated image URL: {image_url}")
        print("="*70 + "\n")
        return image_url
    
    except Exception as e:
        print(f"[ERROR] Exception occurred: {type(e).__name__}")
        print(f"[ERROR] Error message: {e}")
        print(f"[ERROR] Full traceback:")
        import traceback
        traceback.print_exc()
        
        # Check if it's an insufficient credit error - use latent space viz as fallback
        if "Insufficient credit" in str(e) or "402" in str(e):
            print("[INFO] Insufficient Replicate credits. Falling back to latent space data.")
            viz_data = generate_latent_space_visualization(artwork_details, cache_key)
            if viz_data:
                print(f"[SUCCESS] Generated latent space data as fallback: {type(viz_data)}")
                print("="*70 + "\n")
                return viz_data
        
        print("="*70 + "\n")
        return None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         total_artworks=len(artworks),
                         metadata=metadata)


@app.route('/api/random')
def random_artwork():
    """Get a random starting artwork"""
    idx = np.random.randint(0, len(artworks))
    details = get_artwork_details(idx)
    return jsonify(details)


@app.route('/api/artwork/<int:idx>')
def get_artwork(idx):
    """Get details for a specific artwork"""
    if idx < 0 or idx >= len(artworks):
        return jsonify({'error': 'Invalid index'}), 400
    
    details = get_artwork_details(idx)
    return jsonify(details)


@app.route('/api/navigate', methods=['POST'])
def navigate():
    """Navigate from current artwork along a dimension"""
    data = request.json
    current_idx = data.get('current_idx')
    dimension = data.get('dimension', 'similar')
    k = data.get('k', 5)
    
    if current_idx is None or current_idx < 0 or current_idx >= len(artworks):
        return jsonify({'error': 'Invalid current index'}), 400
    
    # Find nearest neighbors
    neighbors = find_nearest_by_dimension(current_idx, dimension, k)
    
    # Get details for each neighbor
    results = []
    for idx, similarity in neighbors:
        details = get_artwork_details(idx)
        details['similarity'] = similarity
        results.append(details)
    
    return jsonify({
        'dimension': dimension,
        'neighbors': results
    })


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate an image for an artwork"""
    print("\n" + "="*70)
    print("/API/GENERATE ENDPOINT CALLED")
    print("="*70)
    
    try:
        data = request.json
        print(f"[DEBUG] Request data: {data}")
        
        idx = data.get('idx')
        use_ai = data.get('use_ai', True)  # Default to AI if not specified
        print(f"[DEBUG] Artwork index: {idx}")
        print(f"[DEBUG] Use AI: {use_ai}")
        
        if idx is None or idx < 0 or idx >= len(artworks):
            print(f"[ERROR] Invalid index: {idx} (must be 0-{len(artworks)-1})")
            return jsonify({'error': 'Invalid index'}), 400
        
        print(f"[DEBUG] Getting artwork details for index {idx}...")
        details = get_artwork_details(idx)
        print(f"[DEBUG] Artwork details: {details.get('title')} by {details.get('artist')}")
        
        print(f"[DEBUG] Calling generate_artwork_image()...")
        result = generate_artwork_image(details, use_ai=use_ai)
        
        if result:
            print(f"[SUCCESS] Image generated successfully")
            
            # Check if it's latent data (dict) or URL (string)
            if isinstance(result, dict) and result.get('type') == 'latent_data':
                print(f"[DEBUG] Generated latent data structure")
                print("="*70 + "\n")
                return jsonify({'latent_data': result})
            else:
                # It's a URL string
                result_str = str(result)
                if result_str.startswith('data:'):
                    print(f"[DEBUG] Generated base64 image")
                else:
                    print(f"[DEBUG] Generated URL: {result_str[:100]}...")
                print("="*70 + "\n")
                return jsonify({'image_url': result_str})
        else:
            print(f"[ERROR] generate_artwork_image() returned None")
            print("="*70 + "\n")
            return jsonify({'error': 'Failed to generate image. Check server logs for details.'}), 500
    except Exception as e:
        print(f"[ERROR] Exception in /api/generate endpoint: {type(e).__name__}")
        print(f"[ERROR] Error message: {e}")
        import traceback
        traceback.print_exc()
        print("="*70 + "\n")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/generate-gan', methods=['POST'])
def generate_gan():
    """Generate GAN-style visualization from latent vector"""
    print("\n" + "="*70)
    print("/API/GENERATE-GAN ENDPOINT CALLED")
    print("="*70)
    
    try:
        data = request.json
        idx = data.get('idx')
        
        print(f"[DEBUG] Artwork index: {idx}")
        
        if idx is None or idx < 0 or idx >= len(artworks):
            print(f"[ERROR] Invalid index: {idx}")
            return jsonify({'error': 'Invalid index'}), 400
        
        print(f"[DEBUG] Getting artwork details...")
        details = get_artwork_details(idx)
        
        print(f"[DEBUG] Generating GAN visualization from latent vector...")
        image_url = generate_gan_from_latent(details, idx)
        
        if image_url:
            print(f"[SUCCESS] Generated GAN visualization")
            print("="*70 + "\n")
            return jsonify({'image_url': image_url})
        else:
            print(f"[ERROR] Failed to generate GAN visualization")
            print("="*70 + "\n")
            return jsonify({'error': 'Failed to generate GAN visualization'}), 500
            
    except Exception as e:
        print(f"[ERROR] Exception in /api/generate-gan: {type(e).__name__}")
        print(f"[ERROR] Error message: {e}")
        import traceback
        traceback.print_exc()
        print("="*70 + "\n")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/test-replicate')
def test_replicate():
    """Test if Replicate API is working"""
    if not REPLICATE_API_TOKEN:
        return jsonify({'error': 'No API token configured'}), 500
    
    try:
        # Try a simple API call
        import replicate
        # Just check if we can access the API
        return jsonify({
            'status': 'ok',
            'message': 'Replicate API token is valid',
            'token_prefix': REPLICATE_API_TOKEN[:8] + '...'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Replicate API test failed'
        }), 500


@app.route('/api/stats', methods=['POST'])
def get_stats():
    """Get statistics for a path through the collection"""
    data = request.json
    path_indices = data.get('path', [])
    
    if not path_indices:
        return jsonify({'error': 'No path provided'}), 400
    
    # Compute statistics
    nationalities = {}
    genders = {}
    departments = {}
    decades = {}
    
    for idx in path_indices:
        if idx < 0 or idx >= len(artworks):
            continue
        
        artwork = artworks[idx]
        
        # Nationality
        if artwork.get('ConstituentID'):
            const_ids = artwork['ConstituentID']
            if isinstance(const_ids, list) and const_ids:
                artist_id = const_ids[0]
                if artist_id in artists:
                    nat = artists[artist_id].get('Nationality', 'Unknown')
                    nationalities[nat] = nationalities.get(nat, 0) + 1
                    
                    gender = artists[artist_id].get('Gender', 'Unknown')
                    genders[gender] = genders.get(gender, 0) + 1
        
        # Department
        dept = artwork.get('Department', 'Unknown')
        departments[dept] = departments.get(dept, 0) + 1
        
        # Decade (from date acquired)
        date_acq = artwork.get('DateAcquired', '')
        if date_acq and len(date_acq) >= 4:
            try:
                year = int(date_acq[:4])
                decade = (year // 10) * 10
                decades[str(decade)] = decades.get(str(decade), 0) + 1
            except:
                pass
    
    # Calculate percentages
    total = len(path_indices)
    
    stats = {
        'total_artworks': total,
        'nationalities': {k: {'count': v, 'percent': (v/total)*100} 
                         for k, v in sorted(nationalities.items(), key=lambda x: x[1], reverse=True)},
        'genders': {k: {'count': v, 'percent': (v/total)*100} 
                   for k, v in sorted(genders.items(), key=lambda x: x[1], reverse=True)},
        'departments': {k: {'count': v, 'percent': (v/total)*100} 
                       for k, v in sorted(departments.items(), key=lambda x: x[1], reverse=True)},
        'acquisition_decades': {k: {'count': v, 'percent': (v/total)*100} 
                               for k, v in sorted(decades.items())}
    }
    
    return jsonify(stats)


if __name__ == '__main__':
    print()
    print("=" * 70)
    print("WHAT THE DREAM OBSCURES")
    print("A Counterfactual Exploration of MoMA's Archive")
    print("=" * 70)
    print()
    print(f"Loaded {len(artworks):,} artworks in latent space")
    print()
    print("Starting server...")
    port = int(os.getenv('PORT', 5001))
    print(f"Open: http://localhost:{port}")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=False)
