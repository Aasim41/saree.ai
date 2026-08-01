import { useState, useEffect, useCallback } from 'react'
import './index.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [view, setView] = useState('library');
  const [assets, setAssets] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [exportingId, setExportingId] = useState(null);

  const [uploadData, setUploadData] = useState({
    name: '', fabric_type: 'Silk Crepe', print_width_cm: 115, repeat_size_cm: 50
  });
  const [uploadFile, setUploadFile] = useState(null);

  const authHeader = 'Basic ' + btoa(`${credentials.username}:${credentials.password}`);

  const fetchAssets = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/assets`, {
        headers: { 'Authorization': authHeader }
      });
      if (response.ok) {
        const data = await response.json();
        setAssets(data.assets || []);
        setError('');
      } else if (response.status === 401) {
        setIsAuthenticated(false);
        setError('Invalid credentials.');
      } else {
        setError('Failed to load assets.');
      }
    } catch (err) {
      console.error(err);
      setError('Cannot reach backend. Is the API running?');
    }
  }, [authHeader]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch(`${API_URL}/assets`, {
        headers: { 'Authorization': authHeader }
      });
      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        setError('Invalid Operator ID or Passkey.');
      }
    } catch {
      setError('Cannot reach backend. Is the API running on port 8000?');
    }
  };

  useEffect(() => {
    if (view === 'library' && isAuthenticated) fetchAssets();
  }, [view, isAuthenticated, fetchAssets]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return alert("Please select a design file first.");

    setIsUploading(true);
    setError('');
    const data = new FormData();
    data.append('fabric_type', uploadData.fabric_type);
    data.append('name', uploadData.name);
    data.append('print_width_cm', uploadData.print_width_cm);
    data.append('repeat_size_cm', uploadData.repeat_size_cm);
    data.append('file', uploadFile);

    try {
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        headers: { 'Authorization': authHeader },
        body: data
      });
      if (res.ok) {
        setView('library');
        setUploadFile(null);
        fetchAssets();
      } else {
        const detail = await res.json().catch(() => ({}));
        setError(detail.detail || 'Upload failed.');
      }
    } catch (err) {
      console.error(err);
      setError('Upload failed — network error.');
    } finally {
      setIsUploading(false);
    }
  };

  const generateVariant = async (parentId) => {
    setError('');
    const data = new FormData();
    data.append('prompt', '');
    data.append('lora', '');

    try {
      const res = await fetch(`${API_URL}/generate-variant/${parentId}`, {
        method: 'POST',
        headers: { 'Authorization': authHeader },
        body: data
      });
      if (res.ok) {
        fetchAssets();
      } else {
        const detail = await res.json().catch(() => ({}));
        setError(detail.detail || 'Variant generation failed.');
      }
    } catch (err) {
      console.error(err);
      setError('Variant generation failed — network error.');
    }
  };

  const exportVariant = async (variantId) => {
    setError('');
    setExportingId(variantId);
    try {
      const res = await fetch(`${API_URL}/export/${variantId}`, {
        headers: { 'Authorization': authHeader }
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        setError(detail.detail || 'Export failed.');
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `texflow_production_pkg_var${variantId}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      setError('Export failed — network error.');
    } finally {
      setExportingId(null);
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
          {error && <p style={{color: 'var(--accent-color)', marginBottom: '1rem'}}>{error}</p>}
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

      {error && (
        <div style={{background: 'rgba(226,109,92,0.15)', border: '1px solid var(--accent-color)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem'}}>
          {error}
        </div>
      )}

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
                <input type="file" accept="image/*" className="glass-input" onChange={e => setUploadFile(e.target.files[0])} />
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
              <div key={`${asset.type}-${asset.id}`} className="asset-card glass">
                <div className="asset-img-container">
                  {asset.type === 'variant' && <div className="asset-badge">Variant</div>}
                  <img src={asset.image_url} alt={asset.name || asset.filename} />
                </div>

                <div className="asset-info">
                  <h4>{asset.name || asset.filename}</h4>
                  <p>
                    <strong>Substrate:</strong> {asset.fabric_type || '—'} <br/>
                    {asset.print_width_cm && (
                      <> <strong>Width:</strong> {asset.print_width_cm}cm | <strong>Repeat:</strong> {asset.repeat_size_cm}cm <br/></>
                    )}
                    {asset.dominant_colors && (
                      <> <strong>Extracted Palette:</strong> {asset.dominant_colors || asset.palette} <br/></>
                    )}
                    {asset.caption && asset.type === 'design' && (
                      <> <strong>Caption:</strong> {asset.caption.slice(0, 80)}{asset.caption.length > 80 ? '…' : ''}</>
                    )}
                  </p>
                </div>

                <div className="asset-actions">
                  {asset.type === 'design' && (
                    <button onClick={() => generateVariant(asset.id)} className="btn-secondary" style={{flex: 1, padding: '0.5rem', fontSize: '0.85rem'}}>
                      + Spin Variant
                    </button>
                  )}
                  {asset.type === 'variant' && (
                    <button
                      onClick={() => exportVariant(asset.id)}
                      disabled={exportingId === asset.id}
                      className="btn-primary"
                      style={{flex: 1, padding: '0.5rem', fontSize: '0.85rem'}}
                    >
                      {exportingId === asset.id ? 'Exporting…' : 'Export ZIP'}
                    </button>
                  )}
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
