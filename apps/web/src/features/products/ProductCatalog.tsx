import Link from "next/link"

import type { ProductListResponse } from "@/api/products"
import { ProductImage } from "./ProductImage"
import styles from "./products.module.css"

export function ProductCatalog({ products }: { products: ProductListResponse["items"] }) {
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>The product collection</p>
        <h1>Discover local specialties</h1>
        <p className={styles.intro}>Explore products, their origins, and the stories behind them.</p>
      </header>
      {products.length === 0 ? (
        <section className={styles.state} role="status">
          <h2>No products yet</h2>
          <p>The catalog is currently empty. Please check back later.</p>
        </section>
      ) : (
        <>
          <p className={styles.count}>{products.length} {products.length === 1 ? "product" : "products"}</p>
          <ul className={styles.grid}>
            {products.map((product) => (
              <li key={product.id}>
                <Link href={`/products/${encodeURIComponent(product.id)}`} className={styles.card}>
                  <ProductImage src={product.images[0]} name={product.name} />
                  <div className={styles.cardBody}>
                    <div className={styles.tags}>
                      <span className={styles.category}>{product.category}</span>
                      <span className={styles.tagOrigin}>{product.origin}</span>
                    </div>
                    <h2>{product.name}</h2>
                    <p className={styles.description}>{product.description}</p>
                    <div className={styles.cardFooter}>
                      {product.price !== null && <span>Price: {product.price}</span>}
                      <span className={styles.view}>View product <span aria-hidden="true">→</span></span>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
