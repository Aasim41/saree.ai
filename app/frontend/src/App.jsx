import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [view, setView] = useState('library'); 
  const [assets, setAssets] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  
  const [uploadData, setUploadData] = useState({
    name: '', collection: 'Spring 2027', fabric_type: 'Silk Crepe', print_width_cm: 115, repeat_size_cm: 50
  });
  const [uploadFile, setUploadFile] = useState(null);

  const authHeader = 'Basic ' + btoa(`${credentials.username}:${credentials.password}`);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsAuthenticated(true); 
  };

  const fetchAssets = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/assets', {
        headers: { 'Authorization': authHeader }
      });
      if (response.ok) {
        const data = await response.json();
        setAssets(data.assets || []);
      } else if (response.status === 401) {
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (view === 'library' && isAuthenticated) fetchAssets();
  }, [view, isAuthenticated]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return alert("Please select a design file first.");
    
    setIsUploading(true);
    const data = new FormData();
    Object.keys(uploadData).forEach(k => data.append(k, uploadData[k]));
    data.append('file', uploadFile);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        headers: { 'Authorization': authHeader },
        body: data
      });
      if (res.ok) {
        setView('library');
        setUploadFile(null);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const generateVariant = async (parentId) => {
    const data = new FormData();
    data.append('new_palette', 'Blue, Silver');
    data.append('new_repeat_cm', 30);
    
    try {
      await fetch(`http://127.0.0.1:8000/generate-variant/${parentId}`, {
        method: 'POST',
        headers: { 'Authorization': authHeader },
        body: data
      });
      fetchAssets();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="app-container" style={{display:'flex', justifyContent:'center', alignItems:'center', minHeight:'100vh'}}>
        <div className="glass animate-fade-in" style={{padding: '4rem', width: '100%', maxWidth: '450px'}}>
          <div style={{marginBottom: '3rem'}}>
            <h1 style={{fontSize: '2.5rem', marginBottom: '0.5rem'}}>TexFlow</h1>
            <p style={{fontFamily: 'Space Mono', fontSize: '0.8rem', letterSpacing: '0.05em'}}>SYSTEM AUTHENTICATION REQUIRED</p>
          </div>
          <form onSubmit={handleLogin} style={{display:'flex', flexDirection:'column', gap:'1.5rem'}}>
            <div className="form-group">
              <label>Operator ID</label>
              <input type="text" className="glass-input" placeholder="ID" value={credentials.username} onChange={e => setCredentials({...credentials, username: e.target.value})} required />
            </div>
            <div className="form-group">
              <label>Passkey</label>
              <input type="password" className="glass-input" placeholder="***" value={credentials.password} onChange={e => setCredentials({...credentials, password: e.target.value})} required />
            </div>
            <button type="submit" className="btn-primary" style={{marginTop: '1rem'}}>Execute Login</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
        <div>
          <h1>TexFlow</h1>
          <p>Production Workspace System</p>
        </div>
        <div className="nav-tabs">
          <button className={`nav-tab ${view === 'library' ? 'active' : ''}`} onClick={() => setView('library')}>Library</button>
          <button className={`nav-tab ${view === 'upload' ? 'active' : ''}`} onClick={() => setView('upload')}>Ingest</button>
        </div>
      </header>

      {view === 'upload' ? (
        <main className="animate-fade-in">
          <div className="glass" style={{padding: '3rem', maxWidth: '650px', margin: '0 auto', width: '100%'}}>
            <div style={{marginBottom: '2rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem'}}>
              <h2 style={{margin: 0}}>Ingest New Asset</h2>
              <p style={{color: 'var(--text-muted)', margin: '0.5rem 0 0 0'}}>Upload a raw design file and define physical machine requirements.</p>
            </div>
            
            <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="form-group">
                <label>Master Design File (Image)</label>
                <input type="file" className="glass-input" onChange={e => setUploadFile(e.target.files[0])} />
              </div>
              
              <div className="form-group">
                <label>Asset Nomenclature</label>
                <input type="text" className="glass-input" placeholder="e.g. Royal Peacock Border v2" value={uploadData.name} onChange={e => setUploadData({...uploadData, name: e.target.value})} />
              </div>
              
              <div className="form-group">
                <label>Target Fabric Substrate</label>
                <input type="text" className="glass-input" placeholder="e.g. Silk Crepe" value={uploadData.fabric_type} onChange={e => setUploadData({...uploadData, fabric_type: e.target.value})} />
              </div>
              
              <div style={{display: 'flex', gap: '1.5rem', width: '100%'}}>
                <div className="form-group" style={{flex: 1}}>
                  <label>Machine Print Width (cm)</label>
                  <input type="number" className="glass-input" placeholder="115" value={uploadData.print_width_cm} onChange={e => setUploadData({...uploadData, print_width_cm: e.target.value})} />
                </div>
                <div className="form-group" style={{flex: 1}}>
                  <label>Pattern Repeat Scale (cm)</label>
                  <input type="number" className="glass-input" placeholder="50" value={uploadData.repeat_size_cm} onChange={e => setUploadData({...uploadData, repeat_size_cm: e.target.value})} />
                </div>
              </div>
              
              <div style={{marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end'}}>
                <button type="submit" className="btn-primary" disabled={isUploading}>
                  {isUploading ? 'Extracting & Ingesting...' : 'Upload & Analyze Asset'}
                </button>
              </div>
            </form>
          </div>
        </main>
      ) : (
        <main>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
            <h2 style={{margin: 0}}>Production Assets</h2>
            <span style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>{assets.length} items tracked</span>
          </div>
          
          <div className="asset-grid">
            {assets.map((asset) => (
              <div key={asset.id} className="asset-card glass">
                <div className="asset-img-container">
                  {asset.parent_id && <div className="asset-badge">Variant</div>}
                  <img src={asset.image_url} alt={asset.name} />
                </div>
                
                <div className="asset-info">
                  <h4>{asset.name}</h4>
                  <p>
                    <strong>Substrate:</strong> {asset.fabric_type} <br/>
                    <strong>Width:</strong> {asset.print_width_cm}cm | <strong>Repeat:</strong> {asset.repeat_size_cm}cm <br/>
                    <strong>Extracted Palette:</strong> {asset.palette}
                  </p>
                </div>
                
                <div className="asset-actions">
                  <button onClick={() => generateVariant(asset.id)} className="btn-secondary" style={{flex: 1, padding: '0.5rem', fontSize: '0.85rem'}}>
                    + Spin Variant
                  </button>
                  <a href={`http://127.0.0.1:8000/export/${asset.id}`} className="btn-primary" style={{flex: 1, textAlign: 'center', padding: '0.5rem', fontSize: '0.85rem', textDecoration: 'none'}}>
                    Export ZIP
                  </a>
                </div>
              </div>
            ))}
            
            {assets.length === 0 && (
              <div style={{gridColumn: '1 / -1', textAlign: 'center', padding: '4rem', color: 'var(--text-muted)'}}>
                <div style={{fontSize: '3rem', marginBottom: '1rem'}}>📁</div>
                <h3>No assets found</h3>
                <p>Ingest a new design asset to begin populating your library.</p>
                <button onClick={() => setView('upload')} className="btn-secondary" style={{marginTop: '1rem'}}>Go to Ingest</button>
              </div>
            )}
          </div>
        </main>
      )}
    </div>
  )
}

export default App
