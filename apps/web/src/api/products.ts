import type { paths } from "./generated/schema"

export type ProductListResponse =
  paths["/products"]["get"]["responses"][200]["content"]["application/json"]
export type ProductResponse =
  paths["/products/{product_id}"]["get"]["responses"][200]["content"]["application/json"]

export class ProductApiError extends Error {
  name = "ProductApiError"
}

const loadError = "Unable to load products. Please try again."

async function requestProductApi(path: string): Promise<Response> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  try {
    return await fetch(`${baseUrl.replace(/\/$/, "")}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    })
  } catch {
    throw new ProductApiError(loadError)
  }
}

async function readResponse<T>(response: Response): Promise<T> {
  if (!response.ok) throw new ProductApiError(loadError)
  try {
    return (await response.json()) as T
  } catch {
    throw new ProductApiError(loadError)
  }
}

export async function listProducts(): Promise<ProductListResponse> {
  return readResponse<ProductListResponse>(await requestProductApi("/products"))
}

export async function getProduct(productId: string): Promise<ProductResponse | null> {
  const response = await requestProductApi(`/products/${encodeURIComponent(productId)}`)
  if (response.status === 404) return null
  return readResponse<ProductResponse>(response)
}
