import type { paths } from "./generated/schema"

type Operation = paths["/assistant/chat"]["post"]
export type AssistantRequest = Operation["requestBody"]["content"]["application/json"]
export type AssistantReply = Operation["responses"][200]["content"]["application/json"]
export type AssistantSuggestedAction = NonNullable<AssistantReply["suggested_action"]>

export const assistantErrorMessage = "当前助手暂时无法回答，请稍后再试。"

export class AssistantApiError extends Error {
  name = "AssistantApiError"
}

export function createAssistantRequest(message: string, productId?: string): AssistantRequest {
  return productId === undefined ? { message } : { message, product_id: productId }
}

export async function replyToAssistant(request: AssistantRequest): Promise<AssistantReply> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  try {
    if (!request.message.trim()) throw new AssistantApiError(assistantErrorMessage)
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/assistant/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Explicitly pick current-turn fields; never serialize component conversation state.
      body: JSON.stringify(createAssistantRequest(request.message, request.product_id ?? undefined)),
      signal: AbortSignal.timeout(20_000),
    })
    if (!response.ok) throw new AssistantApiError(assistantErrorMessage)
    return (await response.json()) as AssistantReply
  } catch {
    throw new AssistantApiError(assistantErrorMessage)
  }
}
