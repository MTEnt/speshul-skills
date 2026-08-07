'use client'

import { useEffect, useRef } from 'react'
import styles from './video-particle-field.module.css'

type Palette = {
  dark: string
  mid: string
  light: string
  signal: string
  warm: string
}

type Placement = { left: number; top: number; width: number; height: number }

type Props = {
  videoSrc: string
  destinationImageSrc?: string
  posterSrc?: string
  progress: number
  className?: string
  desktopParticles?: number
  mobileParticles?: number
  palette?: Partial<Palette>
  destinationPlacement?: Partial<Placement>
}

type Particle = {
  x: number
  y: number
  depth: number
  phase: number
  glyphSeed: number
  micro: boolean
}

type Visual = {
  x: number
  y: number
  color: string
  opacity: number
  size: number
}

const DEFAULT_PALETTE: Palette = {
  dark: '#26343D',
  mid: '#9AA8A3',
  light: '#F1F5F3',
  signal: '#56E6F0',
  warm: '#FFB454',
}

const GLYPHS = ['.', '·', ':', '+', '-', '|', '/', '\\']

function clamp(value: number, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value))
}

function mix(a: number, b: number, amount: number) {
  return a + (b - a) * amount
}

function smoothstep(value: number) {
  const x = clamp(value)
  return x * x * (3 - 2 * x)
}

function hash(value: number) {
  const result = Math.sin(value * 12.9898) * 43758.5453
  return result - Math.floor(result)
}

function parseHex(color: string) {
  const value = color.replace('#', '')
  return [
    Number.parseInt(value.slice(0, 2), 16),
    Number.parseInt(value.slice(2, 4), 16),
    Number.parseInt(value.slice(4, 6), 16),
  ]
}

function mixColor(from: string, to: string, amount: number) {
  const a = parseHex(from)
  const b = parseHex(to)
  const channels = a.map((channel, index) =>
    Math.round(mix(channel, b[index], amount)).toString(16).padStart(2, '0'),
  )
  return `#${channels.join('')}`
}

function quantizeColor(
  red: number,
  green: number,
  blue: number,
  luminance: number,
  palette: Palette,
) {
  if (luminance > 0.78) return palette.light
  if (blue > red + 12 || green > red + 22) return palette.signal
  if (red > blue + 22 && red >= green * 0.92) return palette.warm
  if (luminance < 0.07) return palette.dark
  return palette.mid
}

function makeParticles(count: number, aspect: number): Particle[] {
  const columns = Math.ceil(Math.sqrt(count * aspect))
  return Array.from({ length: count }, (_, index) => {
    const column = index % columns
    const row = Math.floor(index / columns)
    const rows = Math.ceil(count / columns)
    return {
      x: clamp((column + 0.5 + (hash(index * 3.37 + 5) - 0.5) * 0.34) / columns),
      y: clamp((row + 0.5 + (hash(index * 7.11 + 13) - 0.5) * 0.34) / rows),
      depth: hash(index * 6.17 + 19),
      phase: hash(index * 5.1 + 2) * Math.PI * 2,
      glyphSeed: hash(index * 3.7 + 4),
      micro: index % 6 !== 0,
    }
  })
}

export default function VideoParticleField({
  videoSrc,
  destinationImageSrc,
  posterSrc,
  progress,
  className,
  desktopParticles = 24000,
  mobileParticles = 7000,
  palette: paletteOverride,
  destinationPlacement,
}: Props) {
  const rootRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const progressRef = useRef(progress)

  useEffect(() => {
    progressRef.current = clamp(progress)
  }, [progress])

  const destinationLeft = destinationPlacement?.left ?? 0
  const destinationTop = destinationPlacement?.top ?? 0
  const destinationWidth = destinationPlacement?.width ?? 1
  const destinationHeight = destinationPlacement?.height ?? 1

  useEffect(() => {
    const root = rootRef.current
    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d')
    if (!root || !video || !canvas || !context) return

    const palette = { ...DEFAULT_PALETTE, ...paletteOverride }
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const samplingCanvas = document.createElement('canvas')
    const samplingContext = samplingCanvas.getContext('2d', { willReadFrequently: true })
    if (!samplingContext) return

    let width = window.innerWidth
    let height = window.innerHeight
    let reducedMotion = motionQuery.matches
    let visible = !document.hidden
    let frameId = 0
    let lastSample = -Infinity
    let particles: Particle[] = []
    let sourceVisuals: Visual[] = []
    let destinationVisuals: Visual[] = []

    const defaultVisual = (particle: Particle): Visual => ({
      x: particle.x,
      y: particle.y,
      color: palette.dark,
      opacity: 0.24,
      size: 1.25,
    })

    const readFrame = (
      source: CanvasImageSource,
      sourceWidth: number,
      sourceHeight: number,
      placement: Placement,
    ): Visual[] => {
      const viewportAspect = width / height
      const sampleWidth = width < 720 ? 216 : 384
      const sampleHeight = Math.max(1, Math.round(sampleWidth / viewportAspect))
      samplingCanvas.width = sampleWidth
      samplingCanvas.height = sampleHeight

      const sourceAspect = sourceWidth / sourceHeight
      let sx = 0
      let sy = 0
      let sw = sourceWidth
      let sh = sourceHeight
      if (sourceAspect > viewportAspect) {
        sw = sourceHeight * viewportAspect
        sx = (sourceWidth - sw) * 0.5
      } else {
        sh = sourceWidth / viewportAspect
        sy = (sourceHeight - sh) * 0.5
      }

      samplingContext.drawImage(source, sx, sy, sw, sh, 0, 0, sampleWidth, sampleHeight)
      const pixels = samplingContext.getImageData(0, 0, sampleWidth, sampleHeight).data
      const luminanceAt = (x: number, y: number) => {
        const px = Math.min(sampleWidth - 1, Math.max(0, x))
        const py = Math.min(sampleHeight - 1, Math.max(0, y))
        const offset = (py * sampleWidth + px) * 4
        return (
          pixels[offset] * 0.2126 +
          pixels[offset + 1] * 0.7152 +
          pixels[offset + 2] * 0.0722
        )
      }

      return particles.map((particle) => {
        const x = Math.min(sampleWidth - 2, Math.max(1, Math.floor(particle.x * sampleWidth)))
        const y = Math.min(sampleHeight - 2, Math.max(1, Math.floor(particle.y * sampleHeight)))
        const offset = (y * sampleWidth + x) * 4
        const red = pixels[offset]
        const green = pixels[offset + 1]
        const blue = pixels[offset + 2]
        const luminance = luminanceAt(x, y) / 255
        const edge = clamp(
          (Math.abs(luminanceAt(x + 1, y) - luminanceAt(x - 1, y)) +
            Math.abs(luminanceAt(x, y + 1) - luminanceAt(x, y - 1))) /
            145,
        )
        return {
          x: placement.left + particle.x * placement.width,
          y: placement.top + particle.y * placement.height,
          color: quantizeColor(red, green, blue, luminance, palette),
          opacity: clamp(0.24 + Math.pow(luminance, 0.62) * 0.72 + edge * 0.24),
          size: 1.25 + luminance * 1.45 + edge * 0.9,
        }
      })
    }

    const sampleVideo = () => {
      if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return
      if (!video.videoWidth || !video.videoHeight) return
      sourceVisuals = readFrame(video, video.videoWidth, video.videoHeight, {
        left: 0,
        top: 0,
        width: 1,
        height: 1,
      })
    }

    const loadDestination = async () => {
      if (!destinationImageSrc) return
      const image = new Image()
      image.decoding = 'async'
      image.src = destinationImageSrc
      await image.decode()
      destinationVisuals = readFrame(image, image.naturalWidth, image.naturalHeight, {
        left: destinationLeft,
        top: destinationTop,
        width: destinationWidth,
        height: destinationHeight,
      })
    }

    const resize = () => {
      width = root.clientWidth || window.innerWidth
      height = root.clientHeight || window.innerHeight
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5)
      canvas.width = Math.floor(width * ratio)
      canvas.height = Math.floor(height * ratio)
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      particles = makeParticles(width < 720 ? mobileParticles : desktopParticles, width / height)
      sourceVisuals = particles.map(defaultVisual)
      destinationVisuals = particles.map(defaultVisual)
      sampleVideo()
      void loadDestination()
    }

    const draw = (time: number) => {
      if (!visible) return
      context.clearRect(0, 0, width, height)

      if (!reducedMotion && time - lastSample > (width < 720 ? 110 : 85)) {
        sampleVideo()
        lastSample = time
      }

      const rawProgress = reducedMotion ? Math.round(progressRef.current) : progressRef.current
      const travel = smoothstep(rawProgress)
      const breakup = reducedMotion ? 0 : Math.sin(Math.PI * rawProgress)

      context.font = `${width < 720 ? 8 : 10}px ui-monospace, monospace`
      context.textAlign = 'center'
      context.textBaseline = 'middle'

      particles.forEach((particle, index) => {
        const from = sourceVisuals[index] || defaultVisual(particle)
        const to = destinationVisuals[index] || from
        const baseX = mix(from.x, to.x, travel) * width
        const baseY = mix(from.y, to.y, travel) * height
        const radialX = baseX - width * 0.5
        const radialY = baseY - height * 0.5
        const strength = 0.1 + particle.depth * 0.3
        let x = baseX + radialX * breakup * strength
        let y = baseY + radialY * breakup * strength * 0.66
        x += Math.cos(particle.phase) * width * 0.05 * breakup * particle.depth
        y += Math.sin(particle.phase * 1.37) * height * 0.06 * breakup * particle.depth
        if (!reducedMotion) {
          x += Math.sin(time * 0.0003 + particle.phase) * (particle.micro ? 0.65 : 1.6)
          y += Math.cos(time * 0.00024 + particle.phase) * (particle.micro ? 0.65 : 1.6)
        }

        const opacity = mix(from.opacity, to.opacity, travel) * (1 - breakup * 0.14)
        const size = mix(from.size, to.size, travel) * (1 - breakup * 0.18)
        context.globalAlpha = clamp(opacity)
        context.fillStyle = mixColor(from.color, to.color, travel)
        if (particle.micro) {
          context.fillRect(x - size * 0.5, y - size * 0.5, size, size)
        } else {
          const glyph = GLYPHS[Math.floor(particle.glyphSeed * GLYPHS.length)]
          context.fillText(glyph, x, y)
        }
      })

      context.globalAlpha = 1
      frameId = requestAnimationFrame(draw)
    }

    const changeMotion = (event: MediaQueryListEvent) => {
      reducedMotion = event.matches
      if (reducedMotion) video.pause()
      else void video.play().catch(() => undefined)
    }

    const changeVisibility = () => {
      visible = !document.hidden
      if (visible) {
        if (!reducedMotion) void video.play().catch(() => undefined)
        frameId = requestAnimationFrame(draw)
      } else {
        video.pause()
        cancelAnimationFrame(frameId)
      }
    }

    resize()
    video.addEventListener('loadeddata', sampleVideo)
    window.addEventListener('resize', resize)
    motionQuery.addEventListener('change', changeMotion)
    document.addEventListener('visibilitychange', changeVisibility)
    if (reducedMotion) video.pause()
    else void video.play().catch(() => undefined)
    frameId = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(frameId)
      video.removeEventListener('loadeddata', sampleVideo)
      window.removeEventListener('resize', resize)
      motionQuery.removeEventListener('change', changeMotion)
      document.removeEventListener('visibilitychange', changeVisibility)
    }
  }, [
    desktopParticles,
    destinationHeight,
    destinationImageSrc,
    destinationLeft,
    destinationTop,
    destinationWidth,
    mobileParticles,
    paletteOverride,
  ])

  return (
    <div ref={rootRef} className={`${styles.field} ${className || ''}`} aria-hidden="true">
      <video
        ref={videoRef}
        className={styles.decoder}
        src={videoSrc}
        poster={posterSrc}
        autoPlay
        muted
        playsInline
        preload="auto"
      />
      <canvas ref={canvasRef} className={styles.canvas} />
    </div>
  )
}
