import type { ProductListResponse } from "@/api/selection"

export function resolveProductSelection(
  products: ProductListResponse["items"],
  initialProductId: string,
  selectedProductId: string | null,
): string {
  const candidate = selectedProductId ?? initialProductId
  return candidate && products.some((product) => product.id === candidate) ? candidate : ""
}
