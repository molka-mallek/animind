import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { modules, CATEGORIES } from '../data/modules'
import styles from './Modules.module.css'

export default function Modules() {
  const navigate = useNavigate()
  const [activeCategory, setActiveCategory] = useState('all')

  const filtered = activeCategory === 'all'
    ? modules
    : modules.filter(m => m.category === activeCategory)

  const availableCount = modules.filter(m => m.tag === 'Available').length

  return (
    <div className={styles.page}>

      <div className={styles.header}>
        <span className={styles.headerLabel}>Choose a check</span>
        <h1 className={styles.title}>What do you want to know about your animal?</h1>
        <p className={styles.subtitle}>
          {availableCount} checks available — pick one, upload a photo or audio, and get your answer in seconds.
        </p>
      </div>

      {/* ── Category filter pills ── */}
      <div className={styles.filterRow}>
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            className={`${styles.filterPill} ${activeCategory === cat.id ? styles.filterPillActive : ''}`}
            onClick={() => setActiveCategory(cat.id)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* ── Module grid ── */}
      <div className={styles.grid}>
        {filtered.map((mod) => {
          const isAvailable = mod.route || mod.external
          const isExternal  = !mod.route && mod.external
          return (
            <div
              key={mod.id}
              className={`${styles.card} ${!isAvailable ? styles.cardDisabled : ''}`}
            >
              <div className={styles.cardTop}>
                <span className={styles.cardIcon}>{mod.icon}</span>
                {mod.tag && (
                  <span className={`${styles.cardTag} ${mod.tag === 'Coming Soon' ? styles.cardTagSoon : ''}`}>
                    {mod.tag}
                  </span>
                )}
              </div>
              <h3 className={styles.cardTitle}>{mod.title}</h3>
              <p className={styles.cardDesc}>{mod.description}</p>
              <button
                className={
                  mod.route      ? styles.cardBtn         :
                  isExternal     ? styles.cardBtnExternal :
                                   styles.cardBtnDisabled
                }
                onClick={() => {
                  if (mod.route)    navigate(mod.route)
                  else if (mod.external) window.open(mod.external, '_blank')
                }}
                disabled={!isAvailable}
              >
                {mod.route ? 'Start →' : isExternal ? 'Open Dashboard ↗' : 'Coming soon'}
              </button>
            </div>
          )
        })}
      </div>

      {filtered.length === 0 && (
        <div className={styles.empty}>
          <span>🔍</span>
          <p>No checks in this category yet.</p>
        </div>
      )}

    </div>
  )
}
