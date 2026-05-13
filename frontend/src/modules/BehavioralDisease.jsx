import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './BehavioralDisease.module.css'
import { API_BASE_URL } from '../config'

const CLASS_NAMES = ['Normal', 'Ataxia', 'Hip Dysplasia']

const CONDITION_META = {
  'Normal': {
    bg: '#f0fdf4', border: '#86efac', text: '#16a34a',
    emoji: '✅',
    description: "The dog's movement appears normal with no signs of neurological or musculoskeletal issues detected.",
  },
  'Ataxia': {
    bg: '#fef2f2', border: '#fca5a5', text: '#dc2626',
    emoji: '⚠️',
    description: 'Ataxia is a neurological condition causing loss of coordination. Signs include stumbling, swaying, or an unsteady gait. Consult a veterinarian promptly.',
  },
  'Hip Dysplasia': {
    bg: '#fffbeb', border: '#fcd34d', text: '#d97706',
    emoji: '🦴',
    description: "Hip dysplasia is a skeletal condition where the hip joint doesn't fit properly. Signs include a bunny-hop gait, reluctance to move, or hind-leg weakness. A vet evaluation is recommended.",
  },
}

function getMeta(label) {
  return CONDITION_META[label] ?? CONDITION_META['Normal']
}

export default function BehavioralDisease() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [preview,  setPreview]  = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    if (!file.type.startsWith('video/')) return
    setResult(null)
    fileRef.current = file
    setPreview(file.name)
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
      const res = await fetch(`${API_BASE_URL}/predict-ataxia`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult({
        prediction:  data.prediction,
        confidence:  (data.confidence * 100).toFixed(1),
        classScores: data.class_scores ?? {},
      })
    } catch (err) {
      const msg = err?.message === 'Failed to fetch'
        ? 'Cannot reach backend API. Make sure the backend is running on port 8000 and retry.'
        : err.message
      setResult({ error: msg })
    } finally {
      setLoading(false)
    }
  }

  const meta = result?.prediction ? getMeta(result.prediction) : null

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🧠</div>
        <div>
          <h1 className={styles.title}>Behavioral Disease Classification</h1>
          <p className={styles.subtitle}>
            Upload a short video of your dog walking or trotting. The ST-GCN model
            analyzes skeletal keypoints to classify the gait as Normal, Ataxia, or Hip Dysplasia.
          </p>
        </div>
      </div>

      {/* ── Main layout ── */}
      <div className={styles.layout}>

        {/* ── Upload panel ── */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Video</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => !preview && inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              <div className={styles.videoPreview}>
                <span className={styles.videoIcon}>🎬</span>
                <p className={styles.videoName}>{preview}</p>
                <span className={styles.videoReady}>Ready to analyze</span>
              </div>
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🎥</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>MP4, MOV, AVI — walking or trotting clip</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="video/*"
            className={styles.fileInput}
            onChange={e => handleFile(e.target.files[0])}
          />

          {/* Tips */}
          <div className={styles.tipsBox}>
            <p className={styles.tipsTitle}>📋 Tips for best results</p>
            <ul className={styles.tipsList}>
              <li>Film the dog walking or trotting on a flat surface</li>
              <li>Keep the full body visible throughout the clip</li>
              <li>Use good lighting and avoid shaky footage</li>
              <li>Aim for at least 3–5 seconds of movement</li>
            </ul>
          </div>

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
                : '🧠 Classify Behavior'
              }
            </button>
          </div>
        </div>

        {/* ── Result panel ── */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Classification Result</p>

          {/* Empty state */}
          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🧠</span>
              <p className={styles.emptyText}>Your classification will appear here</p>
              <p className={styles.emptyHint}>Upload a video and click Classify Behavior</p>
              {/* Class legend */}
              <div className={styles.legend}>
                {CLASS_NAMES.map(name => {
                  const m = getMeta(name)
                  return (
                    <div key={name} className={styles.legendItem}
                      style={{ background: m.bg, borderColor: m.border }}>
                      <span>{m.emoji}</span>
                      <span style={{ color: m.text }}>{name}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Running ST-GCN inference…</p>
              <p className={styles.emptyHint}>Extracting keypoints and classifying gait</p>
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
          {result && !result.error && meta && (
            <div className={styles.resultWrap}>

              {/* Condition hero */}
              <div
                className={styles.conditionHero}
                style={{ background: meta.bg, borderColor: meta.border }}
              >
                <span className={styles.conditionEmoji}>{meta.emoji}</span>
                <div>
                  <p className={styles.conditionLabel} style={{ color: meta.text }}>
                    {result.prediction.toUpperCase()}
                  </p>
                  <p className={styles.conditionSub}>Detected condition</p>
                </div>
                <div className={styles.confidencePill} style={{ background: meta.border }}>
                  <span style={{ color: meta.text }}>{result.confidence}%</span>
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
                    style={{ width: `${result.confidence}%`, background: meta.text }}
                  />
                </div>
              </div>

              {/* Per-class probability bars */}
              {Object.keys(result.classScores).length > 0 && (
                <div className={styles.infoBlock}>
                  <div className={styles.infoBlockHeader}>
                    <span className={styles.infoBlockIcon}>📊</span>
                    <span className={styles.infoBlockTitle}>All Class Probabilities</span>
                  </div>
                  <div className={styles.scoreList}>
                    {CLASS_NAMES.map(label => {
                      const score = result.classScores[label] ?? 0
                      const pct   = (score * 100).toFixed(1)
                      const m     = getMeta(label)
                      return (
                        <div key={label} className={styles.scoreItem}>
                          <div className={styles.scoreItemTop}>
                            <span className={styles.scoreLabel}>
                              {m.emoji} {label}
                            </span>
                            <span className={styles.scoreValue} style={{ color: m.text }}>
                              {pct}%
                            </span>
                          </div>
                          <div className={styles.scoreTrack}>
                            <div
                              className={styles.scoreFill}
                              style={{ width: `${pct}%`, background: m.text }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* What this means */}
              <div
                className={styles.adviceBlock}
                style={{ background: meta.bg, borderColor: meta.border }}
              >
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>💡</span>
                  <span className={styles.infoBlockTitle}>What this means</span>
                </div>
                <p className={styles.infoBlockText}>{meta.description}</p>
              </div>

              {/* Disclaimer */}
              <div className={styles.disclaimer}>
                <span>ℹ️</span>
                <p>This is an AI-assisted screening tool, not a veterinary diagnosis. Always consult a licensed veterinarian for medical decisions.</p>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
