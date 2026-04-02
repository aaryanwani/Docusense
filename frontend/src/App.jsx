import React, { useState, useRef } from 'react';
import axios from 'axios';
import { 
  UploadCloud, FileText, Activity, Shield, Users, 
  Clock, BrainCircuit, CheckCircle, AlertTriangle, 
  FileSearch, BarChart2, Hash, ArrowRight
} from 'lucide-react';

export default function App() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (selectedFile) => {
    const normalizedName = selectedFile.name.toLowerCase();

    if (
      !normalizedName.endsWith('.txt') &&
      !normalizedName.endsWith('.pdf') &&
      !normalizedName.endsWith('.doc') &&
      !normalizedName.endsWith('.docx')
    ) {
      setError("Please upload a .txt, .pdf, .doc, or .docx file.");
      return;
    }
    setError(null);
    setFile(selectedFile);
    processDocument(selectedFile);
  };

  const processDocument = async (fileToProcess) => {
    setAnalyzing(true);
    setResult(null);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", fileToProcess);

    try {
      const response = await axios.post("http://localhost:8000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze document. Ensure backend and Ollama are running.");
    } finally {
      setAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  // Helper to format entity types
  const getEntityIcon = (label) => {
    switch(label) {
      case 'ORG': return <Users size={14} />;
      case 'PERSON': return <Users size={14} />;
      case 'MONEY': return <Activity size={14} />;
      case 'DATE': return <Clock size={14} />;
      case 'LOC': return <FileText size={14} />;
      default: return <Hash size={14} />;
    }
  };

  const formatObligation = (obligation) => {
    if (!obligation) return obligation;

    return obligation
      .replace(/^\s*\d+[.)]\s*/, '')
      .replace(/^\s*[-*•▪●◦‣–—]+\s*/, '')
      .replace(/[_*`]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  };

  return (
    <div className="app-container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      
      {/* HEADER */}
      <header className="animate-fade-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '3rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Logo container using CSS mask to perfectly colorize the transparent PNG logo to Orange and Cream */}
          <div style={{ 
            WebkitMaskImage: 'url("/ds-logo.png")',
            maskImage: 'url("/ds-logo.png")',
            background: 'linear-gradient(135deg, var(--orange-primary), #FEF3C7)',
            WebkitMaskSize: 'contain',
            maskSize: 'contain',
            WebkitMaskRepeat: 'no-repeat',
            maskRepeat: 'no-repeat',
            WebkitMaskPosition: 'center',
            maskPosition: 'center',
            width: '48px',
            height: '48px',
          }} title="DocuSense Logo"></div>
          <h1 style={{ fontSize: '1.75rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.5px' }}>
            DocuSense
          </h1>
        </div>
        
        {/* Analyze Another Document Button moved to header for better visibility */}
        {result && (
          <button className="btn-primary" onClick={resetAnalysis} style={{ background: 'linear-gradient(135deg, var(--orange-primary), #FDBA74)', color: '#9A3412', boxShadow: 'var(--shadow-sm)', border: 'none' }}>
            Analyze Another Document
          </button>
        )}
      </header>

      {/* ERROR MESSAGE */}
      {error && (
        <div className="glass-panel animate-fade-in" style={{ padding: '1rem', marginBottom: '2rem', borderLeft: '4px solid #EF4444', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <AlertTriangle color="#EF4444" />
          <p style={{ margin: 0, color: '#FECACA' }}>{error}</p>
        </div>
      )}

      {/* MAIN CONTENT AREA */}
      <main>
        
        {/* STATE 1: UPLOAD */}
        {!analyzing && !result && (
          <div className="glass-panel animate-fade-in" style={{ padding: '4rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            
            <div 
              className={`upload-zone ${dragActive ? 'active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              style={{ width: '100%', maxWidth: '600px' }}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleChange} 
                accept=".txt,.pdf,.doc,.docx" 
                style={{ display: 'none' }} 
              />
              <div className="animate-float" style={{ marginBottom: '1.5rem', opacity: 0.8 }}>
                <UploadCloud size={64} color="var(--accent-primary)" />
              </div>
              <h3 style={{ marginBottom: '0.5rem', fontSize: '1.5rem' }}>Drop your document here</h3>
              <p style={{ color: 'var(--text-tertiary)' }}>Supports .txt, .pdf, .doc, and .docx files</p>
              
              <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <button className="btn-primary" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click() }}>
                  Browse Files
                </button>
              </div>
            </div>

            <div style={{ marginTop: '3rem', display: 'flex', gap: '2rem', color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Shield size={16} color="var(--accent-secondary)" /> Pre-trained Encoders
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <BrainCircuit size={16} color="var(--accent-primary)" /> Local LLM (Qwen)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileSearch size={16} color="var(--status-legal)" /> Semantic Search
              </div>
            </div>

          </div>
        )}

        {/* STATE 2: ANALYZING */}
        {analyzing && (
          <div className="glass-panel animate-fade-in" style={{ padding: '4rem 2rem', textAlign: 'center', minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ position: 'relative', width: '80px', height: '80px', marginBottom: '2rem' }}>
              <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '4px solid var(--border-subtle)' }}></div>
              <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '4px solid var(--accent-primary)', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }}></div>
              <BrainCircuit size={32} color="var(--accent-primary)" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
            </div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>AI is analyzing your document...</h3>
            <p style={{ color: 'var(--text-tertiary)', maxWidth: '400px', margin: '0 auto' }}>
              Extracting entities, identifying obligations, and generating a comprehensive summary using local LLMs.
            </p>
            <style>
              {`@keyframes spin { 100% { transform: rotate(360deg); } }`}
            </style>
          </div>
        )}

        {/* STATE 3: RESULTS DASHBOARD */}
        {result && !analyzing && (
          <div className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '2rem', alignItems: 'start' }}>
            
            {/* Left Sidebar - Meta & Stats */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                  <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <FileText size={18} color="var(--accent-primary)" />
                    Document
                  </h3>
                  <div className={`chip ${(result.document_type || 'GENERAL').split('_')[0].toLowerCase()}`}>
                    {result.document_type || 'GENERAL DOCUMENT'}
                  </div>
                </div>
                <p style={{ wordBreak: 'break-all', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>{result.filename}</p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>Processed locally • 100% private</p>
                
                <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', margin: '1.5rem 0' }} />
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', marginBottom: '0.25rem' }}>WORDS</p>
                    <p style={{ fontSize: '1.2rem', fontWeight: 600 }}>{result.word_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', marginBottom: '0.25rem' }}>SENTENCES</p>
                    <p style={{ fontSize: '1.2rem', fontWeight: 600 }}>{result.sentence_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', marginBottom: '0.25rem' }}>CHARACTERS</p>
                    <p style={{ fontSize: '1.2rem', fontWeight: 600 }}>{result.char_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', marginBottom: '0.25rem' }}>PARAGRAPHS</p>
                    <p style={{ fontSize: '1.2rem', fontWeight: 600 }}>{result.paragraph_count.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              {/* Entities Panel */}
              {result.entities && result.entities.length > 0 && (
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                  <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                    <Users size={18} color="var(--accent-secondary)" />
                    Key Entities
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {result.entities.slice(0, 15).map((ent, idx) => (
                      <span key={idx} className="chip" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)', display: 'flex', gap: '0.35rem' }}>
                        {getEntityIcon(ent.label)}
                        {ent.text}
                      </span>
                    ))}
                    {result.entities.length > 15 && (
                      <span className="chip" style={{ background: 'transparent' }}>+{result.entities.length - 15} more</span>
                    )}
                  </div>
                </div>
              )}



            </div>

            {/* Right Main Area - Summary & Obligations */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              {/* Summary Hero Panel */}
              <div className="glass-panel-orange" style={{ padding: '2rem', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: '-50px', right: '-50px', width: '150px', height: '150px', background: 'var(--orange-glow)', filter: 'blur(50px)', borderRadius: '50%' }}></div>
                
                <h2 style={{ margin: '0 0 1.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.5rem', color: '#C2410C' }}>
                  <BrainCircuit size={24} color="#EA580C" />
                  AI Summary
                </h2>
                
                {result.summary ? (
                  <div className="markdown-content" style={{ fontSize: '1.05rem', lineHeight: 1.7, color: 'var(--text-primary)' }}>
                    {/* Render basic text with line breaks if it's not full MD, or just pre-wrap */}
                    <div style={{ whiteSpace: 'pre-wrap' }}>
                      {result.summary}
                    </div>
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-tertiary)', fontStyle: 'italic' }}>No summary generated by LLM.</p>
                )}
              </div>

              {/* Obligations Panel */}
              {result.obligations && result.obligations.length > 0 && (
                <div className="glass-panel-light-orange" style={{ padding: '2rem' }}>
                  <h2 style={{ margin: '0 0 1.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.3rem', color: '#9A3412' }}>
                    <Shield size={22} color="#F97316" />
                    Detected Obligations
                    <span style={{ fontSize: '0.8rem', background: 'rgba(249, 115, 22, 0.2)', color: '#C2410C', padding: '2px 8px', borderRadius: '12px', marginLeft: 'auto' }}>
                      {result.obligations.length} found
                    </span>
                  </h2>
                  
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {result.obligations.map((obs, idx) => (
                      <li key={idx} style={{ 
                        background: 'rgba(255,255,255,0.6)', 
                        border: '1px solid var(--border-subtle)', 
                        padding: '1rem 1.25rem', 
                        borderRadius: '8px',
                        display: 'flex',
                        gap: '1rem',
                        alignItems: 'flex-start'
                      }}>
                        <CheckCircle size={18} color="#F97316" style={{ flexShrink: 0, marginTop: '2px' }} />
                        <span style={{ color: 'var(--text-primary)', lineHeight: 1.5 }}>{formatObligation(obs)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          </div>
        )}

      </main>
    </div>
  );
}
