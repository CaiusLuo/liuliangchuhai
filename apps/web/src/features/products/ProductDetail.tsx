import Link from "next/link"

import type { ProductResponse } from "@/api/products"
import { ProductImage } from "./ProductImage"
import styles from "./products.module.css"

export function ProductDetail({ product }: { product: ProductResponse }) {
  const purchaseUrl = product.purchase_url && /^https?:\/\//i.test(product.purchase_url)
    ? product.purchase_url
    : null

  return (
    <main className={styles.page}>
      <nav aria-label="Breadcrumb" className={styles.breadcrumb}>
        <Link href="/products">← All products</Link>
      </nav>
      <article className={styles.detail}>
        <div className={styles.gallery} aria-label={`${product.name} images`}>
          {product.images.length > 0 ? product.images.map((src, index) => (
            <ProductImage key={`${index}-${src}`} src={src} name={product.name} index={index} />
          )) : <ProductImage name={product.name} />}
        </div>
        <div className={styles.detailBody}>
          <header>
            <p className={styles.eyebrow}>{product.category}</p>
            <h1>{product.name}</h1>
            <p className={styles.origin}>Origin · {product.origin}</p>
            <p className={styles.fullDescription}>{product.description}</p>
            {product.price !== null && <p className={styles.price}>Price: {product.price}</p>}
            <p>
              <Link className={styles.button} href={{ pathname: "/analysis", query: { product_id: product.id } }}>
                Analyze market fit
              </Link>
            </p>
            {purchaseUrl && (
              <a href={purchaseUrl} target="_blank" rel="noopener noreferrer">
                Visit seller website ↗ <span className={styles.newTab}>(opens in a new tab)</span>
              </a>
            )}
          </header>
          {product.cultural_background && (
            <section className={styles.section}>
              <h2>Cultural background</h2>
              <p>{product.cultural_background}</p>
            </section>
          )}
          {product.usage && (
            <section className={styles.section}>
              <h2>How to use</h2>
              <p>{product.usage}</p>
            </section>
          )}
          {product.ingredients.length > 0 && (
            <section className={styles.section}>
              <h2>Ingredients</h2>
              <ul className={styles.ingredients}>
                {product.ingredients.map((ingredient, index) => <li key={`${index}-${ingredient}`} className={styles.ingredient}>{ingredient}</li>)}
              </ul>
            </section>
          )}
        </div>
      </article>
    </main>
  )
}
