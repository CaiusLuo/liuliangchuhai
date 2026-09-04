import Link from "next/link"

import styles from "./page.module.css"

export default function Home() {
  return (
    <main className={styles.page}>
      <p className="eyebrow">Guangxi → ASEAN</p>
      <h1>Local products.<br />New market possibilities.</h1>
      <p className={styles.intro}>
        AI-assisted market analysis and content planning for Guangxi products entering ASEAN markets.
      </p>
      <nav className={styles.actions} aria-label="Start exploring">
        <Link className={styles.primary} href="/analysis">Start AI analysis →</Link>
        <Link href="/products">Browse products →</Link>
      </nav>
      <p className={styles.flow}>Choose a product · Explore market fit · Create a content plan</p>
      <p className={styles.note}>Try the complete flow with deterministic mock providers. No API keys needed.</p>
    </main>
  )
}
