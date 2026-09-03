import type { Metadata } from "next"
import type { ReactNode } from "react"

import "./styles.css"

export const metadata: Metadata = {
  title: "liuliangchuhai",
  description: "Phase 0 development shell",
}

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
