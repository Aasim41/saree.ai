import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [view, setView] = useState('design'); // 'design' or 'history'
  const [history, setHistory] = useState([]);
  const [formData, setFormData] = useState({
    prompt: '',
    motif: 'peacock',
    palette: 'green, red',
    border: 'zari_temple',
    pallu: 'heavy_brocade'
  });
  const [previewImage, setPreviewImage] = useState('/hero_preview.jpg');

  // Basic auth credentials matching backend
  const authHeader = 'Basic ' + btoa('designer:saree123');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/history', {
        headers: { 'Authorization': authHeader }
      });
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (view === 'history') fetchHistory();
  }, [view]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    
    try {
      const data = new FormData();
      Object.keys(formData).forEach(key => data.append(key, formData[key]));
      // Note: In real app, append file sketch here
      
      const response = await fetch('http://127.0.0.1:8000/generate', {
        method: 'POST',
        headers: { 'Authorization': authHeader },
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
      <header style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h1>Saree Design AI</h1>
          <p>Craft premium textile designs with generative intelligence.</p>
        </div>
        <div style={{display: 'flex', gap: '10px'}}>
          <button className="btn-primary" onClick={() => setView('design')} style={{padding: '8px 16px', fontSize: '0.9rem'}}>Designer</button>
          <button className="btn-primary" onClick={() => setView('history')} style={{padding: '8px 16px', fontSize: '0.9rem', background: '#334155'}}>History</button>
        </div>
      </header>

      {view === 'design' ? (
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
                  placeholder="e.g. green, red" 
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
            <div className="image-container" style={{background: 'none', border: 'none', position: 'relative'}}>
              {isGenerating ? (
                <div className="loader"></div>
              ) : (
                <>
                  <img src={previewImage} alt="Saree Design Preview" style={{objectFit: 'contain', width: '100%', maxHeight: '500px'}} />
                  {previewImage !== '/hero_preview.jpg' && (
                    <div style={{position: 'absolute', top: '10px', right: '10px'}}>
                      <button className="btn-primary" style={{padding: '8px 16px', background: '#10b981'}}>Download Print Package</button>
                    </div>
                  )}
                </>
              )}
            </div>
          </section>
        </main>
      ) : (
        <main className="workspace" style={{flexDirection: 'column'}}>
          <h2 style={{marginTop: 0}}>Design History</h2>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px'}}>
            {history.map((item, i) => (
              <div key={i} className="glass" style={{padding: '10px'}}>
                <img src={`data:image/jpeg;base64,${item.image_b64}`} style={{width: '100%', borderRadius: '8px'}} />
                <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '10px'}}>{item.prompt.substring(0, 30)}...</p>
              </div>
            ))}
            {history.length === 0 && <p>No designs yet.</p>}
          </div>
        </main>
      )}
    </div>
  )
}

export default App
