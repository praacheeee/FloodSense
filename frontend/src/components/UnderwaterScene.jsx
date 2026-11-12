
import { useEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'

import * as THREE from 'three'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

function createParticles(count) {
  const positions = new Float32Array(count * 3)

  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 35
    positions[i * 3 + 1] = (Math.random() - 0.5) * 20
    positions[i * 3 + 2] = -Math.random() * 45
  }

  return positions
}

function FloatingParticles() {
  const pointsRef = useRef(null)

  const positions = useMemo(() => createParticles(1800), [])

  useFrame((state, delta) => {
    if (!pointsRef.current) return

    pointsRef.current.rotation.y += delta * 0.006
    pointsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.08) * 0.025
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#a9eaff"
        size={0.035}
        transparent
        opacity={0.55}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  )
}

function BubbleField() {
  const groupRef = useRef(null)

  const bubbles = useMemo(() => {
    return Array.from({ length: 65 }, (_, i) => ({
      x: Math.sin(i * 12.37) * 12,
      y: -8 + ((i * 7) % 16),
      z: -2 - ((i * 13) % 38),
      size: 0.035 + (i % 5) * 0.018,
      speed: 0.12 + (i % 7) * 0.035,
      phase: i * 0.7,
    }))
  }, [])

  useFrame((state, delta) => {
    if (!groupRef.current) return

    groupRef.current.children.forEach((bubble, i) => {
      const data = bubbles[i]

      bubble.position.y += delta * data.speed

      if (bubble.position.y > 9) {
        bubble.position.y = -9
      }

      bubble.position.x =
        data.x + Math.sin(state.clock.elapsedTime * 0.35 + data.phase) * 0.16
    })
  })

  return (
    <group ref={groupRef}>
      {bubbles.map((bubble, i) => (
        <mesh
          key={i}
          position={[bubble.x, bubble.y, bubble.z]}
          scale={bubble.size}
        >
          <sphereGeometry args={[1, 12, 12]} />
          <meshPhysicalMaterial
            color="#b9eaff"
            roughness={0.08}
            metalness={0.05}
            transmission={0.65}
            thickness={0.5}
            transparent
            opacity={0.65}
          />
        </mesh>
      ))}
    </group>
  )
}

function LightRays() {
  return (
    <group position={[0, 8, -15]}>
      {[...Array(5)].map((_, i) => (
        <mesh
          key={i}
          position={[(i - 2) * 3.5, -2, -i * 2]}
          rotation={[0, 0, (i - 2) * 0.08]}
        >
          <coneGeometry args={[1.2, 18, 24, 1, true]} />
          <meshBasicMaterial
            color="#55bde8"
            transparent
            opacity={0.035}
            side={THREE.DoubleSide}
            depthWrite={false}
          />
        </mesh>
      ))}
    </group>
  )
}

function CameraJourney({ progressRef }) {
  const { camera } = useThree()
  const target = useRef(new THREE.Vector3())

  useFrame((state, delta) => {
    const progress = progressRef.current

    const desiredX = Math.sin(progress * Math.PI * 1.2) * 0.9
    const desiredY = -progress * 2.2 + Math.sin(progress * Math.PI * 2) * 0.25
    const desiredZ = -progress * 11

    target.current.set(desiredX, desiredY, desiredZ)

    camera.position.lerp(
      target.current,
      1 - Math.exp(-delta * 2.2)
    )

    camera.rotation.x = THREE.MathUtils.damp(
      camera.rotation.x,
      Math.sin(progress * Math.PI) * 0.035,
      2,
      delta
    )

    camera.rotation.y = THREE.MathUtils.damp(
      camera.rotation.y,
      Math.sin(progress * Math.PI * 1.5) * 0.055,
      2,
      delta
    )

    camera.rotation.z = THREE.MathUtils.damp(
      camera.rotation.z,
      Math.sin(progress * Math.PI * 2) * 0.018,
      2,
      delta
    )
  })

  return null
}

function SceneContent({ progressRef }) {
  return (
    <>
      <color attach="background" args={['#031321']} />
      <fog attach="fog" args={['#031321', 8, 38]} />

      <ambientLight intensity={0.65} color="#8bbbd4" />
      <directionalLight
        position={[0, 9, -10]}
        intensity={1.1}
        color="#9bdfff"
      />
      <pointLight
        position={[4, 2, -8]}
        intensity={1.3}
        color="#167ba8"
        distance={25}
      />
      <pointLight
        position={[-7, -3, -18]}
        intensity={0.8}
        color="#15577d"
        distance={30}
      />

      <LightRays />
      <FloatingParticles />
      <BubbleField />
      <CameraJourney progressRef={progressRef} />
      {/* <Environment preset="night" /> */}
    </>
  )
}

export default function UnderwaterScene() {
  const progressRef = useRef(0)

  useEffect(() => {
    const trigger = ScrollTrigger.create({
      trigger: '.ocean-world',
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1.5,
      onUpdate: (self) => {
        progressRef.current = self.progress
      },
    })

    return () => {
      trigger.kill()
    }
  }, [])

  return (
    <div className="underwater-canvas" aria-hidden="true">
      <Canvas
        camera={{
          position: [0, 0, 5],
          fov: 65,
          near: 0.1,
          far: 100,
        }}
        dpr={[1, 1.5]}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
        }}
      >
        <SceneContent progressRef={progressRef} />
      </Canvas>
    </div>
  )
}
