import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './HorsePain.module.css'

export default function HorsePain() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [preview,  setPreview]  = useState(null)   // video object URL
  const [fileName, setFileName] = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    if (!file.type.startsWith('video/')) return
    setResult(null)
    fileRef.current = file
    setFileName(file.name)
    setPreview(URL.createObjectURL(file))
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  function clearFile() {
    setPreview(null)
    setFileName(null)
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
      const res  = await fetch('http://127.0.0.1:8000/predict-horse-pain', { method: 'POST', body: formData })
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

  const isHealthy = result?.prediction === 'Healthy'

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🐴</div>
        <div>
          <h1 className={styles.title}>Horse Pain Detection</h1>
          <p className={styles.subtitle}>
            Upload a video of your horse. Our BiLSTM model analyzes movement patterns
            through optical-flow analysis to detect signs of pain or distress.
          </p>
        </div>
      </div>

      {/* ── Layout ── */}
      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Horse Video</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => !preview && inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              <video src={preview} className={styles.preview} controls muted />
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🐴</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>MP4, MOV, AVI — ideally 5–30 s of movement</p>
              </div>
            )}
          </div>

          {fileName && <p className={styles.fileName}>📎 {fileName}</p>}

          <input
            ref={inputRef}
            type="file"
            accept="video/*"
            className={styles.fileInput}
            onChange={e => handleFile(e.target.files[0])}
          />

          <div className={styles.actions}>
            {preview && (
              <button className={styles.btnSecondary} onClick={clearFile}>Clear</button>
            )}
            <button
              className={styles.btnPrimary}
              onClick={handleAnalyze}
              disabled={!preview || loading}
            >
              {loading ? <><span className={styles.spinnerInline} /> Analyzing…</> : '🔍 Analyze Video'}
            </button>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🐴</span>
              <p className={styles.emptyText}>Your analysis will appear here</p>
              <p className={styles.emptyHint}>Upload a video and click Analyze</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Running BiLSTM inference…</p>
              <p className={styles.emptyHint}>Extracting motion features from video</p>
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
              <div className={`${styles.conditionHero} ${isHealthy ? styles.heroHealthy : styles.heroDistressed}`}>
                <span className={styles.conditionEmoji}>{result.emoji}</span>
                <div>
                  <p className={styles.conditionLabel}>{result.prediction.toUpperCase()}</p>
                  <p className={styles.conditionSub}>{result.recommendation}</p>
                </div>
                <div className={`${styles.confidencePill} ${isHealthy ? styles.pillHealthy : styles.pillDistressed}`}>
                  {(result.confidence * 100).toFixed(1)}%
                </div>
              </div>

              {/* Probability bars */}
              {result.probabilities && (
                <div className={styles.infoBlock}>
                  <div className={styles.infoBlockHeader}>
                    <span className={styles.infoBlockIcon}>📊</span>
                    <span className={styles.infoBlockTitle}>Model Confidence</span>
                  </div>
                  {Object.entries(result.probabilities).map(([label, prob]) => (
                    <div key={label} className={styles.barRow}>
                      <div className={styles.barLabel}>
                        <span>{label}</span><span>{(prob * 100).toFixed(1)}%</span>
                      </div>
                      <div className={styles.barTrack}>
                        <div
                          className={styles.barFill}
                          style={{
                            width: `${prob * 100}%`,
                            background: label === 'Healthy' ? '#16a34a' : '#dc2626',
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Video info */}
              {result.video_info && (
                <div className={styles.infoBlock}>
                  <div className={styles.infoBlockHeader}>
                    <span className={styles.infoBlockIcon}>🎬</span>
                    <span className={styles.infoBlockTitle}>Video Analysis Info</span>
                  </div>
                  <p className={styles.infoBlockText}>
                    {result.video_info.frames} motion frames analyzed &nbsp;·&nbsp; sequence length: {result.video_info.seq_len}
                  </p>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
