import { useNavigate } from 'react-router-dom'
import { modules } from '../data/modules'
import styles from './Modules.module.css'

export default function Modules() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>

      <div className={styles.header}>
        <span className={styles.headerLabel}>Choose a check</span>
        <h1 className={styles.title}>What do you want to know about your animal?</h1>
        <p className={styles.subtitle}>
          Pick one of the options below. Upload a photo or video and get your answer in seconds.
        </p>
      </div>

      <div className={styles.grid}>
        {modules.map((mod) => (
          <div
            key={mod.id}
            className={`${styles.card} ${!mod.route ? styles.cardDisabled : ''}`}
          >
            <div className={styles.cardTop}>
              <span className={styles.cardIcon}>{mod.icon}</span>
              {mod.tag && <span className={styles.cardTag}>{mod.tag}</span>}
            </div>
            <h3 className={styles.cardTitle}>{mod.title}</h3>
            <p className={styles.cardDesc}>{mod.description}</p>
            <button
              className={mod.route ? styles.cardBtn : mod.external ? styles.cardBtnExternal : styles.cardBtnDisabled}
              onClick={() => {
                if (mod.route) navigate(mod.route)
                else if (mod.external) window.open(mod.external, '_blank')
              }}
              disabled={!mod.route && !mod.external}
            >
              {mod.route ? 'Start →' : mod.external ? 'Open Dashboard ↗' : 'Coming soon'}
            </button>
          </div>
        ))}
      </div>

    </div>
  )
}
