import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './ThermalCat.module.css'

export default function ThermalCat() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [preview,  setPreview]  = useState(null)
  const [fileName, setFileName] = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)

  function handleFile(file) {
    if (!file) return
    if (!file.type.startsWith('image/')) return
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
      const res  = await fetch('http://127.0.0.1:8000/predict-thermal-cat', { method: 'POST', body: formData })
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

      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      <div className={styles.header}>
        <div className={styles.headerIcon}>🌡️</div>
        <div>
          <h1 className={styles.title}>Thermal Cat Health Screening</h1>
          <p className={styles.subtitle}>
            Upload a thermal image of your cat. Our ensemble of EfficientNet-B3,
            ResNet50, and Custom CNN screens for signs of illness via thermal pattern analysis.
          </p>
        </div>
      </div>

      <div className={styles.layout}>

        {/* Upload panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Upload Thermal Image</p>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''} ${preview ? styles.hasFile : ''}`}
            onClick={() => !preview && inputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
          >
            {preview ? (
              <img src={preview} alt="Thermal cat preview" className={styles.preview} />
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🌡️</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>JPG, PNG — thermal camera image recommended</p>
              </div>
            )}
          </div>

          {fileName && <p className={styles.fileName}>📎 {fileName}</p>}

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
              {loading ? <><span className={styles.spinnerInline} /> Scanning…</> : '🔍 Screen Health'}
            </button>
          </div>
        </div>

        {/* Result panel */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🌡️</span>
              <p className={styles.emptyText}>Your screening result will appear here</p>
              <p className={styles.emptyHint}>Upload a thermal image and click Screen</p>
            </div>
          )}

          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Running ensemble inference…</p>
              <p className={styles.emptyHint}>3 models are analyzing the thermal pattern</p>
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
              <div className={`${styles.conditionHero} ${isHealthy ? styles.heroHealthy : styles.heroSick}`}>
                <span className={styles.conditionEmoji}>{result.emoji}</span>
                <div>
                  <p className={styles.conditionLabel}>{result.prediction.toUpperCase()}</p>
                  <p className={styles.conditionSub}>{result.recommendation}</p>
                </div>
                <div className={`${styles.confidencePill} ${isHealthy ? styles.pillHealthy : styles.pillSick}`}>
                  {(result.confidence * 100).toFixed(1)}%
                </div>
              </div>

              {/* Sick / Healthy probability bar */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>Ensemble Probabilities</span>
                </div>
                <div className={styles.barRow}>
                  <div className={styles.barLabel}><span>Healthy</span><span>{result.healthy_probability}%</span></div>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{ width: `${result.healthy_probability}%`, background: '#16a34a' }} />
                  </div>
                </div>
                <div className={styles.barRow}>
                  <div className={styles.barLabel}><span>Sick</span><span>{result.sick_probability}%</span></div>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{ width: `${result.sick_probability}%`, background: '#dc2626' }} />
                  </div>
                </div>
                <p className={styles.thresholdNote}>⚡ Decision threshold: {result.threshold}%</p>
              </div>

              {/* Per-model breakdown */}
              {result.per_model && (
                <div className={styles.infoBlock}>
                  <div className={styles.infoBlockHeader}>
                    <span className={styles.infoBlockIcon}>🧠</span>
                    <span className={styles.infoBlockTitle}>Per-Model Sick Probability</span>
                  </div>
                  {Object.entries(result.per_model).map(([name, prob]) => (
                    <div key={name} className={styles.barRow}>
                      <div className={styles.barLabel}>
                        <span>{name.replace(/_/g, ' ')}</span>
                        <span>{prob}%</span>
                      </div>
                      <div className={styles.barTrack}>
                        <div
                          className={styles.barFill}
                          style={{ width: `${prob}%`, background: prob >= result.threshold ? '#f97316' : '#94a3b8' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
