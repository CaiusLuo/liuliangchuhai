"use client"

import { useState } from "react"

import styles from "@/app/page.module.css"

export function CatalogImage({ src, name, priority = false }: {
  src?: string
  name: string
  priority?: boolean
}) {
  const [failedSource, setFailedSource] = useState<string>()
  const usable = src && /^https?:\/\//i.test(src) && failedSource !== src

  return (
    <div className={styles.catalogImage}>
      {usable ? (
        // Catalog-owned URLs follow the existing adapter/image display pattern.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={src}
          alt={name}
          loading={priority ? "eager" : "lazy"}
          ref={(image) => {
            if (image?.complete && image.naturalWidth === 0) setFailedSource(src)
          }}
          onError={() => setFailedSource(src)}
        />
      ) : (
        <div className={styles.imageFallback}>
          <span className={styles.originSeal} aria-hidden="true">桂</span>
          <span className={styles.fallbackName}>{name}</span>
          <span className={styles.imageUnavailable}>{src ? "Product image unavailable" : "Catalog image not provided"}</span>
        </div>
      )}
    </div>
  )
}
