import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './ThermalCat.module.css'

export default function ThermalCat() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [preview,  setPreview]  = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
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
      const res = await fetch('http://127.0.0.1:8000/predict-thermal-cat', {
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

  const isSick = result?.prediction === 'Sick'

  return (
    <div className={styles.page}>

      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      <div className={styles.header}>
        <div className={styles.headerIcon}>🌡️</div>
        <div>
          <h1 className={styles.title}>Thermal Cat Classification</h1>
          <p className={styles.subtitle}>
            Upload a thermal image of your cat to screen for health issues.
            An ensemble of 3 AI models (CNN + EfficientNet-B3 + ResNet50) classifies
            Healthy vs Sick with high recall.
          </p>
        </div>
      </div>

      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Thermal Image</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              <img src={preview} alt="Thermal preview" className={styles.preview} />
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🌡️</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>PNG, JPG, WEBP — thermal cat image (RGB)</p>
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
              <button className={styles.btnSecondary} onClick={clearFile}>Clear</button>
            )}
            <button
              className={styles.btnPrimary}
              onClick={handleAnalyze}
              disabled={!preview || loading}
            >
              {loading
                ? <><span className={styles.spinnerInline} /> Analyzing…</>
                : '🌡️ Analyze Thermal Image'
              }
            </button>
          </div>

          <div className={styles.howItWorks}>
            <p className={styles.howTitle}>How it works</p>
            <div className={styles.howSteps}>
              <div className={styles.howStep}><span className={styles.howNum}>1</span><span className={styles.howLabel}>Thermal image</span></div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}><span className={styles.howNum}>2</span><span className={styles.howLabel}>3-model ensemble</span></div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}><span className={styles.howNum}>3</span><span className={styles.howLabel}>Healthy / Sick</span></div>
            </div>
          </div>

          {/* Disclaimer */}
          <div className={styles.disclaimer}>
            <span className={styles.disclaimerIcon}>ℹ️</span>
            <p className={styles.disclaimerText}>
              This is a screening tool, not a diagnosis. Always consult a licensed veterinarian.
            </p>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🌡️</span>
              <p className={styles.emptyText}>Health screening result will appear here</p>
              <p className={styles.emptyHint}>Upload a thermal image and click Analyze</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Analyzing thermal signature…</p>
              <p className={styles.emptyHint}>Running ensemble inference (CNN + EfficientNet + ResNet)</p>
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
                style={{ background: result.bg, borderColor: result.border }}
              >
                <span className={styles.predEmoji}>{result.emoji}</span>
                <div>
                  <p className={styles.predLabel} style={{ color: result.color }}>
                    {result.prediction.toUpperCase()}
                  </p>
                  <p className={styles.predSub}>Thermal health screening</p>
                </div>
                <div className={styles.confPill} style={{ background: result.border }}>
                  <span style={{ color: result.color }}>{result.confidence}%</span>
                </div>
              </div>

              {/* Sick alert */}
              {isSick && (
                <div className={styles.sickAlert}>
                  <span>⚠️</span>
                  <div>
                    <p className={styles.sickAlertTitle}>HEALTH CONCERN DETECTED</p>
                    <p className={styles.sickAlertSub}>Please consult a licensed veterinarian.</p>
                  </div>
                </div>
              )}

              {/* Confidence bar */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>Health Probability</span>
                </div>
                <div className={styles.probBars}>
                  <div className={styles.probBarRow}>
                    <span className={styles.probBarLabel}>Sick</span>
                    <div className={styles.probBarTrack}>
                      <div className={styles.probBarFillRed} style={{ width: `${result.sick_probability}%` }} />
                    </div>
                    <span className={styles.probBarValue}>{result.sick_probability}%</span>
                  </div>
                  <div className={styles.probBarRow}>
                    <span className={styles.probBarLabel}>Healthy</span>
                    <div className={styles.probBarTrack}>
                      <div className={styles.probBarFillGreen} style={{ width: `${result.healthy_probability}%` }} />
                    </div>
                    <span className={styles.probBarValue}>{result.healthy_probability}%</span>
                  </div>
                </div>
                <p className={styles.thresholdNote}>
                  Classification threshold: {result.threshold}% sick probability
                </p>
              </div>

              {/* Ensemble model scores */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>🤖</span>
                  <span className={styles.infoBlockTitle}>Ensemble Model Scores (Sick %)</span>
                </div>
                <div className={styles.modelScores}>
                  {Object.entries(result.model_scores).map(([name, score]) => (
                    <div key={name} className={styles.modelScoreRow}>
                      <span className={styles.modelScoreName}>{name.replace(/_/g, ' ')}</span>
                      <div className={styles.probBarTrack}>
                        <div
                          className={score > result.threshold ? styles.probBarFillRed : styles.probBarFillGreen}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                      <span className={styles.probBarValue}>{score}%</span>
                    </div>
                  ))}
                </div>
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
              <div className={isSick ? styles.adviceBlockAlert : styles.adviceBlock}>
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
