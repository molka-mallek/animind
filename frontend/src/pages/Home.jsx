import { useNavigate } from 'react-router-dom'
import styles from './Home.module.css'

const steps = [
  { num: '01', icon: '📸', title: 'Upload a photo or video', desc: 'Take a quick photo or short video of your animal — no special equipment needed.' },
  { num: '02', icon: '🔍', title: 'We read the behavior', desc: 'AniMind looks at body language, facial cues, and movement to understand what your animal is experiencing.' },
  { num: '03', icon: '💡', title: 'Get clear advice', desc: 'Receive a simple, plain-language summary of your animal\'s state and what you can do about it.' },
]

const petFeatures = [
  { icon: '😊', text: 'Know if your dog is happy, stressed, or anxious' },
  { icon: '🩺', text: 'Spot skin issues or injuries before they worsen' },
  { icon: '❤️', text: 'Strengthen your bond through better understanding' },
  { icon: '🚨', text: 'Get alerts when something seems off' },
]

const farmerFeatures = [
  { icon: '📊', text: 'Track herd behavior patterns over time' },
  { icon: '⚡', text: 'Catch unusual activity early' },
  { icon: '🐄', text: 'Monitor multiple animals at once' },
  { icon: '📋', text: 'Get actionable care recommendations' },
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

        <div className={styles.heroVisual}>
          <div className={styles.heroCard}>
            <div className={styles.heroCardTop}>
              <span className={styles.heroCardEmoji}>🐶</span>
              <div className={styles.heroCardBadge}>✓ Analysis complete</div>
            </div>
            <div className={styles.heroCardEmotion}>
              <span className={styles.heroCardEmotionEmoji}>😄</span>
              <div>
                <p className={styles.heroCardEmotionLabel}>Happy</p>
                <p className={styles.heroCardEmotionSub}>Your dog is relaxed and content</p>
              </div>
            </div>
            <div className={styles.heroCardBar}>
              <div className={styles.heroCardBarLabel}>
                <span>Confidence</span><span>92%</span>
              </div>
              <div className={styles.heroCardBarTrack}>
                <div className={styles.heroCardBarFill} style={{ width: '92%' }} />
              </div>
            </div>
            <div className={styles.heroCardAdvice}>
              💡 Great time for play and bonding
            </div>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>How it works</div>
        <h2 className={styles.sectionTitle}>Three simple steps</h2>
        <div className={styles.stepsGrid}>
          {steps.map((s) => (
            <div key={s.num} className={styles.stepCard}>
              <div className={styles.stepNum}>{s.num}</div>
              <span className={styles.stepIcon}>{s.icon}</span>
              <h3 className={styles.stepTitle}>{s.title}</h3>
              <p className={styles.stepDesc}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── WHO IT'S FOR ── */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>Who it's for</div>
        <h2 className={styles.sectionTitle}>Built for the people who care most</h2>
        <div className={styles.audienceGrid}>

          <div className={`${styles.audienceCard} ${styles.audiencePet}`}>
            <div className={styles.audienceHeader}>
              <span className={styles.audienceEmoji}>🐶</span>
              <div>
                <h3 className={styles.audienceTitle}>Pet Owners</h3>
                <p className={styles.audienceTagline}>Deepen your bond</p>
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
              Analyze my pet →
            </button>
          </div>

          <div className={`${styles.audienceCard} ${styles.audienceFarmer}`}>
            <div className={styles.audienceHeader}>
              <span className={styles.audienceEmoji}>🌾</span>
              <div>
                <h3 className={styles.audienceTitle}>Farmers</h3>
                <p className={styles.audienceTagline}>Protect your herd</p>
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
          <h2 className={styles.ctaTitle}>Start understanding your animal today</h2>
          <p className={styles.ctaSub}>
            It takes less than a minute. No sign-up required.
          </p>
          <button className={styles.ctaBtn} onClick={() => navigate('/modules')}>
            Try it now — it's free
          </button>
        </div>
      </section>

    </div>
  )
}
