import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './FishFreshness.module.css'
import { API_BASE_URL } from '../config'

const GRADE_COLORS = {
  C1: { bg: '#f0fdf4', border: '#86efac', text: '#16a34a' },
  C2: { bg: '#fffbeb', border: '#fcd34d', text: '#d97706' },
  C3: { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626' },
}

export default function FishFreshness() {
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
      const res = await fetch(`${API_BASE_URL}/predict-fish-freshness`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult(data)
    } catch (err) {
      const msg =
        err?.message === 'Failed to fetch'
          ? 'Cannot reach backend API. Start backend on port 8000 and retry.'
          : err.message
      setResult({ error: msg })
    } finally {
      setLoading(false)
    }
  }

  const grade      = result?.grade ?? 'C1'
  const gradeColor = GRADE_COLORS[grade] ?? GRADE_COLORS.C1

  // Score ring colour
  const scoreColor =
    result?.score >= 80
      ? '#16a34a'
      : result?.score >= 45
      ? '#d97706'
      : '#dc2626'

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🐟</div>
        <div>
          <h1 className={styles.title}>Fish Freshness Analysis</h1>
          <p className={styles.subtitle}>
            Upload a photo of your fish and get an instant freshness score (0–100)
            along with a quality grade and actionable insights.
          </p>
        </div>
      </div>

      {/* ── Grade legend ── */}
      <div className={styles.legend}>
        {[
          { grade: 'C1', label: 'Very Fresh',        color: GRADE_COLORS.C1 },
          { grade: 'C2', label: 'Moderately Fresh',  color: GRADE_COLORS.C2 },
          { grade: 'C3', label: 'Not Fresh',         color: GRADE_COLORS.C3 },
        ].map(({ grade: g, label, color }) => (
          <div key={g} className={styles.legendItem}>
            <span
              className={styles.legendDot}
              style={{ background: color.text }}
            />
            <span className={styles.legendGrade} style={{ color: color.text }}>
              {g}
            </span>
            <span className={styles.legendLabel}>{label}</span>
          </div>
        ))}
      </div>

      {/* ── Main layout ── */}
      <div className={styles.layout}>

        {/* ── Upload panel ── */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Fish Image</p>

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
                <span className={styles.dropzoneIcon}>🐟</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>PNG, JPG, WEBP — clear fish photo</p>
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
                : '✨ Check Freshness'
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
              <span className={styles.emptyIcon}>🐟</span>
              <p className={styles.emptyText}>Your freshness report will appear here</p>
              <p className={styles.emptyHint}>Upload a fish photo and click Check Freshness</p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Analyzing freshness…</p>
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

              {/* Score ring + grade hero */}
              <div
                className={styles.scoreHero}
                style={{ background: gradeColor.bg, borderColor: gradeColor.border }}
              >
                {/* Score ring */}
                <div className={styles.scoreRingWrap}>
                  <svg className={styles.scoreRing} viewBox="0 0 80 80">
                    <circle
                      cx="40" cy="40" r="34"
                      fill="none"
                      stroke="var(--border)"
                      strokeWidth="7"
                    />
                    <circle
                      cx="40" cy="40" r="34"
                      fill="none"
                      stroke={scoreColor}
                      strokeWidth="7"
                      strokeLinecap="round"
                      strokeDasharray={`${2 * Math.PI * 34}`}
                      strokeDashoffset={`${2 * Math.PI * 34 * (1 - result.score / 100)}`}
                      transform="rotate(-90 40 40)"
                      style={{ transition: 'stroke-dashoffset 0.8s ease' }}
                    />
                  </svg>
                  <div className={styles.scoreRingInner}>
                    <span className={styles.scoreNum} style={{ color: scoreColor }}>
                      {result.score}
                    </span>
                    <span className={styles.scoreLabel}>/ 100</span>
                  </div>
                </div>

                {/* Grade info */}
                <div className={styles.gradeInfo}>
                  <div className={styles.gradeRow}>
                    <span className={styles.gradeEmoji}>{result.emoji}</span>
                    <span
                      className={styles.gradeBadge}
                      style={{ background: gradeColor.border, color: gradeColor.text }}
                    >
                      Grade {result.grade}
                    </span>
                  </div>
                  <p
                    className={styles.gradeLabel}
                    style={{ color: gradeColor.text }}
                  >
                    {result.label}
                  </p>
                  <p className={styles.gradeDesc}>{result.description}</p>
                </div>
              </div>

              {/* Confidence bar */}
              <div className={styles.confBarWrap}>
                <div className={styles.confBarLabel}>
                  <span>Model confidence</span>
                  <span>{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className={styles.confBarTrack}>
                  <div
                    className={styles.confBarFill}
                    style={{
                      width: `${(result.confidence * 100).toFixed(1)}%`,
                      background: gradeColor.text,
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
                      <span
                        className={styles.cueDot}
                        style={{ background: gradeColor.text }}
                      />
                      {cue}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommendation */}
              <div
                className={styles.adviceBlock}
                style={{ background: gradeColor.bg, borderColor: gradeColor.border }}
              >
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>
                    {result.grade === 'C1' ? '✅' : result.grade === 'C2' ? '⚠️' : '🚫'}
                  </span>
                  <span className={styles.infoBlockTitle}>Recommendation</span>
                </div>
                <p className={styles.infoBlockText}>{result.recommendation}</p>
              </div>

              {/* Grade probabilities */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>Grade Probabilities</span>
                </div>
                <div className={styles.probBars}>
                  {Object.entries(result.probabilities).map(([cls, prob]) => (
                    <div key={cls} className={styles.probBarRow}>
                      <span className={styles.probBarLabel}>{cls}</span>
                      <div className={styles.probBarTrack}>
                        <div
                          className={styles.probBarFill}
                          style={{
                            width: `${(prob * 100).toFixed(1)}%`,
                            background: GRADE_COLORS[cls]?.text ?? 'var(--primary)',
                          }}
                        />
                      </div>
                      <span className={styles.probBarValue}>
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
