import { useNavigate } from 'react-router-dom'
import styles from './Home.module.css'

const petFeatures = [
  { icon: '🐶', text: 'Dog emotion analysis (photo/video)' },
  { icon: '🐱', text: 'Cat behavior classification' },
  { icon: '🐴', text: 'Horse pain detection (video)' },
  { icon: '🐦', text: 'Bird health monitoring' },
]

const farmerFeatures = [
  { icon: '🐄', text: 'Real-time calf behavior monitoring' },
  { icon: '📊', text: 'Track herd patterns over time' },
  { icon: '⚡', text: 'Early detection of unusual activity' },
  { icon: '🩺', text: 'Health alerts and recommendations' },
]

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>

      {/* ── HERO ── */}
      <section className={styles.hero}>
        <div className={styles.heroInner}>
          <span className={styles.heroBadge}>🐾 For pet owners & farmers</span>
          <h1 className={styles.heroTitle}>
            Understand your animal<br />
            <span className={styles.heroAccent}>like never before</span>
          </h1>
          <p className={styles.heroSub}>
            Upload a photo or video and get clear, simple insights about
            how your animal feels — no expertise needed.
          </p>
          <div className={styles.heroActions}>
            <button className={styles.btnPrimary} onClick={() => navigate('/modules')}>
              Start Analysis
            </button>
            <button className={styles.btnGhost} onClick={() => navigate('/dashboard')}>
              See how it works ↓
            </button>
          </div>

          <div className={styles.heroStats}>
            <div className={styles.heroStat}>
              <span className={styles.heroStatNum}>7</span>
              <span className={styles.heroStatLabel}>Behavior checks</span>
            </div>
            <div className={styles.heroStatDivider} />
            <div className={styles.heroStat}>
              <span className={styles.heroStatNum}>4+</span>
              <span className={styles.heroStatLabel}>Animal types</span>
            </div>
            <div className={styles.heroStatDivider} />
            <div className={styles.heroStat}>
              <span className={styles.heroStatNum}>Fast</span>
              <span className={styles.heroStatLabel}>Results in seconds</span>
            </div>
          </div>
        </div>


      </section>

      {/* ── WHO IT'S FOR ── */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>Who it's for</div>
        <h2 className={styles.sectionTitle}>Built for the people who care most</h2>
        <div className={styles.audienceGrid}>

          <div className={`${styles.audienceCard} ${styles.audiencePet}`}>
            <div className={styles.audienceHeader}>
              <span className={styles.audienceEmoji}>🐾</span>
              <div>
                <h3 className={styles.audienceTitle}>Pet Owners</h3>
                <p className={styles.audienceTagline}>Understand your animals</p>
              </div>
            </div>
            <ul className={styles.featureList}>
              {petFeatures.map((f) => (
                <li key={f.text} className={styles.featureItem}>
                  <span className={styles.featureIcon}>{f.icon}</span>
                  <span>{f.text}</span>
                </li>
              ))}
            </ul>
            <button className={styles.audienceBtn} onClick={() => navigate('/modules')}>
              Analyze my animal →
            </button>
          </div>

          <div className={`${styles.audienceCard} ${styles.audienceFarmer}`}>
            <div className={styles.audienceHeader}>
              <span className={styles.audienceEmoji}>🌾</span>
              <div>
                <h3 className={styles.audienceTitle}>Farmers</h3>
                <p className={styles.audienceTagline}>Monitor your livestock</p>
              </div>
            </div>
            <ul className={styles.featureList}>
              {farmerFeatures.map((f) => (
                <li key={f.text} className={styles.featureItem}>
                  <span className={styles.featureIcon}>{f.icon}</span>
                  <span>{f.text}</span>
                </li>
              ))}
            </ul>
            <button className={styles.audienceBtn} onClick={() => navigate('/modules')}>
              Monitor my livestock →
            </button>
          </div>

        </div>
      </section>

      {/* ── FEATURES ── */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>What you get</div>
        <h2 className={styles.sectionTitle}>Everything you need to know</h2>
        <div className={styles.featuresGrid}>
          {[
            { icon: '👁️', title: 'Visual cues explained', desc: 'We break down exactly what your animal\'s body language means in plain language.' },
            { icon: '💬', title: 'Clear recommendations', desc: 'Every analysis ends with a simple action you can take right now.' },
            { icon: '📸', title: 'Photos and videos', desc: 'Works with a quick snapshot or a short video clip — whatever you have.' },
            { icon: '⚡', title: 'Results in seconds', desc: 'No waiting. Upload and get your insights almost instantly.' },
          ].map((f) => (
            <div key={f.title} className={styles.featureCard}>
              <span className={styles.featureCardIcon}>{f.icon}</span>
              <h3 className={styles.featureCardTitle}>{f.title}</h3>
              <p className={styles.featureCardDesc}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── FINAL CTA ── */}
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
