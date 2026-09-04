import Link from "next/link"

import styles from "@/features/products/products.module.css"

export default function ProductNotFound() {
  return (
    <main className={styles.page}>
      <div className={styles.state}>
        <p className={styles.eyebrow}>Product not found · 404</p>
        <h1>This product is unavailable</h1>
        <p>It may have been removed, or the link may be incorrect.</p>
        <Link className={styles.button} href="/products">Browse all products</Link>
      </div>
    </main>
  )
}
