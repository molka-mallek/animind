import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './EyeInfection.module.css'

const CONDITION_COLORS = {
  infected: { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626' },
  normal: { bg: '#f0fdf4', border: '#86efac', text: '#16a34a' },
}

export default function BirdDroppings() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const fileRef = useRef(null)

  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    if (!file.type.startsWith('image/')) return
    setResult(null)
    fileRef.current = file
    setPreview(URL.createObjectURL(file))
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  function clearFile() {
    setPreview(null)
    setResult(null)
    fileRef.current = null
    if (inputRef.current) inputRef.current.value = ''
  }

  async function handleAnalyze() {
    if (!fileRef.current) return
    setLoading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', fileRef.current)
      const res = await fetch('http://127.0.0.1:8000/predict-bird-droppings', { method: 'POST', body: formData })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult({
        condition: data.condition,
        rawLabel: data.raw_label,
        confidence: (data.confidence * 100).toFixed(1),
        emoji: data.emoji,
        cues: data.cues,
        description: data.description,
        recommendation: data.recommendation,
      })
    } catch (err) {
      const msg = err?.message === 'Failed to fetch'
        ? 'Cannot reach backend API. Start backend on port 8000 and retry.'
        : err.message
      setResult({ error: msg })
    } finally {
      setLoading(false)
    }
  }

  const conditionColor = CONDITION_COLORS[result?.condition] ?? CONDITION_COLORS.normal

  return (
    <div className={styles.page}>
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      <div className={styles.header}>
        <div className={styles.headerIcon}>🧪</div>
        <div>
          <h1 className={styles.title}>Bird Droppings Analysis</h1>
          <p className={styles.subtitle}>Upload a droppings image to screen for signs of possible infection.</p>
        </div>
      </div>

      <div className={styles.layout}>
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Image</p>
          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              <img src={preview} alt="Preview" className={styles.preview} />
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>📷</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>PNG, JPG, WEBP</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className={styles.fileInput}
            onChange={(e) => handleFile(e.target.files[0])}
          />

          <div className={styles.actions}>
            {preview && <button className={styles.btnSecondary} onClick={clearFile}>Clear</button>}
            <button className={styles.btnPrimary} onClick={handleAnalyze} disabled={!preview || loading}>
              {loading ? <><span className={styles.spinnerInline} /> Analyzing…</> : '✨ Analyze'}
            </button>
          </div>
        </div>

        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🧪</span>
              <p className={styles.emptyText}>Your analysis will appear here</p>
              <p className={styles.emptyHint}>Upload a file and click Analyze</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Running model inference…</p>
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
              <div className={styles.conditionHero} style={{ background: conditionColor.bg, borderColor: conditionColor.border }}>
                <span className={styles.conditionEmoji}>{result.emoji}</span>
                <div>
                  <p className={styles.conditionLabel} style={{ color: conditionColor.text }}>{String(result.rawLabel || result.condition).toUpperCase()}</p>
                  <p className={styles.conditionSub}>{result.description}</p>
                </div>
                <div className={styles.confidencePill} style={{ background: conditionColor.border }}>
                  <span style={{ color: conditionColor.text }}>{result.confidence}%</span>
                </div>
              </div>

              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>🔍</span>
                  <span className={styles.infoBlockTitle}>Indicators</span>
                </div>
                <ul className={styles.cueList}>
                  {result.cues.map((cue, i) => (
                    <li key={i} className={styles.cueItem}>
                      <span className={styles.cueDot} style={{ background: conditionColor.text }} />
                      {cue}
                    </li>
                  ))}
                </ul>
              </div>

              <div className={styles.adviceBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>💡</span>
                  <span className={styles.infoBlockTitle}>Recommendation</span>
                </div>
                <p className={styles.infoBlockText}>{result.recommendation}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
