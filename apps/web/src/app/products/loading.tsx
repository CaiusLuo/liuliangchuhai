import styles from "@/features/products/products.module.css"

export default function LoadingProducts() {
  return (
    <main className={styles.page} aria-busy="true">
      <div className={styles.state} role="status">
        <p className={styles.eyebrow}>The product collection</p>
        <h1>Loading products…</h1>
        <p>Retrieving product information.</p>
      </div>
    </main>
  )
}
