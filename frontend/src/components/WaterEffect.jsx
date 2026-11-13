
import { useEffect, useRef } from 'react'

function WaterEffect() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    let width = 0
    let height = 0
    let frame = 0
    let time = 0

    const trail = []
    let previous = null

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)

      width = window.innerWidth
      height = window.innerHeight

      canvas.width = width * dpr
      canvas.height = height * dpr

      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }

    const handlePointerMove = (event) => {
      const x = event.clientX
      const y = event.clientY

      if (!previous) {
        previous = { x, y }
        return
      }

      const dx = x - previous.x
      const dy = y - previous.y
      const distance = Math.hypot(dx, dy)

      if (distance > 2) {
        const steps = Math.ceil(distance / 5)

        for (let i = 1; i <= steps; i++) {
          const progress = i / steps

          const pointX = previous.x + dx * progress
          const pointY = previous.y + dy * progress

          trail.push({
            x: pointX,
            y: pointY,
            angle: Math.atan2(dy, dx),
            life: 1,
            seed: Math.random() * Math.PI * 2,
          })
        }
      }

      previous = { x, y }

      // Prevent an excessively large trail
      if (trail.length > 500) {
        trail.splice(0, trail.length - 500)
      }
    }

    const drawRibbon = (offset, phase, thickness, strength) => {
      if (trail.length < 3) return

      ctx.beginPath()

      let first = true

      for (let i = 0; i < trail.length; i++) {
        const point = trail[i]

        const wave =
          Math.sin(time * 1.4 + point.seed + phase) * 5 +
          Math.sin(time * 0.8 + i * 0.035 + phase) * 3

        const perpendicular = point.angle + Math.PI / 2

        const x =
          point.x + Math.cos(perpendicular) * (offset + wave)

        const y =
          point.y + Math.sin(perpendicular) * (offset + wave)

        if (first) {
          ctx.moveTo(x, y)
          first = false
        } else {
          const previousPoint = trail[i - 1]

          const previousWave =
            Math.sin(time * 1.4 + previousPoint.seed + phase) * 5

          const previousX =
            previousPoint.x +
            Math.cos(previousPoint.angle + Math.PI / 2) *
              (offset + previousWave)

          const previousY =
            previousPoint.y +
            Math.sin(previousPoint.angle + Math.PI / 2) *
              (offset + previousWave)

          const middleX = (previousX + x) / 2
          const middleY = (previousY + y) / 2

          ctx.quadraticCurveTo(previousX, previousY, middleX, middleY)
        }
      }

      const last = trail[trail.length - 1]
      ctx.lineTo(last.x, last.y)

      const averageLife =
        trail.reduce((sum, point) => sum + point.life, 0) /
        trail.length

      ctx.save()
      ctx.globalAlpha = averageLife * strength
      ctx.strokeStyle = '#83b6c6'
      ctx.lineWidth = thickness
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.shadowColor = 'rgba(104, 169, 190, 0.35)'
      ctx.shadowBlur = 20
      ctx.stroke()
      ctx.restore()
    }

    const animate = () => {
      time += 0.018

      ctx.clearRect(0, 0, width, height)

      // Three irregular, flowing ribbons form the water wake
      drawRibbon(-12, 0, 25, 0.035)
      drawRibbon(0, 2, 19, 0.045)
      drawRibbon(13, 4, 11, 0.035)

      // A finer blue highlight along the moving trail
      drawRibbon(3, 1, 2, 0.12)

      // Dissolve the trail gradually
      for (let i = trail.length - 1; i >= 0; i--) {
        trail[i].life -= 0.0035

        if (trail[i].life <= 0) {
          trail.splice(i, 1)
        }
      }

      frame = requestAnimationFrame(animate)
    }

    resize()
    animate()

    window.addEventListener('resize', resize)
    window.addEventListener('pointermove', handlePointerMove)

    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('resize', resize)
      window.removeEventListener('pointermove', handlePointerMove)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="water-effect"
      aria-hidden="true"
    />
  )
}

export default WaterEffect
