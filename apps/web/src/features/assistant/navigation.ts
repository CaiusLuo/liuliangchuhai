import type { AssistantSuggestedAction } from "../../api/assistant"

export function assistantActionHref(action: AssistantSuggestedAction): string {
  const id = encodeURIComponent(action.product_id)
  switch (action.type) {
    case "view_product": return `/products/${id}`
    case "start_analysis": return `/analysis?product_id=${id}`
  }
}
