import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './BirdSpecies.module.css'

const SUPPORTED_SPECIES = [
  { key: 'Common_Cuckoo',           label: 'Common Cuckoo',            emoji: '🐦' },
  { key: 'Eurasian_Blackcap',       label: 'Eurasian Blackcap',        emoji: '🐦' },
  { key: 'Great_Tit',               label: 'Great Tit',                emoji: '🐦' },
  { key: 'Grey-breasted_Wood_Wren', label: 'Grey-breasted Wood Wren',  emoji: '🐦' },
  { key: 'House_Wren',              label: 'House Wren',               emoji: '🐦' },
]

// Local images served from /public — no external dependency
const SPECIES_IMAGES = {
  Common_Cuckoo:             '/common cuckoo.jpg',
  Eurasian_Blackcap:         '/Eurasian Blackcap.jpg',
  Great_Tit:                 '/Great Tit.jpg',
  'Grey-breasted_Wood_Wren': '/Grey-breasted Wood Wren.jpg',
  House_Wren:                '/House Wren.jpg',
}

export default function BirdSpecies() {
  const navigate  = useNavigate()
  const inputRef  = useRef(null)
  const fileRef   = useRef(null)

  const [fileName, setFileName] = useState(null)
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [imgError, setImgError] = useState(false)

  function handleFile(file) {
    if (!file) return
    const isAudio = file.type.startsWith('audio/') || /\.(wav|mp3|ogg|flac|m4a|aac)$/i.test(file.name)
    if (!isAudio) return
    setResult(null)
    setImgError(false)
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
    setImgError(false)
    fileRef.current = null
    if (inputRef.current) inputRef.current.value = ''
  }

  async function handleAnalyze() {
    if (!fileRef.current) return
    setLoading(true)
    setResult(null)
    setImgError(false)
    try {
      const formData = new FormData()
      formData.append('file', fileRef.current)
      const res = await fetch('http://127.0.0.1:8000/predict-bird-species', {
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

  // Sort probabilities descending for display
  const sortedProbs = result?.probabilities
    ? Object.entries(result.probabilities).sort((a, b) => b[1] - a[1])
    : []

  return (
    <div className={styles.page}>

      {/* ── Back ── */}
      <button className={styles.back} onClick={() => navigate('/modules')}>
        ← Back to Modules
      </button>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>🎵</div>
        <div>
          <h1 className={styles.title}>Bird Species Classification</h1>
          <p className={styles.subtitle}>
            Upload a bird audio recording and our AI will identify the species from
            its song. The model recognises 5 species using mel-spectrogram analysis.
          </p>
        </div>
      </div>

      {/* ── Supported species chips ── */}
      <div className={styles.speciesChips}>
        {SUPPORTED_SPECIES.map(s => (
          <span key={s.key} className={styles.chip}>
            {s.emoji} {s.label}
          </span>
        ))}
      </div>

      {/* ── Main layout ── */}
      <div className={styles.layout}>

        {/* ── Upload panel ── */}
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
                    <div
                      key={i}
                      className={styles.audioBar}
                      style={{ animationDelay: `${i * 0.08}s` }}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className={styles.dropzoneInner}>
                <span className={styles.dropzoneIcon}>🎵</span>
                <p className={styles.dropzoneText}>Drag & drop or click to upload</p>
                <p className={styles.dropzoneHint}>WAV, MP3, OGG, FLAC, M4A</p>
              </div>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="audio/*,.wav,.mp3,.ogg,.flac,.m4a,.aac"
            className={styles.fileInput}
            onChange={e => handleFile(e.target.files[0])}
          />

          <div className={styles.actions}>
            {fileName && (
              <button className={styles.btnSecondary} onClick={clearFile}>
                Clear
              </button>
            )}
            <button
              className={styles.btnPrimary}
              onClick={handleAnalyze}
              disabled={!fileName || loading}
            >
              {loading
                ? <><span className={styles.spinnerInline} /> Classifying…</>
                : '🎵 Identify Species'
              }
            </button>
          </div>

          {/* How it works */}
          <div className={styles.howItWorks}>
            <p className={styles.howTitle}>How it works</p>
            <div className={styles.howSteps}>
              <div className={styles.howStep}>
                <span className={styles.howNum}>1</span>
                <span className={styles.howLabel}>Audio loaded</span>
              </div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}>
                <span className={styles.howNum}>2</span>
                <span className={styles.howLabel}>Mel-spectrogram</span>
              </div>
              <div className={styles.howArrow}>→</div>
              <div className={styles.howStep}>
                <span className={styles.howNum}>3</span>
                <span className={styles.howLabel}>CNN classifier</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── Result panel ── */}
        <div className={styles.panel}>
          <p className={styles.panelTitle}>Result</p>

          {/* Empty state */}
          {!result && !loading && (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>🐦</span>
              <p className={styles.emptyText}>Species identification will appear here</p>
              <p className={styles.emptyHint}>Upload an audio file and click Identify Species</p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              <p className={styles.emptyText}>Analyzing audio…</p>
              <p className={styles.emptyHint}>Computing mel-spectrogram and running classifier</p>
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

              {/* Bird image + name hero */}
              <div className={styles.birdHero}>
                <div className={styles.birdImageWrap}>
                  {!imgError ? (
                    <img
                      src={SPECIES_IMAGES[result.species] ?? result.image_url}
                      alt={result.display_name}
                      className={styles.birdImage}
                      onError={() => setImgError(true)}
                    />
                  ) : (
                    <div className={styles.birdImageFallback}>
                      <span>🐦</span>
                    </div>
                  )}
                  <div className={styles.birdImageOverlay}>
                    <span className={styles.birdImageLabel}>{result.display_name}</span>
                  </div>
                </div>

                <div className={styles.birdMeta}>
                  <div className={styles.birdNameRow}>
                    <span className={styles.birdEmoji}>{result.emoji}</span>
                    <div>
                      <p className={styles.birdName}>{result.display_name}</p>
                      <p className={styles.birdSpeciesKey}>{result.species.replace(/_/g, ' ')}</p>
                    </div>
                  </div>

                  {/* Confidence pill */}
                  <div className={styles.confPill}>
                    <span className={styles.confPillLabel}>Confidence</span>
                    <span className={styles.confPillValue}>
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  {/* Confidence bar */}
                  <div className={styles.confBarTrack}>
                    <div
                      className={styles.confBarFill}
                      style={{ width: `${(result.confidence * 100).toFixed(1)}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📖</span>
                  <span className={styles.infoBlockTitle}>About this species</span>
                </div>
                <p className={styles.infoBlockText}>{result.description}</p>
              </div>

              {/* Habitat & Range */}
              <div className={styles.detailsGrid}>
                <div className={styles.detailCard}>
                  <span className={styles.detailIcon}>🌿</span>
                  <div>
                    <p className={styles.detailLabel}>Habitat</p>
                    <p className={styles.detailValue}>{result.habitat}</p>
                  </div>
                </div>
                <div className={styles.detailCard}>
                  <span className={styles.detailIcon}>🌍</span>
                  <div>
                    <p className={styles.detailLabel}>Range</p>
                    <p className={styles.detailValue}>{result.range}</p>
                  </div>
                </div>
              </div>

              {/* Fun fact */}
              <div className={styles.funFactBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>💡</span>
                  <span className={styles.infoBlockTitle}>Fun Fact</span>
                </div>
                <p className={styles.infoBlockText}>{result.fun_fact}</p>
              </div>

              {/* All species probabilities */}
              <div className={styles.infoBlock}>
                <div className={styles.infoBlockHeader}>
                  <span className={styles.infoBlockIcon}>📊</span>
                  <span className={styles.infoBlockTitle}>All Species Scores</span>
                </div>
                <div className={styles.probBars}>
                  {sortedProbs.map(([species, prob]) => (
                    <div key={species} className={styles.probBarRow}>
                      <span className={styles.probBarLabel}>
                        {species.replace(/_/g, ' ')}
                      </span>
                      <div className={styles.probBarTrack}>
                        <div
                          className={styles.probBarFill}
                          style={{
                            width: `${(prob * 100).toFixed(1)}%`,
                            background:
                              species === result.species
                                ? 'var(--primary)'
                                : 'var(--primary-mid)',
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
