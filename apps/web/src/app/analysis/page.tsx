import AnalysisWorkbench from "@/features/selection/AnalysisWorkbench"
import styles from "@/features/selection/analysis.module.css"

export default function AnalysisPage() {
  return (
    <main className={styles.page}>
      <AnalysisWorkbench />
    </main>
  )
}
