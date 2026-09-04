import type { Metadata } from "next"

import { listProducts } from "@/api/products"
import { ProductCatalog } from "@/features/products/ProductCatalog"

// Fetch the live catalog at request time; builds must not require the API.
export const dynamic = "force-dynamic"

export const metadata: Metadata = {
  title: "Product catalog | liuliangchuhai",
  description: "Explore local specialties and the stories behind them.",
}

export default async function ProductsPage() {
  const products = await listProducts()
  return <ProductCatalog products={products.items} />
}
