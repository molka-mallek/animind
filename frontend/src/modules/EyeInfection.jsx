import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './EyeInfection.module.css'

const CONDITION_COLORS = {
  infected: { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626' },
  normal:   { bg: '#f0fdf4', border: '#86efac', text: '#16a34a' },
}

export default function EyeInfection() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const fileRef  = useRef(null)

  const [preview, setPreview] = useState(null)
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    const isImage = file.type.startsWith('image/')
    if (!isImage) return
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
      const endpoint = 'http://127.0.0.1:8000/predict-eye-infection'
      const res  = await fetch(endpoint, { method: 'POST', body: formData })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult({
        condition:    data.condition,
        confidence:   (data.confidence * 100).toFixed(1),
        emoji:        data.emoji,
        cues:         data.cues,
        description:  data.description,
        recommendation: data.recommendation,
        probabilities: data.probabilities
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

  const conditionKey   = result?.condition?.toLowerCase()
  const conditionColor = CONDITION_COLORS[conditionKey] ?? CONDITION_COLORS.normal

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>👁️</div>
        <div>
          <h1 className={styles.title}>Cat & Dog Eye Infection Screening</h1>
          <p className={styles.subtitle}>
            Upload a clear photo of your pet's eye to screen for possible signs of infection.
            Our AI model analyzes the image and provides instant feedback.
          </p>
        </div>
      </div>

      {/* ── Main layout ── */}
      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Eye Image</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              <img src={preview} alt="Preview" className={styles.preview} />
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>👁️</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>PNG, JPG, WEBP (clear eye close-up)</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className={styles.fileInput}
            onChange={e => handleFile(e.target.files[0])}
          />

          <div className={styles.actions}>
            {preview && (
              <button className={styles.btnSecondary} onClick={clearFile}>
                Clear
              </button>
            )}
            <button
              className={styles.btnPrimary}
              onClick={handleAnalyze}
              disabled={!preview || loading}
            >
              {loading
                ? <><span className={styles.spinnerInline} /> Analyzing…</>
                : '✨ Analyze Eye'
              }
            </button>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {/* Empty state */}
          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>👁️</span>
              <p className={styles.emptyText}>Your analysis will appear here</p>
              <p className={styles.emptyHint}>Upload a clear eye photo and click Analyze</p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Running model inference…</p>
              <p className={styles.emptyHint}>This may take a few seconds</p>
            </div>
          )}

          {/* Error */}
          {result?.error && (
            <div className={styles.errorBox}>
              <span>⚠️</span>
              <div>
                <p className={styles.errorTitle}>Something went wrong</p>
                <p className={styles.errorMsg}>{result.error}</p>
              </div>
            </div>
          )}

          {/* Success */}
          {result && !result.error && (
            <div className={styles.resultWrap}>

              {/* Condition hero */}
              <div
                className={styles.conditionHero}
                style={{
                  background: conditionColor.bg,
                  borderColor: conditionColor.border,
                }}
              >
                <span className={styles.conditionEmoji}>{result.emoji}</span>
                <div>
                  <p
                    className={styles.conditionLabel}
                    style={{ color: conditionColor.text }}
                  >
                    {result.condition.toUpperCase()}
                  </p>
                  <p className={styles.conditionSub}>{result.description}</p>
                </div>
                <div className={styles.confidencePill} style={{ background: conditionColor.border }}>
                  <span style={{ color: conditionColor.text }}>{result.confidence}%</span>
                </div>
              </div>

              {/* Confidence bar */}
              <div className={styles.confBarWrap}>
                <div className={styles.confBarLabel}>
                  <span>Confidence</span>
                  <span>{result.confidence}%</span>
                </div>
                <div className={styles.confBarTrack}>
                  <div
                    className={styles.confBarFill}
                    style={{
                      width: `${result.confidence}%`,
                      background: conditionColor.text,
                    }}
                  />
                </div>
              </div>

              {/* Visual cues */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>🔍</span>
                  <span className={styles.infoBlockTitle}>Visual Indicators</span>
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

              {/* Recommendation */}
              <div className={styles.adviceBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>💊</span>
                  <span className={styles.infoBlockTitle}>Recommendation</span>
                </div>
                <p className={styles.infoBlockText}>{result.recommendation}</p>
              </div>

              {/* Probability details */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>Model Confidence Details</span>
                </div>
                <div className={styles.probDetails}>
                  <div className={styles.probItem}>
                    <span className={styles.probLabel}>Infected</span>
                    <span className={styles.probValue}>{(result.probabilities.infected * 100).toFixed(1)}%</span>
                  </div>
                  <div className={styles.probItem}>
                    <span className={styles.probLabel}>Normal</span>
                    <span className={styles.probValue}>{(result.probabilities.normal * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
