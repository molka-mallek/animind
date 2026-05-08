import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './SkinAnomaly.module.css'

const STATUS_COLORS = {
  anomaly: { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626' },
  healthy: { bg: '#f0fdf4', border: '#86efac', text: '#16a34a' },
}

export default function SkinAnomaly() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [preview,  setPreview]  = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return
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
      const res = await fetch('http://127.0.0.1:8000/predict-skin-anomaly', { method: 'POST', body: formData })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult(data)
    } catch (err) {
      const msg = err?.message === 'Failed to fetch'
        ? 'Cannot reach backend API. Start backend on port 8000 and retry.'
        : err.message
      setResult({ error: msg })
    } finally {
      setLoading(false)
    }
  }

  const statusColor = STATUS_COLORS[result?.status] ?? STATUS_COLORS.healthy

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🔬</div>
        <div>
          <h1 className={styles.title}>Cat & Dog Skin Anomaly Detection</h1>
          <p className={styles.subtitle}>
            Upload a photo of your cat or dog. The AI will identify the animal,
            detect any skin anomaly, and — if needed — highlight the affected area
            using segmentation.
          </p>
        </div>
      </div>

      {/* ── Pipeline steps badge ── */}
      <div className={styles.steps}>
        <div className={styles.step}>
          <span className={styles.stepNum}>1</span>
          <span className={styles.stepLabel}>Identify animal</span>
        </div>
        <div className={styles.stepArrow}>→</div>
        <div className={styles.step}>
          <span className={styles.stepNum}>2</span>
          <span className={styles.stepLabel}>Detect anomaly</span>
        </div>
        <div className={styles.stepArrow}>→</div>
        <div className={styles.step}>
          <span className={styles.stepNum}>3</span>
          <span className={styles.stepLabel}>Segment affected area</span>
        </div>
      </div>

      {/* ── Main layout ── */}
      <div className={styles.layout}>

        {/* ── Upload panel ── */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Image</p>

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
                <span className={styles.dropzoneIcon}>🐾</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>PNG, JPG, WEBP — cat or dog photo</p>
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
                : '✨ Analyze Skin'
              }
            </button>
          </div>
        </div>

        {/* ── Result panel ── */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {/* Empty state */}
          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🔬</span>
              <p className={styles.emptyText}>Your analysis will appear here</p>
              <p className={styles.emptyHint}>Upload a photo and click Analyze Skin</p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Running 3-step pipeline…</p>
              <p className={styles.emptyHint}>Classification → Detection → Segmentation</p>
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

              {/* ── Step 1: Animal classification ── */}
              <div className={styles.stepCard}>
                <div className={styles.stepCardHeader}>
                  <span className={styles.stepBadge}>Step 1</span>
                  <span className={styles.stepCardTitle}>Animal Identified</span>
                </div>
                <div className={styles.animalRow}>
                  <span className={styles.animalEmoji}>{result.animal_emoji}</span>
                  <div>
                    <p className={styles.animalLabel}>{result.animal_label}</p>
                    <p className={styles.animalConf}>Confidence: {result.animal_confidence}%</p>
                  </div>
                  <div className={styles.confBarMini}>
                    <div
                      className={styles.confBarMiniFill}
                      style={{ width: `${result.animal_confidence}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* ── Step 2: Anomaly detection verdict ── */}
              <div
                className={styles.verdictHero}
                style={{ background: statusColor.bg, borderColor: statusColor.border }}
              >
                <div className={styles.stepCardHeader}>
                  <span className={styles.stepBadge}>Step 2</span>
                  <span className={styles.stepCardTitle}>Skin Analysis</span>
                </div>
                <div className={styles.verdictRow}>
                  <span className={styles.verdictEmoji}>{result.status_emoji}</span>
                  <div>
                    <p
                      className={styles.verdictLabel}
                      style={{ color: statusColor.text }}
                    >
                      {result.status_label}
                    </p>
                    <p className={styles.verdictDesc}>{result.status_description}</p>
                  </div>
                  <div
                    className={styles.confidencePill}
                    style={{ background: statusColor.border }}
                  >
                    <span style={{ color: statusColor.text }}>
                      {result.verdict_confidence}%
                    </span>
                  </div>
                </div>

                {/* Probability bars */}
                <div className={styles.probBars}>
                  <div className={styles.probBarRow}>
                    <span className={styles.probBarLabel}>Anomaly</span>
                    <div className={styles.probBarTrack}>
                      <div
                        className={styles.probBarFill}
                        style={{ width: `${result.p_anomaly}%`, background: '#dc2626' }}
                      />
                    </div>
                    <span className={styles.probBarValue}>{result.p_anomaly}%</span>
                  </div>
                  <div className={styles.probBarRow}>
                    <span className={styles.probBarLabel}>Healthy</span>
                    <div className={styles.probBarTrack}>
                      <div
                        className={styles.probBarFill}
                        style={{ width: `${result.p_healthy}%`, background: '#16a34a' }}
                      />
                    </div>
                    <span className={styles.probBarValue}>{result.p_healthy}%</span>
                  </div>
                </div>
              </div>

              {/* ── Step 3: Segmentation (only if anomaly) ── */}
              {result.segmentation_done && (
                <div className={styles.stepCard}>
                  <div className={styles.stepCardHeader}>
                    <span className={styles.stepBadge}>Step 3</span>
                    <span className={styles.stepCardTitle}>Affected Area — Segmentation</span>
                  </div>
                  {result.seg_overlay ? (
                    <>
                      <img
                        src={result.seg_overlay}
                        alt="Segmentation overlay"
                        className={styles.segOverlay}
                      />
                      <p className={styles.segAreaText}>
                        Estimated affected area:{' '}
                        <strong style={{ color: '#dc2626' }}>{result.seg_area_pct}%</strong>{' '}
                        of the image
                      </p>
                    </>
                  ) : (
                    <p className={styles.segAreaText}>Segmentation map unavailable.</p>
                  )}
                </div>
              )}

              {/* ── Visual cues ── */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>🔍</span>
                  <span className={styles.infoBlockTitle}>Visual Indicators</span>
                </div>
                <ul className={styles.cueList}>
                  {result.cues.map((cue, i) => (
                    <li key={i} className={styles.cueItem}>
                      <span
                        className={styles.cueDot}
                        style={{ background: statusColor.text }}
                      />
                      {cue}
                    </li>
                  ))}
                </ul>
              </div>

              {/* ── Recommendation ── */}
              <div
                className={styles.adviceBlock}
                style={{
                  background: statusColor.bg,
                  borderColor: statusColor.border,
                }}
              >
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>
                    {result.status === 'anomaly' ? '💊' : '✅'}
                  </span>
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
