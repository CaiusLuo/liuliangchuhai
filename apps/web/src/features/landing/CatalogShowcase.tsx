import Link from "next/link"
import { cache } from "react"

import { listProducts } from "@/api/products"
import styles from "@/app/page.module.css"
import { CatalogImage } from "./CatalogImage"
import { selectFeaturedProducts } from "./featured-products"

// Both streamed sections share one catalog read per server render.
const loadFeaturedProducts = cache(async () => {
  try {
    return selectFeaturedProducts((await listProducts()).items)
  } catch {
    return null
  }
})

export async function HeroExample() {
  const products = await loadFeaturedProducts()
  const product = products?.[0]

  return (
    <div className={styles.example}>
      <div className={styles.exampleTop}><span>LOCAL ROOTS</span><span>CHINA → ASEAN</span></div>
      {product ? (
        <>
          <div className={styles.heroProduct}>
            <CatalogImage src={product.images[0]} name={product.name} priority />
            <div className={styles.productLabel}><span>{product.origin} · {product.category}</span><h2>{product.name}</h2></div>
          </div>
          <div className={styles.exampleReport}>
            <p className={styles.reportEyebrow}>AN EXAMPLE TO EXPLORE <span aria-hidden="true">↗</span></p>
            <h3>{product.name} <span aria-hidden="true">→</span> Malaysia</h3>
            <div className={styles.reportRow}><span>Demo recommendation</span><span className={styles.caution}>Caution</span></div>
            <p className={styles.reportNote}>Sample output: market assumptions need validation.</p>
            <p className={styles.reportContent}>Add your audience, then create a product introduction and social caption.</p>
            <Link className={styles.textLink} href={`/analysis?product_id=${encodeURIComponent(product.id)}`}>Try this product <span aria-hidden="true">→</span></Link>
          </div>
        </>
      ) : (
        <div className={styles.visualEmpty}>
          <span aria-hidden="true">↗</span>
          <h2>A local story.<br />A new market.</h2>
          <p>Choose a product and an ASEAN market to begin your demo.</p>
        </div>
      )}
      <p className={styles.exampleFoot}>PRODUCT <span>→</span> MARKET <span>→</span> CONTENT</p>
    </div>
  )
}

export async function FeaturedProducts() {
  const products = await loadFeaturedProducts()

  if (!products?.length) {
    return (
      <div className={styles.catalogState} role="status">
        <h3>{products === null ? "The collection is taking a moment." : "New product stories are on the way."}</h3>
        <p>{products === null ? "Featured products are temporarily unavailable. You can still explore the demo." : "There are no products in the catalog yet. Please check back later."}</p>
        <Link className={styles.textLink} href="/products">Visit the product catalog <span aria-hidden="true">→</span></Link>
      </div>
    )
  }

  return (
    <ul className={styles.productGrid}>
      {products.map((product, index) => (
        <li key={product.id} className={styles.productCard}>
          <div className={styles.cardImage}>
            <CatalogImage src={product.images[0]} name={product.name} />
            <span className={styles.cardNumber}>THE COLLECTION / 0{index + 1}</span>
          </div>
          <div className={styles.cardBody}>
            <div className={styles.tags}><span className={styles.tag}>{product.category}</span><span className={styles.tag}>{product.origin}</span></div>
            <h3>{product.name}</h3>
            <p className={styles.description}>{product.description}</p>
            <div className={styles.cardActions}>
              <Link className={styles.secondary} href={`/products/${encodeURIComponent(product.id)}`} aria-label={`View Product: ${product.name}`}>View Product</Link>
              <Link className={styles.primary} href={`/analysis?product_id=${encodeURIComponent(product.id)}`} aria-label={`Start Analysis: ${product.name}`}>Start Analysis <span aria-hidden="true">↗</span></Link>
            </div>
          </div>
        </li>
      ))}
    </ul>
  )
}
