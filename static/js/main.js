// What the Dream Obscures - Graph Visualization & Navigation

let currentArtwork = null;
let path = [];  // Array of {idx, artwork, latent_data, latent_url, ai_url, gan_url}
let visitedEdges = new Set();  // Set of "idx1->idx2" strings
let network = null;
let networkData = { nodes: [], edges: [] };
let currentNeighbors = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Start button
    document.getElementById('startBtn').addEventListener('click', startExploring);
    
    // Control buttons
    document.getElementById('aboutBtn')?.addEventListener('click', showAbout);
    document.getElementById('showStatsBtn').addEventListener('click', showStatistics);
    document.getElementById('resetBtn').addEventListener('click', resetExploration);
    document.getElementById('closeStats')?.addEventListener('click', () => {
        document.getElementById('statsOverlay').style.display = 'none';
    });
    document.getElementById('closeAbout')?.addEventListener('click', () => {
        document.getElementById('aboutOverlay').style.display = 'none';
    });
    
    // Transparency toggle
    document.getElementById('toggleTransparency')?.addEventListener('click', () => {
        const content = document.getElementById('transparencyContent');
        const button = document.getElementById('toggleTransparency');
        const icon = button.querySelector('.toggle-icon');
        const text = button.querySelector('.toggle-text');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            icon.textContent = '⊖';
            text.textContent = 'Conceal the Machinery';
        } else {
            content.style.display = 'none';
            icon.textContent = '⊕';
            text.textContent = 'Reveal the Machinery';
        }
    });
}

function showAbout() {
    document.getElementById('aboutOverlay').style.display = 'flex';
}

async function startExploring() {
    showLoading('Entering the latent space...');
    
    try {
        const response = await fetch('/api/random');
        const artwork = await response.json();
        
        currentArtwork = artwork;
        path = [{
            idx: artwork.index,
            artwork: artwork,
            latent_data: null,
            latent_url: null,
            ai_url: null,
            gan_url: null
        }];
        
        // Hide start screen, show explorer IMMEDIATELY
        document.getElementById('startScreen').style.display = 'none';
        document.getElementById('mainExplorer').style.display = 'flex';
        hideLoading();
        
        // Initialize network
        initializeNetwork();
        
        // Load the artwork (non-blocking)
        loadArtwork(artwork);
        
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        alert('Error loading artwork. Please try again.');
    }
}

function initializeNetwork() {
    const container = document.getElementById('network');
    
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#ffffff',
                face: 'Inter'
            },
            borderWidth: 2,
            borderWidthSelected: 4,
            color: {
                border: '#00ff88',
                background: '#1a1a28',
                highlight: {
                    border: '#ff0088',
                    background: '#2a2a38'
                }
            }
        },
        edges: {
            width: 2,
            color: {
                color: '#2a2a3a',
                highlight: '#00ff88',
                hover: '#00aaff'
            },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            },
            font: {
                size: 11,
                color: '#b0b0c8',
                strokeWidth: 0,
                face: 'Inter'
            },
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 0.5
                }
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.3,
                springLength: 200,
                springConstant: 0.05
            },
            stabilization: {
                iterations: 100
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            zoomView: true,
            dragView: true
        }
    };
    
    networkData = { nodes: new vis.DataSet(), edges: new vis.DataSet() };
    network = new vis.Network(container, networkData, options);
    
    // Handle node clicks
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            selectArtworkFromGraph(nodeId);
        }
    });
}

function loadArtwork(artwork) {
    // Update current artwork
    currentArtwork = artwork;
    
    // Display metadata and prompt IMMEDIATELY
    displayMetadata(artwork);
    
    // Clear visualizations with placeholders IMMEDIATELY
    document.getElementById('aiViz').innerHTML = '<div class="viz-placeholder viz-loading">Generating text-to-image...</div>';
    document.getElementById('ganViz').innerHTML = '<div class="viz-placeholder viz-loading">Generating from latent vector...</div>';
    document.getElementById('latentViz').innerHTML = '<div class="viz-placeholder viz-loading">Loading latent space...</div>';
    
    // Update path history IMMEDIATELY
    updatePathHistory();
    
    // Everything below happens in background, non-blocking
    updateGraph(artwork);
    generateAllVisualizations(artwork);
}

async function generateAllVisualizations(artwork) {
    // Generate latent space viz (for transparency section)
    try {
        const latentResponse = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idx: artwork.index, use_ai: false})
        });
        
        const latentData = await latentResponse.json();
        
        if (latentData.latent_data) {
            // Render latent data fast with canvas
            renderLatentData(latentData.latent_data, 'latentViz');
            
            // Update path
            const pathItem = path.find(p => p.idx === artwork.index);
            if (pathItem) pathItem.latent_data = latentData.latent_data;
        } else if (latentData.image_url) {
            document.getElementById('latentViz').innerHTML = `<img src="${latentData.image_url}" alt="Latent space visualization">`;
            
            const pathItem = path.find(p => p.idx === artwork.index);
            if (pathItem) pathItem.latent_url = latentData.image_url;
        }
    } catch (error) {
        console.error('Error generating latent viz:', error);
        document.getElementById('latentViz').innerHTML = '<div class="viz-placeholder">Failed to generate</div>';
    }
    
    // Generate text-to-image AI viz
    try {
        const aiResponse = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idx: artwork.index, use_ai: true})
        });
        
        const aiData = await aiResponse.json();
        
        if (aiData.latent_data) {
            // AI generation failed, got latent data fallback
            console.log('AI generation unavailable, showing latent data');
            document.getElementById('aiViz').innerHTML = '<div class="viz-placeholder">AI credits exhausted<br><small>Add credits at replicate.com</small></div>';
        } else if (aiData.image_url) {
            document.getElementById('aiViz').innerHTML = `<img src="${aiData.image_url}" alt="Text-to-image AI">`;
            
            // Update path with AI URL
            const pathItem = path.find(p => p.idx === artwork.index);
            if (pathItem) pathItem.ai_url = aiData.image_url;
            
            updatePathHistory();
        }
    } catch (error) {
        console.error('Error generating AI viz:', error);
        document.getElementById('aiViz').innerHTML = '<div class="viz-placeholder">Failed to generate<br><small>(may need credits)</small></div>';
    }
    
    // Generate GAN from latent vector
    try {
        const ganResponse = await fetch('/api/generate-gan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idx: artwork.index})
        });
        
        const ganData = await ganResponse.json();
        
        if (ganData.image_url) {
            document.getElementById('ganViz').innerHTML = `<img src="${ganData.image_url}" alt="GAN from latent vector">`;
            
            // Update path with GAN URL
            const pathItem = path.find(p => p.idx === artwork.index);
            if (pathItem) pathItem.gan_url = ganData.image_url;
            
            updatePathHistory();
        } else {
            document.getElementById('ganViz').innerHTML = '<div class="viz-placeholder">Failed to generate GAN visualization</div>';
        }
    } catch (error) {
        console.error('Error generating GAN viz:', error);
        document.getElementById('ganViz').innerHTML = '<div class="viz-placeholder">Failed to generate<br><small>Server error</small></div>';
    }
}

function renderLatentData(data, containerId) {
    const container = document.getElementById(containerId);
    const embedding = data.embedding;
    
    // Determine canvas size based on container
    const isSmall = containerId === 'latentViz'; // Small version in transparency section
    const width = isSmall ? 600 : 800;
    const height = isSmall ? 250 : 600;
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    // Dark background
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw bar chart
    const barWidth = canvas.width / embedding.length;
    const maxVal = Math.max(...embedding.map(Math.abs));
    const centerY = canvas.height / 2;
    const scale = (canvas.height * 0.4) / maxVal;
    
    embedding.forEach((val, i) => {
        // Color gradient
        const hue = (i / embedding.length) * 360;
        ctx.fillStyle = `hsl(${hue}, 80%, 60%)`;
        
        // Draw bar
        const barHeight = val * scale;
        const x = i * barWidth;
        const y = barHeight > 0 ? centerY - barHeight : centerY;
        
        ctx.fillRect(x, y, barWidth - 1, Math.abs(barHeight));
    });
    
    // Add text overlay
    const fontSize = isSmall ? 12 : 14;
    ctx.fillStyle = '#00ff88';
    ctx.font = `${fontSize}px monospace`;
    ctx.fillText(`${embedding.length}D Latent Space`, 10, 25);
    ctx.fillStyle = '#b0b0c8';
    ctx.font = `${fontSize - 2}px monospace`;
    ctx.fillText(`Index: ${data.index}`, 10, 45);
    
    if (!isSmall) {
        // Add more detail for large version
        ctx.fillText(`Min: ${Math.min(...embedding).toFixed(3)}  Max: ${Math.max(...embedding).toFixed(3)}`, 10, 65);
    }
    
    // Replace container content
    container.innerHTML = '';
    container.appendChild(canvas);
}

function displayMetadata(artwork) {
    // Create metadata for transparency section
    const metaHTML = `
        <div class="meta-item">
            <div class="meta-label">Title</div>
            <div class="meta-value">${artwork.title}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Artist</div>
            <div class="meta-value">${artwork.artist}</div>
        </div>
        ${artwork.nationality !== 'Unknown' ? `
        <div class="meta-item">
            <div class="meta-label">Nationality</div>
            <div class="meta-value">${artwork.nationality}</div>
        </div>` : ''}
        ${artwork.gender !== 'Unknown' ? `
        <div class="meta-item">
            <div class="meta-label">Gender</div>
            <div class="meta-value">${artwork.gender}</div>
        </div>` : ''}
        ${artwork.birth_year !== 'Unknown' ? `
        <div class="meta-item">
            <div class="meta-label">Artist Born</div>
            <div class="meta-value">${artwork.birth_year}</div>
        </div>` : ''}
        <div class="meta-item">
            <div class="meta-label">Date Created</div>
            <div class="meta-value">${artwork.date}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Medium</div>
            <div class="meta-value">${artwork.medium}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Dimensions</div>
            <div class="meta-value">${artwork.dimensions}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Classification</div>
            <div class="meta-value">${artwork.classification}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Department</div>
            <div class="meta-value">${artwork.department}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Date Acquired</div>
            <div class="meta-value">${artwork.date_acquired}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Credit Line</div>
            <div class="meta-value">${artwork.credit_line}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Latent Space Index</div>
            <div class="meta-value">${artwork.index} of 158,822</div>
        </div>
    `;
    
    document.getElementById('metadataDisplay').innerHTML = metaHTML;
    
    // Generate the prompt that will be sent to AI
    const aiPrompt = generatePromptForDisplay(artwork);
    document.getElementById('aiPrompt').textContent = aiPrompt;
}

function generatePromptForDisplay(artwork) {
    // This matches the backend prompt generation
    let prompt = `An artwork titled '${artwork.title}' by ${artwork.artist}`;
    
    if (artwork.nationality && artwork.nationality !== 'Unknown') {
        prompt += ` (${artwork.nationality} artist)`;
    }
    
    if (artwork.date && artwork.date !== 'Unknown') {
        prompt += `, created in ${artwork.date}`;
    }
    
    if (artwork.medium && artwork.medium !== 'Unknown') {
        prompt += `, using ${artwork.medium}`;
    }
    
    if (artwork.classification && artwork.classification !== 'Unknown') {
        prompt += `, classified as ${artwork.classification}`;
    }
    
    prompt += ". Museum quality, high resolution, professional photography.";
    
    return prompt;
}

function updateGraph(artwork) {
    const currentNodeId = `art_${artwork.index}`;
    
    // Update current node style IMMEDIATELY (visual feedback)
    if (!networkData.nodes.get(currentNodeId)) {
        networkData.nodes.add({
            id: currentNodeId,
            label: artwork.title.length > 30 ? artwork.title.substring(0, 30) + '...' : artwork.title,
            title: `${artwork.title}\n${artwork.artist}`,
            size: 25,
            color: {
                border: '#ff0088',
                background: '#2a2a38'
            }
        });
    } else {
        networkData.nodes.update({
            id: currentNodeId,
            size: 25,
            color: {
                border: '#ff0088',
                background: '#2a2a38'
            }
        });
    }
    
    // Focus on current node IMMEDIATELY
    network.focus(currentNodeId, {
        scale: 1.2,
        animation: {
            duration: 800,
            easingFunction: 'easeInOutQuad'
        }
    });
    
    // Fetch neighbors in background (truly non-blocking now)
    fetchNeighborsInBackground(artwork, currentNodeId);
}

async function fetchNeighborsInBackground(artwork, currentNodeId) {
    currentNeighbors = [];
    const seenNeighbors = new Set();
    
    try {
        const response = await fetch('/api/navigate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                current_idx: artwork.index,
                dimension: 'similar',
                k: 10
            })
        });
        
        const data = await response.json();
        
        if (data.neighbors && data.neighbors.length > 0) {
            data.neighbors.forEach((neighbor, idx) => {
                if (seenNeighbors.has(neighbor.index)) return;
                seenNeighbors.add(neighbor.index);
                
                const neighborId = `art_${neighbor.index}`;
                const edgeId = `${currentNodeId}_${neighborId}`;
                
                // Add neighbor node
                if (!networkData.nodes.get(neighborId)) {
                    networkData.nodes.add({
                        id: neighborId,
                        label: neighbor.title.length > 25 ? neighbor.title.substring(0, 25) + '...' : neighbor.title,
                        title: `${neighbor.title}\n${neighbor.artist}\n${neighbor.nationality || ''}\nSimilarity: ${(neighbor.similarity * 100).toFixed(1)}%\n\nClick to navigate`,
                        size: 15,
                        color: {
                            border: '#00ff88',
                            background: '#1a1a28'
                        }
                    });
                }
                
                // Add edge
                const edgeKey = `${artwork.index}->${neighbor.index}`;
                const isVisited = visitedEdges.has(edgeKey);
                
                if (!networkData.edges.get(edgeId)) {
                    networkData.edges.add({
                        id: edgeId,
                        from: currentNodeId,
                        to: neighborId,
                        label: `${(neighbor.similarity * 100).toFixed(0)}%`,
                        color: isVisited ? {color: '#00ff88', highlight: '#00ff88'} : {color: '#2a2a3a', highlight: '#00aaff'},
                        width: isVisited ? 3 : 2,
                        data: {
                            similarity: neighbor.similarity,
                            visited: isVisited
                        }
                    });
                }
                
                currentNeighbors.push({...neighbor, dimension: 'similar'});
            });
        }
    } catch (error) {
        console.error(`Error loading neighbors:`, error);
    }
}

function getDimensionLabel(dimension) {
    const labels = {
        'similar': 'Similar',
        'nationality': 'Nationality',
        'medium': 'Medium',
        'department': 'Dept',
        'gender': 'Gender'
    };
    return labels[dimension] || dimension;
}

function selectArtworkFromGraph(nodeId) {
    const idx = parseInt(nodeId.replace('art_', ''));
    
    // Find the artwork in neighbors
    const neighbor = currentNeighbors.find(n => n.index === idx);
    
    if (!neighbor) {
        console.log('Not a neighbor, ignoring click');
        return;
    }
    
    // Mark edge as visited IMMEDIATELY
    const edgeKey = `${currentArtwork.index}->${idx}`;
    visitedEdges.add(edgeKey);
    
    // Update edge color IMMEDIATELY
    const edgeId = `art_${currentArtwork.index}_art_${idx}`;
    if (networkData.edges.get(edgeId)) {
        networkData.edges.update({
            id: edgeId,
            color: {color: '#00ff88', highlight: '#00ff88'},
            width: 3
        });
    }
    
    // Update current node style IMMEDIATELY
    const currentNodeId = `art_${currentArtwork.index}`;
    networkData.nodes.update({
        id: currentNodeId,
        size: 15,
        color: {
            border: '#00ff88',
            background: '#1a1a28'
        }
    });
    
    // Update clicked node to current style IMMEDIATELY
    networkData.nodes.update({
        id: nodeId,
        size: 25,
        color: {
            border: '#ff0088',
            background: '#2a2a38'
        }
    });
    
    // Focus on new node IMMEDIATELY
    network.focus(nodeId, {
        scale: 1.2,
        animation: {
            duration: 500,
            easingFunction: 'easeInOutQuad'
        }
    });
    
    // Add to path
    path.push({
        idx: neighbor.index,
        artwork: neighbor,
        latent_data: null,
        latent_url: null,
        ai_url: null,
        gan_url: null
    });
    
    // Load new artwork - non-blocking, happens in background
    loadArtwork(neighbor);
}

function updatePathHistory() {
    const container = document.getElementById('pathHistory');
    
    container.innerHTML = path.map((item, idx) => {
        const isCurrent = idx === path.length - 1;
        
        // Prefer AI image, fallback to placeholder
        let imgUrl = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="%231a1a28" width="100" height="100"/></svg>';
        
        if (item.ai_url) {
            imgUrl = item.ai_url;
        } else if (item.latent_data) {
            // Create tiny canvas thumbnail for latent data
            imgUrl = createLatentThumbnail(item.latent_data);
        } else if (item.latent_url) {
            imgUrl = item.latent_url;
        }
        
        return `
            <div class="path-item ${isCurrent ? 'current' : ''}" data-idx="${idx}">
                <div class="path-item-number">${idx + 1}</div>
                <img src="${imgUrl}" alt="${item.artwork.title}">
            </div>
        `;
    }).join('');
    
    // Add click handlers
    container.querySelectorAll('.path-item').forEach((el, idx) => {
        if (idx < path.length - 1) {  // Don't allow clicking current
            el.addEventListener('click', () => goToPathIndex(idx));
        }
    });
}

function createLatentThumbnail(data) {
    const canvas = document.createElement('canvas');
    canvas.width = 80;
    canvas.height = 80;
    const ctx = canvas.getContext('2d');
    
    // Dark background
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, 80, 80);
    
    // Draw simplified bars
    const embedding = data.embedding;
    const barWidth = 80 / embedding.length;
    const maxVal = Math.max(...embedding.map(Math.abs));
    const centerY = 40;
    const scale = 30 / maxVal;
    
    embedding.forEach((val, i) => {
        const hue = (i / embedding.length) * 360;
        ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
        const barHeight = val * scale;
        const y = barHeight > 0 ? centerY - barHeight : centerY;
        ctx.fillRect(i * barWidth, y, barWidth, Math.abs(barHeight));
    });
    
    return canvas.toDataURL();
}

function goToPathIndex(idx) {
    if (idx >= path.length - 1) return;
    
    const item = path[idx];
    
    // Update current artwork IMMEDIATELY
    currentArtwork = item.artwork;
    
    // Display metadata IMMEDIATELY
    displayMetadata(item.artwork);
    
    // Show cached visualizations IMMEDIATELY
    if (item.latent_data) {
        renderLatentData(item.latent_data, 'latentViz');
    } else if (item.latent_url) {
        document.getElementById('latentViz').innerHTML = `<img src="${item.latent_url}" alt="Latent space visualization">`;
    } else {
        document.getElementById('latentViz').innerHTML = '<div class="viz-placeholder">No visualization</div>';
    }
    
    if (item.ai_url) {
        document.getElementById('aiViz').innerHTML = `<img src="${item.ai_url}" alt="Text-to-image AI">`;
    } else {
        document.getElementById('aiViz').innerHTML = '<div class="viz-placeholder">No AI visualization</div>';
    }
    
    if (item.gan_url) {
        document.getElementById('ganViz').innerHTML = `<img src="${item.gan_url}" alt="GAN from latent vector">`;
    } else {
        document.getElementById('ganViz').innerHTML = '<div class="viz-placeholder">No GAN visualization</div>';
    }
    
    // Update path history IMMEDIATELY
    updatePathHistory();
    
    // Update graph in background
    updateGraph(item.artwork);
}

function resetExploration() {
    if (confirm('Start a new exploration? This will reset your current path.')) {
        // Reset everything
        path = [];
        visitedEdges.clear();
        currentNeighbors = [];
        
        if (networkData) {
            networkData.nodes.clear();
            networkData.edges.clear();
        }
        
        // Show start screen
        document.getElementById('mainExplorer').style.display = 'none';
        document.getElementById('startScreen').style.display = 'flex';
    }
}

async function showStatistics() {
    showLoading('Computing statistics...');
    
    try {
        const pathIndices = path.map(p => p.idx);
        
        const response = await fetch('/api/stats', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: pathIndices})
        });
        
        const stats = await response.json();
        
        displayStatistics(stats);
        
        document.getElementById('statsOverlay').style.display = 'flex';
        
        hideLoading();
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        alert('Error computing statistics. Please try again.');
    }
}

function displayStatistics(stats) {
    // Nationalities
    const natDiv = document.getElementById('nationalityStats');
    const topNats = Object.entries(stats.nationalities).slice(0, 5);
    natDiv.innerHTML = topNats.map(([nat, data]) => `
        <div class="stat-item">
            <div class="stat-label">${nat}</div>
            <div class="stat-bar">
                <div class="stat-fill" style="width: ${data.percent}%"></div>
            </div>
            <div class="stat-value">${data.percent.toFixed(1)}%</div>
        </div>
    `).join('');
    
    // Gender
    const genderDiv = document.getElementById('genderStats');
    genderDiv.innerHTML = Object.entries(stats.genders).map(([gender, data]) => `
        <div class="stat-item">
            <div class="stat-label">${gender}</div>
            <div class="stat-bar">
                <div class="stat-fill" style="width: ${data.percent}%"></div>
            </div>
            <div class="stat-value">${data.percent.toFixed(1)}%</div>
        </div>
    `).join('');
    
    // Departments
    const deptDiv = document.getElementById('departmentStats');
    const topDepts = Object.entries(stats.departments).slice(0, 5);
    deptDiv.innerHTML = topDepts.map(([dept, data]) => `
        <div class="stat-item">
            <div class="stat-label">${dept}</div>
            <div class="stat-bar">
                <div class="stat-fill" style="width: ${data.percent}%"></div>
            </div>
            <div class="stat-value">${data.percent.toFixed(1)}%</div>
        </div>
    `).join('');
    
    // Acquisition decades
    const acqDiv = document.getElementById('acquisitionStats');
    acqDiv.innerHTML = Object.entries(stats.acquisition_decades).map(([decade, data]) => `
        <div class="stat-item">
            <div class="stat-label">${decade}s</div>
            <div class="stat-bar">
                <div class="stat-fill" style="width: ${data.percent}%"></div>
            </div>
            <div class="stat-value">${data.percent.toFixed(1)}%</div>
        </div>
    `).join('');
}

function showLoading(text) {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.innerHTML = text;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

