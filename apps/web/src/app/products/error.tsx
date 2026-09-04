"use client"

import Link from "next/link"

import styles from "@/features/products/products.module.css"

export default function ProductsError({ retry }: { retry: () => void }) {
  return (
    <main className={styles.page}>
      <div className={styles.state} role="alert">
        <p className={styles.eyebrow}>The product collection</p>
        <h1>Unable to load products</h1>
        <p>Product information is temporarily unavailable. Please try again.</p>
        <div className={styles.actions}>
          <button className={styles.button} onClick={() => retry()}>Try again</button>
          <Link className={styles.secondaryButton} href="/products">Back to catalog</Link>
        </div>
      </div>
    </main>
  )
}
