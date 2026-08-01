import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [view, setView] = useState('library'); // library, upload
  const [assets, setAssets] = useState([]);
  
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
    if (!uploadFile) return alert("Select an image");
    
    const data = new FormData();
    Object.keys(uploadData).forEach(k => data.append(k, uploadData[k]));
    data.append('file', uploadFile);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        headers: { 'Authorization': authHeader },
        body: data
      });
      if (res.ok) setView('library');
    } catch (err) {
      console.error(err);
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
        <div className="glass" style={{padding: '40px', width: '400px', textAlign: 'center'}}>
          <h2>TexFlow Secure Login</h2>
          <form onSubmit={handleLogin} style={{display:'flex', flexDirection:'column', gap:'15px', marginTop:'20px'}}>
            <input type="text" className="glass-input" placeholder="Username" value={credentials.username} onChange={e => setCredentials({...credentials, username: e.target.value})} required />
            <input type="password" className="glass-input" placeholder="Password" value={credentials.password} onChange={e => setCredentials({...credentials, password: e.target.value})} required />
            <button type="submit" className="btn-primary">Enter Workspace</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h1>TexFlow</h1>
          <p>AI Design & Production Workspace</p>
        </div>
        <div style={{display: 'flex', gap: '10px'}}>
          <button className="btn-primary" onClick={() => setView('library')} style={{padding: '8px 16px', fontSize: '0.9rem'}}>Asset Library</button>
          <button className="btn-primary" onClick={() => setView('upload')} style={{padding: '8px 16px', fontSize: '0.9rem', background: '#334155'}}>Upload Design</button>
        </div>
      </header>

      {view === 'upload' ? (
        <main className="workspace">
          <div className="glass" style={{padding: '30px', maxWidth: '600px', margin: '0 auto', width: '100%'}}>
            <h2>Ingest New Design</h2>
            <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <input type="file" className="glass-input" onChange={e => setUploadFile(e.target.files[0])} />
              <input type="text" className="glass-input" placeholder="Design Name" value={uploadData.name} onChange={e => setUploadData({...uploadData, name: e.target.value})} />
              <input type="text" className="glass-input" placeholder="Fabric Type" value={uploadData.fabric_type} onChange={e => setUploadData({...uploadData, fabric_type: e.target.value})} />
              <div style={{display: 'flex', gap: '10px'}}>
                <input type="number" className="glass-input" placeholder="Print Width (cm)" value={uploadData.print_width_cm} onChange={e => setUploadData({...uploadData, print_width_cm: e.target.value})} />
                <input type="number" className="glass-input" placeholder="Repeat Size (cm)" value={uploadData.repeat_size_cm} onChange={e => setUploadData({...uploadData, repeat_size_cm: e.target.value})} />
              </div>
              <button type="submit" className="btn-primary">Upload & Analyze</button>
            </form>
          </div>
        </main>
      ) : (
        <main className="workspace" style={{flexDirection: 'column'}}>
          <h2 style={{marginTop: 0}}>Production Asset Library</h2>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px'}}>
            {assets.map((asset) => (
              <div key={asset.id} className="glass" style={{padding: '15px'}}>
                <img src={asset.image_url} style={{width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px'}} />
                <h4 style={{margin: '10px 0 5px 0'}}>{asset.name} {asset.parent_id && <span style={{fontSize:'0.7rem', color:'var(--primary)'}}>(Variant of #{asset.parent_id})</span>}</h4>
                <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 10px 0'}}>
                  Fabric: {asset.fabric_type} | Width: {asset.print_width_cm}cm<br/>
                  Extracted Palette: {asset.palette}
                </p>
                <div style={{display: 'flex', gap: '5px'}}>
                  <button onClick={() => generateVariant(asset.id)} className="btn-primary" style={{flex: 1, padding: '5px', fontSize: '0.8rem'}}>+ Variant</button>
                  <a href={`http://127.0.0.1:8000/export/${asset.id}`} className="btn-primary" style={{flex: 1, textAlign: 'center', padding: '5px', fontSize: '0.8rem', textDecoration: 'none', background: '#10b981'}}>ZIP</a>
                </div>
              </div>
            ))}
            {assets.length === 0 && <p>No assets ingested yet.</p>}
          </div>
        </main>
      )}
    </div>
  )
}

export default App
