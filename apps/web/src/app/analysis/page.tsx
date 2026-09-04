import Link from "next/link"

import AnalysisWorkbench from "@/features/selection/AnalysisWorkbench"
import styles from "@/features/selection/analysis.module.css"

export default async function AnalysisPage({ searchParams }: {
  searchParams: Promise<{ product_id?: string | string[] }>
}) {
  const { product_id } = await searchParams
  const initialProductId = typeof product_id === "string" ? product_id : ""

  return (
    <main className={styles.page}>
      <nav className={styles.navigation} aria-label="Demo navigation">
        <Link href="/">Home</Link>
        <Link href="/products">Browse products</Link>
      </nav>
      <AnalysisWorkbench initialProductId={initialProductId} />
    </main>
  )
}
