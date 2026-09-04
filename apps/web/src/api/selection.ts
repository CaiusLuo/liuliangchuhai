import type { paths } from "./generated/schema"

export type ProductListResponse =
  paths["/products"]["get"]["responses"][200]["content"]["application/json"]
export type ProductAnalysisRequest =
  paths["/product-analysis"]["post"]["requestBody"]["content"]["application/json"]
export type ProductAnalysisResponse =
  paths["/product-analysis"]["post"]["responses"][200]["content"]["application/json"]

export class SelectionApiError extends Error {
  name = "SelectionApiError"
}

const catalogError = "Unable to load products. Please try again."
const analysisError = "Unable to run analysis. Please try again."
const inputError = "Please check the form inputs."
const analysisStatusMessages: Partial<Record<number, string>> = {
  422: inputError,
  404: "The selected product is no longer available.",
  502: "Analysis returned an invalid response. Please try again.",
  503: "Analysis service is temporarily unavailable. Please try again later.",
}

export async function listProducts(): Promise<ProductListResponse> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  try {
    const response = await fetch(`${baseUrl}/products`, { cache: "no-store" })
    if (!response.ok) throw new SelectionApiError(catalogError)
    return (await response.json()) as ProductListResponse
  } catch {
    throw new SelectionApiError(catalogError)
  }
}

export async function analyzeProduct(
  request: ProductAnalysisRequest,
): Promise<ProductAnalysisResponse> {
  const normalized: ProductAnalysisRequest = {
    product_id: request.product_id.trim(),
    country: request.country.trim(),
    target_audience: request.target_audience?.trim() || null,
    market_notes: request.market_notes?.trim() || null,
  }
  if (!normalized.product_id || !normalized.country) {
    throw new SelectionApiError(inputError)
  }

  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  try {
    const response = await fetch(`${baseUrl}/product-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(normalized),
    })
    if (!response.ok) {
      throw new SelectionApiError(analysisStatusMessages[response.status] ?? analysisError)
    }
    return (await response.json()) as ProductAnalysisResponse
  } catch (error) {
    if (error instanceof SelectionApiError) throw error
    throw new SelectionApiError(analysisError)
  }
}
