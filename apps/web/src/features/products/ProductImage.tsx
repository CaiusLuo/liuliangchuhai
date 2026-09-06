"use client"

import { useState } from "react"

import { isUsableImageSource } from "./image-source"
import styles from "./products.module.css"

export function ProductImage({ src, name, index = 0 }: {
  src?: string
  name: string
  index?: number
}) {
  const [failedSource, setFailedSource] = useState<string>()
  const usable = isUsableImageSource(src) && failedSource !== src

  return (
    <div className={styles.image}>
      {usable ? (
        // Catalog-owned local and remote sources need no global Next.js image configuration.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          ref={(image) => {
            // A cached image failure can happen before React attaches onError.
            if (image?.complete && image.naturalWidth === 0) setFailedSource(src)
          }}
          src={src}
          alt={`${name} — product image ${index + 1}`}
          loading={index === 0 ? "eager" : "lazy"}
          onError={() => setFailedSource(src)}
        />
      ) : (
        <span className={styles.imagePlaceholder}>
          <span aria-hidden="true" className={styles.imageMark}>◇</span>
          Image unavailable
        </span>
      )}
    </div>
  )
}
