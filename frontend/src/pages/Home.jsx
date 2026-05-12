import { useNavigate } from 'react-router-dom'
import styles from './Home.module.css'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>

      {/* ── HERO ── */}
      <section className={styles.hero}>
        <div className={styles.heroInner}>
          <span className={styles.heroBadge}>🎓 Esprit School of Engineering Project</span>
          <h1 className={styles.heroTitle}>
            Understand your animal<br />
            <span className={styles.heroAccent}>like never before</span>
          </h1>
          <p className={styles.heroSub}>
            Upload a photo or audio and get instant AI-powered insights about your pet or livestock's health, emotions, and behavior.
          </p>
          <button className={styles.btnPrimary} onClick={() => navigate('/modules')}>
            Analyze my animal →
          </button>
        </div>
      </section>

      {/* ── AUDIENCE ── */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>Built for the people who care most</div>
        <div className={styles.audienceGrid}>

          {/* Pet Owners */}
          <div className={`${styles.audienceCard} ${styles.audiencePet}`}>
            <div className={styles.audienceHeader}>
              <span className={styles.audienceEmoji}>🐶</span>
              <div>
                <p className={styles.audienceTitle}>Pet Owners</p>
                <p className={styles.audienceTagline}>Deepen your bond</p>
              </div>
            </div>
            <ul className={styles.featureList}>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>😊</span>
                Know if your pet is happy, stressed, or anxious
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>🩺</span>
                Spot skin issues or injuries before they worsen
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>❤️</span>
                Strengthen your bond through better understanding
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>🚨</span>
                Get alerts when something seems off
              </li>
            </ul>
            <button className={styles.audienceBtn} onClick={() => navigate('/modules')}>
              Analyze my pet →
            </button>
          </div>

          {/* Farmers */}
          <div className={`${styles.audienceCard} ${styles.audienceFarmer}`}>
            <div className={styles.audienceHeader}>
              <span className={styles.audienceEmoji}>🌾</span>
              <div>
                <p className={styles.audienceTitle}>Farmers</p>
                <p className={styles.audienceTagline}>Protect your herd</p>
              </div>
            </div>
            <ul className={styles.featureList}>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>📊</span>
                Track herd behavior patterns over time
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>⚡</span>
                Catch unusual activity early
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>🐄</span>
                Monitor multiple animals at once
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>📋</span>
                Get actionable care recommendations
              </li>
            </ul>
            <button className={styles.audienceBtn} onClick={() => navigate('/modules')}>
              Monitor my livestock →
            </button>
          </div>

        </div>
      </section>

      {/* ── FEATURES ── */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>What we can detect</div>
        <h2 className={styles.sectionTitle}>Powered by specialized AI models</h2>
        <div className={styles.featuresGrid}>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>😊</span>
            <p className={styles.featureCardTitle}>Emotions & Mood</p>
            <p className={styles.featureCardDesc}>
              Detect happiness, sadness, fear, and stress in dogs and cats
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>🩺</span>
            <p className={styles.featureCardTitle}>Skin Conditions</p>
            <p className={styles.featureCardDesc}>
              Identify rashes, infections, and abnormalities
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>👁️</span>
            <p className={styles.featureCardTitle}>Eye Infections</p>
            <p className={styles.featureCardDesc}>
              Screen for conjunctivitis and other eye issues
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>🐔</span>
            <p className={styles.featureCardTitle}>Poultry Health</p>
            <p className={styles.featureCardDesc}>
              Detect fowlpox and analyze bird droppings
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>🐄</span>
            <p className={styles.featureCardTitle}>Livestock Behavior</p>
            <p className={styles.featureCardDesc}>
              Real-time calf monitoring with health alerts
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>🐟</span>
            <p className={styles.featureCardTitle}>Fish Freshness</p>
            <p className={styles.featureCardDesc}>
              Get instant quality grades and freshness scores
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>🐴</span>
            <p className={styles.featureCardTitle}>Horse Pain</p>
            <p className={styles.featureCardDesc}>
              Identify pain indicators through behavior analysis
            </p>
          </div>
          <div className={styles.featureCard}>
            <span className={styles.featureCardIcon}>🎵</span>
            <p className={styles.featureCardTitle}>Bird Species</p>
            <p className={styles.featureCardDesc}>
              Identify bird species from audio recordings
            </p>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className={styles.ctaSection}>
        <div className={styles.ctaInner}>
          <span className={styles.ctaEmoji}>🐾</span>
          <h2 className={styles.ctaTitle}>Start analyzing your animals today</h2>
          <p className={styles.ctaSub}>
            Get instant insights in seconds. No sign-up required.
          </p>
          <button className={styles.ctaBtn} onClick={() => navigate('/modules')}>
            Try it now
          </button>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className={styles.footer}>
        <div className={styles.footerInner}>

          {/* Brand column */}
          <div className={styles.footerBrand}>
            <img src="/cortexa.png" alt="Cortexa" className={styles.footerLogo} />
            <p className={styles.footerTagline}>
              AI-powered animal health insights for pet owners and farmers.
            </p>
            <div className={styles.footerBadge}>
              <span>🎓</span>
              <span>École Supérieure Privée d'Ingénierie et de Technologie — Esprit</span>
            </div>
          </div>

          {/* Contact column */}
          <div className={styles.footerCol}>
            <p className={styles.footerColTitle}>Contact</p>
            <ul className={styles.footerLinks}>
              <li>
                <a href="mailto:Cortexa@gmail.com" className={styles.footerLink}>
                  <span className={styles.footerLinkIcon}>✉️</span>
                  Cortexa@gmail.com
                </a>
              </li>
              <li>
                <a href="tel:+21612345678" className={styles.footerLink}>
                  <span className={styles.footerLinkIcon}>📞</span>
                  +216 12 345 678
                </a>
              </li>
            </ul>
          </div>

          {/* Resources column */}
          <div className={styles.footerCol}>
            <p className={styles.footerColTitle}>Resources</p>
            <ul className={styles.footerLinks}>
              <li>
                <a
                  href="https://ilefbennour10.wixsite.com/my-site-1/about-4"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.footerLink}
                >
                  <span className={styles.footerLinkIcon}>📝</span>
                  Project Blog
                </a>
              </li>
              <li>
                <a href="/modules" className={styles.footerLink}>
                  <span className={styles.footerLinkIcon}>🔬</span>
                  Start Analysis
                </a>
              </li>
            </ul>
          </div>

        </div>

        <div className={styles.footerBottom}>
          <span>© {new Date().getFullYear()} Cortexa · Esprit · All rights reserved</span>
        </div>
      </footer>

    </div>
  )
}
