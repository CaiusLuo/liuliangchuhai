"use client"

import { usePathname } from "next/navigation"
import { createContext, useContext, useEffect, useState } from "react"
import type { Dispatch, ReactNode, SetStateAction } from "react"

import type { ProductResponse } from "@/api/products"
import { AssistantWidget } from "./AssistantWidget"

export type AssistantProduct = Pick<ProductResponse, "id" | "name">
const ProductContext = createContext<Dispatch<SetStateAction<AssistantProduct | null>> | null>(null)

export function AssistantProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  const [registeredProduct, setProduct] = useState<AssistantProduct | null>(null)
  // Route gating clears context immediately, even before the detail effect cleans up.
  const product = registeredProduct && pathname === `/products/${encodeURIComponent(registeredProduct.id)}`
    ? registeredProduct
    : null

  return (
    <ProductContext.Provider value={setProduct}>
      {children}
      <AssistantWidget product={product} conversationKey={product?.id ?? pathname} />
    </ProductContext.Provider>
  )
}

export function AssistantProductContext({ id, name }: AssistantProduct) {
  const setProduct = useContext(ProductContext)
  useEffect(() => {
    setProduct?.({ id, name })
    return () => setProduct?.(null)
  }, [id, name, setProduct])
  return null
}
