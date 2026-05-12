import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { modules, CATEGORIES } from '../data/modules'
import styles from './Dashboard.module.css'

const availableModules = modules.filter(m => m.route || m.external)

const stats = [
  { icon: '🔍', value: String(availableModules.length), label: 'Checks available' },
  { icon: '🐾', value: '4+',   label: 'Animal types supported' },
  { icon: '⚡', value: 'Fast', label: 'Results in seconds' },
  { icon: '🚀', value: 'Beta', label: 'New checks coming soon' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const [activeCategory, setActiveCategory] = useState('all')

  const filtered = activeCategory === 'all'
    ? availableModules
    : availableModules.filter(m => m.category === activeCategory)

  return (
    <div className={styles.page}>

      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <img src="/animind-logo.jpg" alt="AniMind" className={styles.headerLogo} />
          <div>
            <h1 className={styles.title}>Welcome back 👋</h1>
            <p className={styles.subtitle}>What would you like to check on today?</p>
          </div>
        </div>
        <button className={styles.ctaBtn} onClick={() => navigate('/modules')}>
          + Start a new analysis
        </button>
      </div>

      {/* ── Stats ── */}
      <div className={styles.statsGrid}>
        {stats.map((s) => (
          <div key={s.label} className={styles.statCard}>
            <span className={styles.statIcon}>{s.icon}</span>
            <div>
              <p className={styles.statValue}>{s.value}</p>
              <p className={styles.statLabel}>{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Quick access ── */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>What do you want to check?</h2>
          <button className={styles.viewAll} onClick={() => navigate('/modules')}>
            See all →
          </button>
        </div>

        {/* Category filter */}
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

        <div className={styles.grid}>
          {filtered.map((mod) => (
            <div
              key={mod.id}
              className={styles.card}
              onClick={() => {
                if (mod.route)         navigate(mod.route)
                else if (mod.external) window.open(mod.external, '_blank')
              }}
            >
              <span className={styles.cardIcon}>{mod.icon}</span>
              <div className={styles.cardBody}>
                <p className={styles.cardTitle}>{mod.title}</p>
                <p className={styles.cardDesc}>{mod.description}</p>
              </div>
              <div className={styles.cardArrow}>
                {mod.route ? '→' : mod.external ? <span className={styles.ext}>↗</span> : null}
              </div>
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className={styles.empty}>
            <span>🔍</span>
            <p>No checks in this category yet.</p>
          </div>
        )}
      </div>

    </div>
  )
}
