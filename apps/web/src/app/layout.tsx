import type { Metadata } from "next"
import Link from "next/link"
import type { ReactNode } from "react"

import "./styles.css"
import ui from "./ui.module.css"

export const metadata: Metadata = {
  title: "liuliangchuhai",
  description: "AI-assisted market analysis and content planning for Guangxi products entering ASEAN markets.",
}

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className={ui.skipLink} href="#main-content">Skip to content</a>
        <header className={ui.navigation}>
          <Link href="/" className={ui.brand} aria-label="liuliangchuhai home">
            <span className={ui.brandMark} aria-hidden="true">↗</span>
            <span>liuliangchuhai<span className={ui.brandCaption}>LOCAL ROOTS. NEW HORIZONS.</span></span>
          </Link>
          <nav aria-label="Main navigation">
            <Link className={ui.navProducts} href="/products">Products</Link>
            <Link className={ui.navAction} href="/analysis">Start Analysis <span aria-hidden="true">↗</span></Link>
          </nav>
        </header>
        <div id="main-content" className={ui.content} tabIndex={-1}>{children}</div>
        <footer className={ui.footer}>
          <span>liuliangchuhai <span className={ui.footerChinese}>流量出海</span></span>
          <span>Guangxi, China <span aria-hidden="true">→</span> ASEAN markets</span>
          <span>An AI-assisted strategy demo</span>
        </footer>
      </body>
    </html>
  )
}
