
import { useEffect, useRef, useState, useLayoutEffect } from 'react'
import { ArrowDown, ArrowUpRight, VolumeX } from 'lucide-react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import './App.css'

gsap.registerPlugin(ScrollTrigger)

function App() {
  useLayoutEffect(() => {
  const ctx = gsap.context(() => {

    // Hero moves upward as the visitor leaves it
    gsap.to('.hero-content', {
      y: -110,
      opacity: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero-section',
        start: 'top top',
        end: 'bottom top',
        scrub: 1,
      },
    })

    // Each section reveals itself while scrolling
    gsap.utils.toArray('.reveal-up').forEach((element) => {
      gsap.fromTo(
        element,
        {
          y: 65,
          opacity: 0,
        },
        {
          y: 0,
          opacity: 1,
          ease: 'none',
          scrollTrigger: {
            trigger: element,
            start: 'top 88%',
            end: 'top 48%',
            scrub: 1,
          },
        }
      )
    })

  })

  return () => ctx.revert()
}, [])
  const videoRef = useRef(null)
  const [introComplete, setIntroComplete] = useState(false)
  const [showTitle, setShowTitle] = useState(false)
  const [videoFailed, setVideoFailed] = useState(false)

  const finishIntro = () => {
    if (videoRef.current) {
      videoRef.current.pause()
    }
    setIntroComplete(true)
    setShowTitle(true)
  }

  const handleTimeUpdate = () => {
    const video = videoRef.current
    if (!video || !video.duration) return

    if (video.currentTime >= video.duration - 2.8) {
      setShowTitle(true)
    }
  }

  useEffect(() => {
    document.body.classList.toggle('intro-active', !introComplete)

    return () => {
      document.body.classList.remove('intro-active')
    }
  }, [introComplete])

  return (
    <main className="floodsense">
      <section className={`intro ${introComplete ? 'intro-finished' : ''}`}>
        {!videoFailed && (
          <video
            ref={videoRef}
            className="ocean-video"
            autoPlay
            muted
            playsInline
            preload="auto"
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIntroComplete(true)}
            onError={() => setVideoFailed(true)}
          >
            <source src="/videos/ocean-intro.mp4" type="video/mp4" />
          </video>
        )}

        <div className="intro-shade" />

        <div className={`intro-brand ${showTitle ? 'brand-visible' : ''}`}>
          <span className="brand-eyebrow">INTELLIGENCE FOR HUMANITY</span>
          <h1>FLOOD<span>SENSE</span></h1>
          <p>Analyzing for a safer tomorrow.</p>
        </div>

        {!introComplete && (
          <button className="skip-button" onClick={finishIntro}>
            Skip introduction <ArrowUpRight size={15} />
          </button>
        )}

        <div className="sound-indicator">
          <VolumeX size={14} />
          <span>SOUND MUTED</span>
        </div>
      </section>

      <section className="ocean-world">
        <div className="underwater-atmosphere" />

        <nav className="navbar">
          <a className="nav-brand" href="#home">
            FLOOD<span>SENSE</span>
          </a>

          <div className="nav-links">
            <a href="#mission">Our mission</a>
            <a href="#platform">Platform</a>
          </div>

          <a className="nav-action" href="#platform">
            Explore platform <ArrowUpRight size={15} />
          </a>
        </nav>

        <section className="hero-section" id="home">
          <div className="hero-content">
            <span className="hero-label">
              <span className="status-dot" />
              INTELLIGENCE BELOW THE SURFACE
            </span>

            <h2>
              Every message
              <br />
              <span>could save a life.</span>
            </h2>

            <p className="hero-description">
              Turning emergency messages into actionable intelligence.
              Because when floods strike, every second matters.
            </p>

            <a className="hero-button" href="#platform">
              Discover FloodSense <ArrowUpRight size={17} />
            </a>
          </div>

          <div className="scroll-indicator">
            <ArrowDown size={16} />
            <span>SCROLL TO EXPLORE</span>
          </div>

          <div className="hero-coordinate">
            <span>FLOODSENSE / 001</span>
            <span>BUILT FOR THE UNSEEN</span>
          </div>
        </section>

        <section className="mission-section reveal-up" id="mission">
          <span className="section-kicker">01 / THE PURPOSE</span>
          <h2>
            When water rises,
            <br />
            <span>information matters.</span>
          </h2>
          <p>
            FloodSense is designed to interpret flood-related emergency
            messages and help identify the situations that need attention.
          </p>
        </section>

        <section className="platform-section reveal-up" id="platform">
          <span className="section-kicker">02 / THE PLATFORM</span>
          <h2>From messages to meaning.</h2>
          <p>
            Our emergency message intelligence platform is the next part
            of this experience.
          </p>
          <div className="platform-preview">
            <span className="status-dot" />
            <span>ANALYSIS INTERFACE — IN DEVELOPMENT</span>
          </div>
        </section>

        <footer className="footer">
          <a className="nav-brand" href="#home">
            FLOOD<span>SENSE</span>
          </a>
          <span>ANALYZING FOR A SAFER TOMORROW.</span>
          <span>© 2026 FLOODSENSE</span>
        </footer>
      </section>
    </main>
  )
}


export default App
