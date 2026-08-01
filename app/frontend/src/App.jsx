import { useState } from 'react'
import './index.css'

function App() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [formData, setFormData] = useState({
    prompt: '',
    motif: 'peacock',
    palette: 'green, red',
    border: 'zari_temple',
    pallu: 'heavy_brocade'
  });
  const [previewImage, setPreviewImage] = useState('/hero_preview.jpg');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    try {
      const data = new FormData();
      Object.keys(formData).forEach(key => data.append(key, formData[key]));
      
      const response = await fetch('http://127.0.0.1:8000/generate', {
        method: 'POST',
        body: data
      });
      
      if (!response.ok) throw new Error('Network response was not ok');
      
      const result = await response.json();
      if (result.status === 'success' && result.image) {
        setPreviewImage(result.image);
      } else {
        alert("Failed to generate mockup.");
      }
    } catch (err) {
      console.error(err);
      alert("Error calling backend. Is the FastAPI server running?");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Saree Design AI</h1>
        <p>Craft premium textile designs with generative intelligence.</p>
      </header>

      <main className="workspace">
        <aside className="controls-panel glass">
          <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            <div className="form-group">
              <label>Creative Prompt</label>
              <textarea 
                className="glass-input" 
                name="prompt"
                value={formData.prompt}
                onChange={handleInputChange}
                placeholder="Describe the overall vibe (e.g. vintage royal, modern minimalist)"
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>Primary Motif</label>
              <select className="glass-input" name="motif" value={formData.motif} onChange={handleInputChange}>
                <option value="peacock">Peacock (Annapakshi)</option>
                <option value="mango">Mango (Paisley/Manga)</option>
                <option value="geometric">Geometric Checkers</option>
                <option value="floral">Floral Vine</option>
              </select>
            </div>

            <div className="form-group">
              <label>Color Palette</label>
              <input 
                type="text" 
                className="glass-input" 
                name="palette"
                value={formData.palette}
                onChange={handleInputChange}
                placeholder="e.g. green, red (Basic CSS colors for MVP)" 
              />
            </div>

            <div className="form-group">
              <label>Border Style</label>
              <select className="glass-input" name="border" value={formData.border} onChange={handleInputChange}>
                <option value="zari_temple">Zari Temple Border</option>
                <option value="contrast">Solid Contrast Band</option>
                <option value="skirt">Skirt Border (Tall)</option>
                <option value="borderless">Borderless (Body motif only)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Pallu Complexity</label>
              <select className="glass-input" name="pallu" value={formData.pallu} onChange={handleInputChange}>
                <option value="heavy_brocade">Heavy Brocade (Rich Zari)</option>
                <option value="stripes">Simple Zari Stripes</option>
                <option value="matching">Matches Body</option>
              </select>
            </div>

            <button type="submit" className="btn-primary" disabled={isGenerating}>
              {isGenerating ? 'Weaving Design...' : 'Generate Mockup'}
            </button>
          </form>
        </aside>

        <section className="preview-panel glass">
          <div className="image-container" style={{background: 'none', border: 'none'}}>
            {isGenerating ? (
              <div className="loader"></div>
            ) : (
              <>
                <img src={previewImage} alt="Saree Design Preview" style={{objectFit: 'contain', width: '100%', maxHeight: '500px'}} />
                {previewImage !== '/hero_preview.jpg' && (
                  <div className="image-overlay" style={{opacity: 1, position: 'relative', background: 'transparent', textAlign: 'center', marginTop: '10px'}}>
                    <h3 style={{ margin: '0 0 5px 0' }}>MVP Composite Layout</h3>
                    <p style={{ margin: 0, color: 'var(--text-muted)' }}>Dynamically generated by FastAPI Backend</p>
                  </div>
                )}
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
