import { NavLink } from 'react-router-dom'
import styles from './Navbar.module.css'

export default function Navbar({ onMenuClick }) {
  return (
    <header className={styles.navbar}>
      <button className={styles.menuBtn} onClick={onMenuClick} aria-label="Open menu">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>

      <div className={styles.brand}>
        <div className={styles.brandMark}>🐾</div>
        <span className={styles.brandName}>AniMind</span>
      </div>

      <div className={styles.actions}>
        <button className={styles.signInBtn}>Sign In</button>
        <NavLink to="/modules" className={styles.ctaBtn}>
          Start Analysis
        </NavLink>
      </div>
    </header>
  )
}
