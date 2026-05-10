import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './CatSound.module.css'

const TIER_COLORS = { 1: '#dc2626', 2: '#f97316', 3: '#16a34a', 4: '#6b7280' }

export default function CatSound() {
  const navigate   = useNavigate()
  const inputRef   = useRef(null)
  const fileRef    = useRef(null)

  const [fileName, setFileName]   = useState(null)
  const [result,   setResult]     = useState(null)
  const [loading,  setLoading]    = useState(false)
  const [dragOver, setDragOver]   = useState(false)
  const [playing,  setPlaying]    = useState(false)
  const audioRef = useRef(null)

  function handleFile(file) {
    if (!file) return
    if (!file.type.startsWith('audio/')) return
    setResult(null)
    fileRef.current = file
    setFileName(file.name)
    if (audioRef.current) {
      audioRef.current.src = URL.createObjectURL(file)
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  function clearFile() {
    setFileName(null)
    setResult(null)
    fileRef.current = null
    if (inputRef.current) inputRef.current.value = ''
    if (audioRef.current) { audioRef.current.src = ''; setPlaying(false) }
  }

  function togglePlay() {
    if (!audioRef.current) return
    if (playing) { audioRef.current.pause(); setPlaying(false) }
    else         { audioRef.current.play();  setPlaying(true)  }
  }

  async function handleAnalyze() {
    if (!fileRef.current) return
    setLoading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', fileRef.current)
      const res  = await fetch('http://127.0.0.1:8000/predict-cat-sound', { method: 'POST', body: formData })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult(data)
    } catch (err) {
      setResult({ error: err?.message === 'Failed to fetch'
        ? 'Cannot reach backend API. Start backend on port 8000 and retry.'
        : err.message })
    } finally {
      setLoading(false)
    }
  }

  const tierColor = result ? (TIER_COLORS[result.tier] ?? '#6b7280') : '#6b7280'

  return (
    <div className={styles.page}>

      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      <div className={styles.header}>
        <div className={styles.headerIcon}>🐱</div>
        <div>
          <h1 className={styles.title}>Cat Sound Classification</h1>
          <p className={styles.subtitle}>
            Upload an audio recording of your cat. Our YAMNet-based model classifies the
            vocalization into 10 behavioral categories and flags clinical urgency.
          </p>
        </div>
      </div>

      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Cat Audio</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${fileName ? styles.hasFile : ''}`}
            onClick={() => !fileName && inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {fileName ? (
              <div className={styles.audioPreview}>
                <span className={styles.audioIcon}>🔊</span>
                <p className={styles.audioName}>{fileName}</p>
                <audio ref={audioRef} onEnded={() => setPlaying(false)} />
                <button className={styles.playBtn} onClick={e => { e.stopPropagation(); togglePlay() }}>
                  {playing ? '⏸ Pause' : '▶ Play'}
                </button>
              </div>
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🎙️</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>WAV, MP3, OGG — 1–5 s of cat vocalization recommended</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="audio/*"
            className={styles.fileInput}
            onChange={e => handleFile(e.target.files[0])}
          />

          <div className={styles.actions}>
            {fileName && (
              <button className={styles.btnSecondary} onClick={clearFile}>Clear</button>
            )}
            <button
              className={styles.btnPrimary}
              onClick={handleAnalyze}
              disabled={!fileName || loading}
            >
              {loading
                ? <><span className={styles.spinnerInline} /> Classifying…</>
                : '🔍 Classify Sound'}
            </button>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🐱</span>
              <p className={styles.emptyText}>Your analysis will appear here</p>
              <p className={styles.emptyHint}>Upload an audio file and click Classify</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Extracting YAMNet embeddings…</p>
              <p className={styles.emptyHint}>This may take a few seconds</p>
            </div>
          )}

          {result?.error && (
            <div className={styles.errorBox}>
              <span>⚠️</span>
              <div>
                <p className={styles.errorTitle}>Something went wrong</p>
                <p className={styles.errorMsg}>{result.error}</p>
              </div>
            </div>
          )}

          {result && !result.error && (
            <div className={styles.resultWrap}>

              {/* Hero */}
              <div className={styles.conditionHero} style={{ borderColor: tierColor + '60', background: tierColor + '10' }}>
                <span className={styles.conditionEmoji}>{result.emoji}</span>
                <div>
                  <p className={styles.conditionLabel} style={{ color: tierColor }}>{result.prediction}</p>
                  <p className={styles.conditionSub}>{result.recommendation}</p>
                </div>
                <div className={styles.confidencePill} style={{ background: tierColor + '20', color: tierColor }}>
                  {(result.confidence * 100).toFixed(1)}%
                </div>
              </div>

              {/* Top 3 */}
              {result.top3 && (
                <div className={styles.infoBlock}>
                  <div className={styles.infoBlockHeader}>
                    <span className={styles.infoBlockIcon}>🏆</span>
                    <span className={styles.infoBlockTitle}>Top Predictions</span>
                  </div>
                  {result.top3.map((item, idx) => (
                    <div key={item.class} className={styles.barRow}>
                      <div className={styles.barLabel}>
                        <span>{idx + 1}. {item.class}</span>
                        <span>{(item.probability * 100).toFixed(1)}%</span>
                      </div>
                      <div className={styles.barTrack}>
                        <div
                          className={styles.barFill}
                          style={{ width: `${item.probability * 100}%`, background: idx === 0 ? tierColor : '#94a3b8' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* All probabilities mini-grid */}
              {result.all_probabilities && (
                <div className={styles.infoBlock}>
                  <div className={styles.infoBlockHeader}>
                    <span className={styles.infoBlockIcon}>📊</span>
                    <span className={styles.infoBlockTitle}>All Classes</span>
                  </div>
                  <div className={styles.miniGrid}>
                    {Object.entries(result.all_probabilities).map(([cls, prob]) => (
                      <div key={cls} className={styles.miniCell}>
                        <span className={styles.miniLabel}>{cls}</span>
                        <span className={styles.miniValue} style={{ color: prob > 0.15 ? tierColor : 'var(--text-muted)' }}>
                          {(prob * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
