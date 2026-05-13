import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './CatSound.module.css'
import { API_BASE_URL } from '../config'

const TIER_COLORS = {
  1: { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626', icon: '🔴' },
  2: { bg: '#fff7ed', border: '#fdba74', text: '#ea580c', icon: '🟠' },
  3: { bg: '#f0fdf4', border: '#86efac', text: '#16a34a', icon: '🟢' },
  4: { bg: '#f9fafb', border: '#d1d5db', text: '#6b7280', icon: '⚪' },
}

const CLASS_DESCRIPTIONS = {
  Angry:       'Expressing aggression or irritation',
  Defence:     'Feeling threatened — defensive posture',
  Fighting:    'Engaged in or anticipating a fight',
  Happy:       'Content and expressing positive emotions',
  HuntingMind: 'Focused hunting or stalking mindset',
  Mating:      'Vocalizing for mating purposes',
  MotherCall:  'Mother communicating with kittens',
  Paining:     'Vocalizing due to pain or severe distress',
  Resting:     'Relaxed and at ease',
  Warning:     'Issuing a warning signal to a threat',
}

export default function CatSound() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [fileName, setFileName] = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    const isAudio = file.type.startsWith('audio/') || /\.(wav|mp3|ogg|flac|m4a|aac)$/i.test(file.name)
    if (!isAudio) return
    setResult(null)
    fileRef.current = file
    setFileName(file.name)
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
  }

  async function handleAnalyze() {
    if (!fileRef.current) return
    setLoading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', fileRef.current)
      const res = await fetch(`${API_BASE_URL}/predict-cat-sound`, {
        method: 'POST',
        body: formData,
      })
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

  const tierColor = result ? (TIER_COLORS[result.tier] ?? TIER_COLORS[3]) : null

  return (
    <div className={styles.page}>

      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      <div className={styles.header}>
        <div className={styles.headerIcon}>🔊</div>
        <div>
          <h1 className={styles.title}>Cat Vocalization Classification</h1>
          <p className={styles.subtitle}>
            Upload a cat audio recording to classify vocalizations into 10 behavioral
            categories — with clinical pain detection alerts.
          </p>
        </div>
      </div>

      {/* Class chips */}
      <div className={styles.chips}>
        {Object.entries(CLASS_DESCRIPTIONS).map(([cls]) => (
          <span key={cls} className={styles.chip}>{cls}</span>
        ))}
      </div>

      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Audio File</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${fileName ? styles.hasFile : ''}`}
            onClick={() => inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {fileName ? (
              <div className={styles.audioFileInfo}>
                <span className={styles.audioIcon}>🎵</span>
                <div className={styles.audioMeta}>
                  <p className={styles.audioName}>{fileName}</p>
                  <p className={styles.audioHint}>Ready to analyze</p>
                </div>
                <div className={styles.audioWave}>
                  {[...Array(12)].map((_, i) => (
                    <div key={i} className={styles.audioBar} style={{ animationDelay: `${i * 0.08}s` }} />
                  ))}
                </div>
              </div>
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🔊</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>MP3, WAV, OGG, FLAC — ideally 1–3 seconds</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="audio/*,.wav,.mp3,.ogg,.flac,.m4a"
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
                ? <><span className={styles.spinnerInline} /> Analyzing…</>
                : '🔊 Classify Vocalization'
              }
            </button>
          </div>

          <div className={styles.howItWorks}>
            <p className={styles.howTitle}>How it works</p>
            <div className={styles.howSteps}>
              <div className={styles.howStep}><span className={styles.howNum}>1</span><span className={styles.howLabel}>Audio loaded</span></div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}><span className={styles.howNum}>2</span><span className={styles.howLabel}>YAMNet embeddings</span></div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}><span className={styles.howNum}>3</span><span className={styles.howLabel}>Head classifier</span></div>
            </div>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🐱</span>
              <p className={styles.emptyText}>Vocalization analysis will appear here</p>
              <p className={styles.emptyHint}>Upload an audio file and click Classify</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Analyzing vocalization…</p>
              <p className={styles.emptyHint}>Running YAMNet + head model inference</p>
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

              {/* Pain alert banner */}
              {result.pain_alert && (
                <div className={styles.painAlert}>
                  <span className={styles.painAlertIcon}>🚨</span>
                  <div>
                    <p className={styles.painAlertTitle}>PAIN DETECTED</p>
                    <p className={styles.painAlertSub}>
                      Pain probability: {result.pain_probability}% (threshold: {result.pain_threshold}%)
                    </p>
                  </div>
                </div>
              )}

              {/* Prediction hero */}
              <div
                className={styles.predHero}
                style={{ background: tierColor.bg, borderColor: tierColor.border }}
              >
                <span className={styles.predIcon}>{tierColor.icon}</span>
                <div>
                  <p className={styles.predLabel} style={{ color: tierColor.text }}>
                    {result.predicted_class}
                  </p>
                  <p className={styles.predSub}>
                    {CLASS_DESCRIPTIONS[result.predicted_class] ?? 'Detected vocalization'}
                  </p>
                </div>
                <div className={styles.confPill} style={{ background: tierColor.border }}>
                  <span style={{ color: tierColor.text }}>{result.confidence}%</span>
                </div>
              </div>

              {/* Confidence bar */}
              <div className={styles.confBarWrap}>
                <div className={styles.confBarLabel}>
                  <span>Confidence</span><span>{result.confidence}%</span>
                </div>
                <div className={styles.confBarTrack}>
                  <div className={styles.confBarFill} style={{ width: `${result.confidence}%`, background: tierColor.text }} />
                </div>
              </div>

              {/* Advice */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>💡</span>
                  <span className={styles.infoBlockTitle}>Recommendation</span>
                </div>
                <p className={styles.infoBlockText}>{result.advice}</p>
              </div>

              {/* All class probabilities */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>All Class Probabilities</span>
                </div>
                <div className={styles.probBars}>
                  {result.all_probabilities.map(item => {
                    const tc = TIER_COLORS[item.tier] ?? TIER_COLORS[3]
                    return (
                      <div key={item.class} className={styles.probBarRow}>
                        <span className={styles.probTierIcon}>{item.tier_icon}</span>
                        <span className={styles.probBarLabel}>{item.class}</span>
                        <div className={styles.probBarTrack}>
                          <div
                            className={styles.probBarFill}
                            style={{
                              width: `${item.probability}%`,
                              background: item.class === result.predicted_class ? tc.text : tc.border,
                            }}
                          />
                        </div>
                        <span className={styles.probBarValue}>{item.probability}%</span>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Tier legend */}
              <div className={styles.tierLegend}>
                <p className={styles.tierLegendTitle}>Clinical Priority Tiers</p>
                <div className={styles.tierLegendItems}>
                  {[
                    { tier: 1, label: 'Critical — immediate vet attention' },
                    { tier: 2, label: 'High — monitor closely' },
                    { tier: 3, label: 'Normal — no concern' },
                    { tier: 4, label: 'Neutral — natural behavior' },
                  ].map(({ tier, label }) => (
                    <div key={tier} className={styles.tierLegendItem}>
                      <span>{TIER_COLORS[tier].icon}</span>
                      <span className={styles.tierLegendLabel}>{label}</span>
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
