import type { ProductListResponse } from "@/api/products"

// Editorial picks for the demo, in display order; no ranking or scoring.
export const featuredProductIds = [
  "wuzhou-liubao-tea",
  "liuzhou-luosifen",
  "guilin-luohanguo",
] as const

export function selectFeaturedProducts(products: ProductListResponse["items"]) {
  const featured = featuredProductIds.flatMap((id) => {
    const product = products.find((item) => item.id === id)
    return product ? [product] : []
  })
  return featured.length > 0 ? featured : products.slice(0, 3)
}
