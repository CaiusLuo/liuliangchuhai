import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { getProduct } from "@/api/products"
import { AssistantProductContext } from "@/features/assistant/AssistantProvider"
import { ProductDetail } from "@/features/products/ProductDetail"

// Fetch the live catalog at request time; builds must not require the API.
export const dynamic = "force-dynamic"

export const metadata: Metadata = { title: "Product details | liuliangchuhai" }

export default async function ProductPage({ params }: {
  params: Promise<{ productId: string }>
}) {
  const { productId } = await params
  const product = await getProduct(productId)
  if (!product) notFound()
  return <>
    <AssistantProductContext id={product.id} name={product.name} />
    <ProductDetail product={product} />
  </>
}
