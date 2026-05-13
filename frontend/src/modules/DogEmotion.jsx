import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './DogEmotion.module.css'
import { API_BASE_URL } from '../config'

const MODE_TABS = [
  { id: 'image', label: '🖼️ Image', accept: 'image/*' },
  { id: 'video', label: '🎥 Video', accept: 'video/*' },
]

const EMOTION_COLORS = {
  happy:  { bg: '#f0fdf4', border: '#86efac', text: '#16a34a' },
  relax:  { bg: '#eff6ff', border: '#93c5fd', text: '#2563eb' },
  alert:  { bg: '#fffbeb', border: '#fcd34d', text: '#d97706' },
  frown:  { bg: '#fdf4ff', border: '#d8b4fe', text: '#9333ea' },
  angry:  { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626' },
}

export default function DogEmotion() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const fileRef  = useRef(null)

  const [mode, setMode]       = useState('image')
  const [preview, setPreview] = useState(null)
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    const isImage = file.type.startsWith('image/')
    const isVideo = file.type.startsWith('video/')
    if ((mode === 'image' && !isImage) || (mode === 'video' && !isVideo)) return
    setResult(null)
    fileRef.current = file
    setPreview(mode === 'image' ? URL.createObjectURL(file) : file.name)
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

  function switchMode(m) {
    setMode(m)
    clearFile()
  }

  async function handleAnalyze() {
    if (!fileRef.current) return
    setLoading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', fileRef.current)
      const endpoint = mode === 'image'
        ? `${API_BASE_URL}/predict`
        : `${API_BASE_URL}/predict-video`
      const res  = await fetch(endpoint, { method: 'POST', body: formData })
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult({
        emotion:    data.emotion,
        confidence: (data.confidence * 100).toFixed(1),
        emoji:      data.emoji,
        cues:       data.cues,
        body:       data.body,
        advice:     data.advice,
        evolution:  data.evolution   // 🔥 ADD THIS
      })
    } catch (err) {
      setResult({ error: err.message })
    } finally {
      setLoading(false)
    }
  }

  const emotionKey   = result?.emotion?.toLowerCase()
  const emotionColor = EMOTION_COLORS[emotionKey] ?? EMOTION_COLORS.relax

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🐶</div>
        <div>
          <h1 className={styles.title}>Dog Emotion Analysis</h1>
          <p className={styles.subtitle}>
            Upload a photo or video of your dog — the AI will detect its emotional state
            and give you behavioral insights.
          </p>
        </div>
      </div>

      {/* ── Mode tabs ── */}
      <div className={styles.tabs}>
        {MODE_TABS.map(t => (
          <button
            key={t.id}
            className={`${styles.tab} ${mode === t.id ? styles.tabActive : ''}`}
            onClick={() => switchMode(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Main layout ── */}
      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>
            Upload {mode === 'image' ? 'Image' : 'Video'}
          </p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              mode === 'image'
                ? <img src={preview} alt="Preview" className={styles.preview} />
                : (
                  <div className={styles.videoPreview}>
                    <span className={styles.videoIcon}>🎬</span>
                    <p className={styles.videoName}>{preview}</p>
                    <span className={styles.videoReady}>Ready to analyze</span>
                  </div>
                )
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>
                  {mode === 'image' ? '�' : '🎥'}
                </span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>
                  {mode === 'image' ? 'PNG, JPG, WEBP' : 'MP4, MOV, AVI'}
                </p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept={MODE_TABS.find(t => t.id === mode).accept}
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
                : '✨ Analyze Emotion'
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
              <span className={styles.emptyDog}>�</span>
              <p className={styles.emptyText}>Your analysis will appear here</p>
              <p className={styles.emptyHint}>Upload a file and click Analyze</p>
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

              {/* Emotion hero */}
              <div
                className={styles.emotionHero}
                style={{
                  background: emotionColor.bg,
                  borderColor: emotionColor.border,
                }}
              >
                <span className={styles.emotionEmoji}>{result.emoji}</span>
                <div>
                  <p
                    className={styles.emotionLabel}
                    style={{ color: emotionColor.text }}
                  >
                    {result.emotion.toUpperCase()}
                  </p>
                  <p className={styles.emotionSub}>Detected emotion</p>
                </div>
                <div className={styles.confidencePill} style={{ background: emotionColor.border }}>
                  <span style={{ color: emotionColor.text }}>{result.confidence}%</span>
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
                      background: emotionColor.text,
                    }}
                  />
                </div>
              </div>

              {/* Visual cues */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>👁️</span>
                  <span className={styles.infoBlockTitle}>Visual Cues</span>
                </div>
                <ul className={styles.cueList}>
                  {result.cues.map((cue, i) => (
                    <li key={i} className={styles.cueItem}>
                      <span className={styles.cueDot} style={{ background: emotionColor.text }} />
                      {cue}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Behavior */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>🧠</span>
                  <span className={styles.infoBlockTitle}>Behavior</span>
                </div>
                <p className={styles.infoBlockText}>{result.body}</p>
              </div>

              {/* Advice */}
              <div className={styles.adviceBlock}>
              {/* 🔥 Behavior Evolution */}
              {result.evolution && (
              <div className={styles.infoBlock}>
              <div className={styles.infoBlockHeader}>
              <span className={styles.infoBlockIcon}>📊</span>
              <span className={styles.infoBlockTitle}>Behavior Evolution</span>
              </div>
              <p className={styles.infoBlockText}>{result.evolution}</p>
              </div>
             )} 
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>💡</span>
                  <span className={styles.infoBlockTitle}>Recommendation</span>
                </div>
                <p className={styles.infoBlockText}>{result.advice}</p>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
