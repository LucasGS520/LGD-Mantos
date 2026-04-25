import type { SVGProps } from 'react'

export interface IcoProps {
  size?: number
  stroke?: string
  sw?: number
  fill?: string
}

interface IconBaseProps extends IcoProps {
  d?: string
  children?: React.ReactNode
  vb?: number
}

function Icon({ d, size = 22, stroke = 'currentColor', fill = 'none', sw = 1.6, children, vb = 24 }: IconBaseProps) {
  return (
    <svg
      width={size} height={size}
      viewBox={`0 0 ${vb} ${vb}`}
      fill={fill} stroke={stroke}
      strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"
    >
      {d ? <path d={d} /> : children}
    </svg>
  )
}

export const Ico = {
  box:       (p: IcoProps) => <Icon {...p}><path d="M3 7.5L12 3l9 4.5M3 7.5v9L12 21l9-4.5v-9M3 7.5L12 12m9-4.5L12 12m0 0v9"/></Icon>,
  chart:     (p: IcoProps) => <Icon {...p}><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></Icon>,
  megaphone: (p: IcoProps) => <Icon {...p}><path d="M3 10v4l11 5V5L3 10zM3 10H2a1 1 0 00-1 1v2a1 1 0 001 1h1m11-5l5-3v14l-5-3M7 14v3a2 2 0 002 2h0a2 2 0 002-2"/></Icon>,
  more:      (p: IcoProps) => <Icon {...p}><circle cx="5" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1.5" fill="currentColor" stroke="none"/></Icon>,
  search:    (p: IcoProps) => <Icon {...p}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></Icon>,
  filter:    (p: IcoProps) => <Icon {...p}><path d="M3 5h18M6 12h12M10 19h4"/></Icon>,
  plus:      (p: IcoProps) => <Icon {...p}><path d="M12 5v14M5 12h14"/></Icon>,
  minus:     (p: IcoProps) => <Icon {...p}><path d="M5 12h14"/></Icon>,
  close:     (p: IcoProps) => <Icon {...p}><path d="M6 6l12 12M18 6L6 18"/></Icon>,
  back:      (p: IcoProps) => <Icon {...p}><path d="M15 18l-6-6 6-6"/></Icon>,
  chevron:   (p: IcoProps) => <Icon {...p}><path d="M9 18l6-6-6-6"/></Icon>,
  chevronDown:(p: IcoProps)=> <Icon {...p}><path d="M6 9l6 6 6-6"/></Icon>,
  check:     (p: IcoProps) => <Icon {...p}><path d="M5 12l5 5L20 7"/></Icon>,
  edit:      (p: IcoProps) => <Icon {...p}><path d="M4 20h4l10-10-4-4L4 16v4zM14 6l4 4"/></Icon>,
  trash:     (p: IcoProps) => <Icon {...p}><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/></Icon>,
  camera:    (p: IcoProps) => <Icon {...p}><path d="M3 8h3l2-3h8l2 3h3v11H3V8z"/><circle cx="12" cy="13" r="4"/></Icon>,
  upload:    (p: IcoProps) => <Icon {...p}><path d="M12 16V4M6 10l6-6 6 6M4 20h16"/></Icon>,
  send:      (p: IcoProps) => <Icon {...p}><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></Icon>,
  tag:       (p: IcoProps) => <Icon {...p}><path d="M3 12V3h9l9 9-9 9-9-9z"/><circle cx="7.5" cy="7.5" r="1" fill="currentColor"/></Icon>,
  truck:     (p: IcoProps) => <Icon {...p}><path d="M2 7h11v10H2zM13 11h5l3 3v3h-8M5 19a2 2 0 100-4 2 2 0 000 4zM17 19a2 2 0 100-4 2 2 0 000 4z"/></Icon>,
  cart:      (p: IcoProps) => <Icon {...p}><path d="M3 4h2l2 12h12l2-9H6M9 20a1 1 0 100 0M19 20a1 1 0 100 0"/></Icon>,
  receipt:   (p: IcoProps) => <Icon {...p}><path d="M5 3v18l3-2 2 2 2-2 2 2 2-2 3 2V3l-3 2-2-2-2 2-2-2-2 2-3-2zM8 8h8M8 12h8M8 16h5"/></Icon>,
  cash:      (p: IcoProps) => <Icon {...p}><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 10v.01M18 14v.01"/></Icon>,
  warning:   (p: IcoProps) => <Icon {...p}><path d="M12 3L2 20h20L12 3zM12 10v5M12 18v.01"/></Icon>,
  alert:     (p: IcoProps) => <Icon {...p}><circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16v.01"/></Icon>,
  bell:      (p: IcoProps) => <Icon {...p}><path d="M6 8a6 6 0 0112 0c0 7 3 7 3 9H3c0-2 3-2 3-9zM10 21a2 2 0 004 0"/></Icon>,
  trend:     (p: IcoProps) => <Icon {...p}><path d="M3 17l6-6 4 4 8-8M14 7h7v7"/></Icon>,
  trendDown: (p: IcoProps) => <Icon {...p}><path d="M3 7l6 6 4-4 8 8M14 17h7v-7"/></Icon>,
  user:      (p: IcoProps) => <Icon {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0116 0v1"/></Icon>,
  users:     (p: IcoProps) => <Icon {...p}><circle cx="9" cy="8" r="3.5"/><path d="M2 20v-1a5 5 0 0114 0v1M16 4a3.5 3.5 0 010 7M22 20v-1a5 5 0 00-4-4.9"/></Icon>,
  store:     (p: IcoProps) => <Icon {...p}><path d="M3 9l1.5-5h15L21 9M4 9v11h16V9M4 9h16M9 14h6v6H9z"/></Icon>,
  sparkle:   (p: IcoProps) => <Icon {...p}><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16z"/></Icon>,
  brain:     (p: IcoProps) => <Icon {...p}><path d="M9 4a3 3 0 00-3 3v1a3 3 0 00-3 3 3 3 0 003 3v1a3 3 0 003 3h6a3 3 0 003-3v-1a3 3 0 003-3 3 3 0 00-3-3V7a3 3 0 00-3-3H9zM9 4v16M15 4v16"/></Icon>,
  package:   (p: IcoProps) => <Icon {...p}><path d="M3 8l9-5 9 5v8l-9 5-9-5V8zM3 8l9 5 9-5M12 13v8"/></Icon>,
  tshirt:    (p: IcoProps) => <Icon {...p}><path d="M4 7l4-4h2c0 1.5 1 2.5 2 2.5s2-1 2-2.5h2l4 4-3 3v10H7V10L4 7z"/></Icon>,
  pie:       (p: IcoProps) => <Icon {...p}><path d="M12 3a9 9 0 109 9h-9V3z"/><path d="M14 3a7 7 0 017 7h-7V3z"/></Icon>,
  doc:       (p: IcoProps) => <Icon {...p}><path d="M6 3h9l4 4v14H6V3zM15 3v4h4M9 13h6M9 17h6"/></Icon>,
  calendar:  (p: IcoProps) => <Icon {...p}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></Icon>,
  settings:  (p: IcoProps) => <Icon {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1A1.7 1.7 0 009 19.4a1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1A1.7 1.7 0 004.6 9a1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z"/></Icon>,
  logout:    (p: IcoProps) => <Icon {...p}><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></Icon>,
  refresh:   (p: IcoProps) => <Icon {...p}><path d="M3 12a9 9 0 0015-6.7L21 8M21 4v4h-4M21 12a9 9 0 01-15 6.7L3 16M3 20v-4h4"/></Icon>,
  history:   (p: IcoProps) => <Icon {...p}><path d="M3 12a9 9 0 109-9 9 9 0 00-7.5 4M3 4v4h4M12 7v5l4 2"/></Icon>,
  cloudOff:  (p: IcoProps) => <Icon {...p}><path d="M3 3l18 18M9 5a5 5 0 016.5 4.5A4 4 0 0119 17M5 9a5 5 0 00-1 8h11"/></Icon>,
  link:      (p: IcoProps) => <Icon {...p}><path d="M10 14a4 4 0 005 0l3-3a4 4 0 00-5-5l-1 1M14 10a4 4 0 00-5 0l-3 3a4 4 0 005 5l1-1"/></Icon>,
  phone:     (p: IcoProps) => <Icon {...p}><path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/></Icon>,
  mail:      (p: IcoProps) => <Icon {...p}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></Icon>,
  copy:      (p: IcoProps) => <Icon {...p}><rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 00-2-2H5a2 2 0 00-2 2v9a2 2 0 002 2h3"/></Icon>,
  options:   (p: IcoProps) => <Icon {...p}><circle cx="12" cy="6" r="1.5" fill="currentColor"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/><circle cx="12" cy="18" r="1.5" fill="currentColor"/></Icon>,
  eye:       (p: IcoProps) => <Icon {...p}><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></Icon>,
  eyeOff:    (p: IcoProps) => <Icon {...p}><path d="M3 3l18 18M10 6.5A10 10 0 0112 6c6 0 10 7 10 7a17 17 0 01-3 4M6 6c-2 1.5-4 6-4 6s4 7 10 7c1.7 0 3.3-.6 4.7-1.5M9.9 9.9a3 3 0 004.2 4.2"/></Icon>,
  lock:      (p: IcoProps) => <Icon {...p}><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></Icon>,
  wifi:      (p: IcoProps) => <Icon {...p}><path d="M2 9a17 17 0 0120 0M5 13a12 12 0 0114 0M8.5 17a6 6 0 017 0M12 21v.01"/></Icon>,
} as const

export type IcoKey = keyof typeof Ico
