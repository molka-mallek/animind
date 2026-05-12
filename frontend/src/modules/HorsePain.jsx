import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './HorsePain.module.css'

export default function HorsePain() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [fileName, setFileName] = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    const isVideo = file.type.startsWith('video/') || /\.(mp4|mov|avi|mkv|webm)$/i.test(file.name)
    if (!isVideo) return
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
      const res = await fetch('http://127.0.0.1:8000/predict-horse-pain', {
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

  const isPain = result?.prediction === 'Pain Detected'

  return (
    <div className={styles.page}>

      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      <div className={styles.header}>
        <div className={styles.headerIcon}>🐴</div>
        <div>
          <h1 className={styles.title}>Horse Pain Detection</h1>
          <p className={styles.subtitle}>
            Upload a horse video to detect pain indicators through BiLSTM behavioral
            analysis of movement patterns and gait.
          </p>
        </div>
      </div>

      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Video</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${fileName ? styles.hasFile : ''}`}
            onClick={() => inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {fileName ? (
              <div className={styles.videoPreview}>
                <span className={styles.videoIcon}>🎬</span>
                <div>
                  <p className={styles.videoName}>{fileName}</p>
                  <span className={styles.videoReady}>Ready to analyze</span>
                </div>
              </div>
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🎥</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>MP4, MOV, AVI — horse movement video</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="video/*,.mp4,.mov,.avi,.mkv"
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
                : '🐴 Detect Pain'
              }
            </button>
          </div>

          <div className={styles.howItWorks}>
            <p className={styles.howTitle}>How it works</p>
            <div className={styles.howSteps}>
              <div className={styles.howStep}><span className={styles.howNum}>1</span><span className={styles.howLabel}>Video frames</span></div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}><span className={styles.howNum}>2</span><span className={styles.howLabel}>Optical flow</span></div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}><span className={styles.howNum}>3</span><span className={styles.howLabel}>BiLSTM classifier</span></div>
            </div>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🐴</span>
              <p className={styles.emptyText}>Pain analysis will appear here</p>
              <p className={styles.emptyHint}>Upload a horse video and click Detect Pain</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Analyzing horse behavior…</p>
              <p className={styles.emptyHint}>Extracting motion features and running BiLSTM</p>
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

              {/* Prediction hero */}
              <div
                className={styles.predHero}
                style={{
                  background:   result.bg,
                  borderColor:  result.border,
                }}
              >
                <span className={styles.predEmoji}>{result.emoji}</span>
                <div>
                  <p className={styles.predLabel} style={{ color: result.color }}>
                    {result.prediction.toUpperCase()}
                  </p>
                  <p className={styles.predSub}>Behavioral analysis result</p>
                </div>
                <div className={styles.confPill} style={{ background: result.border }}>
                  <span style={{ color: result.color }}>{result.confidence}%</span>
                </div>
              </div>

              {/* Pain alert */}
              {isPain && (
                <div className={styles.painAlert}>
                  <span>⚠️</span>
                  <div>
                    <p className={styles.painAlertTitle}>PAIN INDICATORS DETECTED</p>
                    <p className={styles.painAlertSub}>Consult an equine veterinarian promptly.</p>
                  </div>
                </div>
              )}

              {/* Probability bars */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>Probability Breakdown</span>
                </div>
                <div className={styles.probBars}>
                  <div className={styles.probBarRow}>
                    <span className={styles.probBarLabel}>Pain Detected</span>
                    <div className={styles.probBarTrack}>
                      <div className={styles.probBarFillRed} style={{ width: `${result.pain_probability}%` }} />
                    </div>
                    <span className={styles.probBarValue}>{result.pain_probability}%</span>
                  </div>
                  <div className={styles.probBarRow}>
                    <span className={styles.probBarLabel}>No Pain</span>
                    <div className={styles.probBarTrack}>
                      <div className={styles.probBarFillGreen} style={{ width: `${result.no_pain_probability}%` }} />
                    </div>
                    <span className={styles.probBarValue}>{result.no_pain_probability}%</span>
                  </div>
                </div>
              </div>

              {/* Behavioral indicators */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>👁️</span>
                  <span className={styles.infoBlockTitle}>Behavioral Indicators</span>
                </div>
                <ul className={styles.indicatorList}>
                  {result.behavioral_indicators.map((ind, i) => (
                    <li key={i} className={styles.indicatorItem}>
                      <span className={styles.indicatorDot} style={{ background: result.color }} />
                      {ind}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Description */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>🧠</span>
                  <span className={styles.infoBlockTitle}>Analysis</span>
                </div>
                <p className={styles.infoBlockText}>{result.description}</p>
              </div>

              {/* Advice */}
              <div className={isPain ? styles.adviceBlockAlert : styles.adviceBlock}>
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
