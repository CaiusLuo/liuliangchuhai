import type { Metadata } from "next"
import type { ReactNode } from "react"

import "./styles.css"

export const metadata: Metadata = {
  title: "liuliangchuhai",
  description: "AI-assisted market analysis and content planning for Guangxi products entering ASEAN markets.",
}

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
