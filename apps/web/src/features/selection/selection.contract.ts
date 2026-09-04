import type { paths } from "@/api/generated/schema"

type ProductListResponse =
  paths["/products"]["get"]["responses"][200]["content"]["application/json"]
type ProductAnalysisRequest =
  paths["/product-analysis"]["post"]["requestBody"]["content"]["application/json"]
type ProductAnalysisResponse =
  paths["/product-analysis"]["post"]["responses"][200]["content"]["application/json"]

type RequireSelectionApi<
  Api extends {
    listProducts: () => Promise<ProductListResponse>
    analyzeProduct: (request: ProductAnalysisRequest) => Promise<ProductAnalysisResponse>
  },
> = Api

// Type-only probe: the planned API module is intentionally absent during RED.
export type SelectionApiContract = RequireSelectionApi<typeof import("@/api/selection")>
