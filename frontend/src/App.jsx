
import { useEffect, useState } from 'react'
import { ArrowDown, ArrowUpRight } from 'lucide-react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import './App.css'
import IntelligenceDesk from './components/IntelligenceDesk'
import WaterEffect from './components/WaterEffect'

gsap.registerPlugin(ScrollTrigger)

function App() {
  const [page, setPage] = useState('home')

  // Standalone pointer listener for the water ripple effect
  useEffect(() => {
    const handlePointerMove = (event) => {
      document.documentElement.style.setProperty(
        '--cursor-x',
        `${event.clientX}px`
      )

      document.documentElement.style.setProperty(
        '--cursor-y',
        `${event.clientY}px`
      )
    }

    window.addEventListener('pointermove', handlePointerMove)

    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
    }
  }, [])

  useEffect(() => {
    if (page !== 'home') return

    const ctx = gsap.context(() => {
      // HERO TEXT REVEAL
      gsap.from('.hero-copy > *', {
        y: 35,
        opacity: 0,
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out',
      })

      // HERO IMAGE REVEAL
      gsap.from('.hero-image', {
        scale: 1.08,
        opacity: 0,
        duration: 1.5,
        ease: 'power3.out',
      })

      // GENERAL SECTION REVEALS
      gsap.utils.toArray('.reveal').forEach((element) => {
        gsap.from(element, {
          y: 55,
          opacity: 0,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: element,
            start: 'top 85%',
            once: true,
          },
        })
      })

      // HERO IMAGE PARALLAX
      gsap.to('.hero-image img', {
        yPercent: 12,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        },
      })

      // PINNED STORYTELLING
      const storyTimeline = gsap.timeline({
        scrollTrigger: {
          trigger: '.statement-section',
          start: 'top top',
          end: '+=120%',
          pin: true,
          scrub: 1,
          anticipatePin: 1,
        },
      })

      storyTimeline
        .fromTo(
          '.statement-image img',
          { scale: 1 },
          { scale: 1.2, ease: 'none' },
          0
        )
        .fromTo(
          '.statement-content',
          { x: 70, opacity: 0 },
          { x: 0, opacity: 1, ease: 'none' },
          0.15
        )

      // PLATFORM PILLARS — SEQUENTIAL REVEAL
      gsap.from('.platform-card', {
        y: 65,
        opacity: 0,
        duration: 0.9,
        stagger: 0.2,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.platform-grid',
          start: 'top 78%',
          once: true,
        },
      })
    }) // CLOSE gsap.context()

    return () => ctx.revert()
  }, [page])

  if (page === 'desk') {
    return <IntelligenceDesk onBack={() => setPage('home')} />
  }

  return (
    <main className="editorial-site">
      <WaterEffect />
      
      <nav className="navbar">
        <a href="#" className="brand">
          FLOODSENSE<span>®</span>
        </a>

        <div className="nav-links">
          <a href="#mission">Our mission</a>
          <a href="#approach">Our approach</a>
          <a href="#platform">Platform</a>
        </div>

        <button
          type="button"
          className="nav-cta"
          onClick={() => setPage('desk')}
        >
          Explore platform <ArrowUpRight size={15} />
        </button>
      </nav>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">INTELLIGENCE FOR A SAFER TOMORROW</p>

          <h1>
            When disaster
            <br />
            speaks, <em>we listen.</em>
          </h1>

          <p className="hero-description">
            Every emergency message carries a story.
            Every second carries a decision.
            We turn scattered signals into meaningful action.
          </p>

          <a href="#mission" className="text-link">
            Discover our purpose <ArrowDown size={16} />
          </a>
        </div>

        <div className="hero-image">
          <img
            src="https://images.unsplash.com/photo-1547683905-f686c993aae5?auto=format&fit=crop&w=1800&q=90"
            alt="Dramatic storm clouds over a flooded landscape"
          />
          <span className="image-caption">
            READING THE SIGNALS. RESPONDING WITH PURPOSE.
          </span>
        </div>
      </section>

      <section className="intro-section" id="mission">
        <div className="intro-grid">
          <h2 className="reveal">
            In a crisis,
            <br />
            <em>clarity is everything.</em>
          </h2>

          <div className="intro-copy reveal">
            <p>
              During a flood, thousands of messages can emerge from
              the same moment of uncertainty. Calls for help, reports
              of rising water, requests for rescue.
            </p>
            <p>
              But not every message reaches the right people at
              the right time. The challenge is finding the signals
              that matter most.
            </p>
          </div>
        </div>
      </section>

      <section className="statement-section" id="approach">
        <div className="statement-image">
          <img
            src="https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1800&q=90"
            alt="Powerful ocean waves"
          />
        </div>

        <div className="statement-content">
          <h2>
            From noise
            <br />
            to <em>knowledge.</em>
          </h2>
          <p>
            FloodSense uses intelligent message analysis to help
            identify emergencies, understand severity, and bring
            urgent information into focus.
          </p>
        </div>
      </section>

      <section className="platform-section" id="platform">
        <h2>
          Turning information
          <br />
          into <em>action.</em>
        </h2>

        <div className="platform-grid">
          <article className="platform-card">
            <span>01</span>
            <h3>Understand</h3>
            <p>Identify messages related to flood emergencies.</p>
          </article>

          <article className="platform-card">
            <span>02</span>
            <h3>Prioritise</h3>
            <p>Bring urgent reports and high-priority needs forward.</p>
          </article>

          <article className="platform-card">
            <span>03</span>
            <h3>Interpret</h3>
            <p>Extract meaningful signals from incoming information.</p>
          </article>
        </div>

        <div className="desk-invitation">
          <div className="invitation-content">
            <h2>
              Every signal
              <br />
              deserves to be <em>heard.</em>
            </h2>

            <p>
              Explore how FloodSense interprets emergency messages
              and brings critical information into focus.
            </p>

            <button
              type="button"
              className="invitation-button"
              onClick={() => setPage('desk')}
            >
              Enter the Intelligence Desk
              <ArrowUpRight size={18} />
            </button>
          </div>

          <div className="invitation-caption">
            A CLEARER PICTURE BEGINS HERE.
          </div>
        </div>

        <div className="platform-footer reveal">
          <p>Technology with a human purpose.</p>
          <span>FLOODSENSE © 2026</span>
        </div>
      </section>
    </main>
  )
}

export default App

