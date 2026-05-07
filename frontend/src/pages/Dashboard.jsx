import { useNavigate } from 'react-router-dom'
import { modules } from '../data/modules'
import styles from './Dashboard.module.css'

const stats = [
  { icon: '🔍', value: '7', label: 'Behavior checks available' },
  { icon: '🐾', value: '4+', label: 'Animal types supported' },
  { icon: '⚡', value: 'Fast', label: 'Results in seconds' },
  { icon: '🚀', value: 'Beta', label: 'New checks coming soon' },
]

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>

      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Welcome back 👋</h1>
          <p className={styles.subtitle}>What would you like to check on today?</p>
        </div>
        <button className={styles.ctaBtn} onClick={() => navigate('/modules')}>
          + Start a new analysis
        </button>
      </div>

      {/* Stats */}
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

      {/* Quick access */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>What do you want to check?</h2>
          <button className={styles.viewAll} onClick={() => navigate('/modules')}>
            See all →
          </button>
        </div>
        <div className={styles.grid}>
          {modules.slice(0, 4).map((mod) => (
            <div
              key={mod.id}
              className={`${styles.card} ${(!mod.route && !mod.external) ? styles.cardDisabled : ''}`}
              onClick={() => {
                if (mod.route) navigate(mod.route)
                else if (mod.external) window.open(mod.external, '_blank')
              }}
            >
              <span className={styles.cardIcon}>{mod.icon}</span>
              <div className={styles.cardBody}>
                <p className={styles.cardTitle}>{mod.title}</p>
                <p className={styles.cardDesc}>{mod.description}</p>
              </div>
              <div className={styles.cardArrow}>
                {mod.route ? '→' : mod.external ? <span className={styles.ext}>↗</span> : <span className={styles.soon}>Soon</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
