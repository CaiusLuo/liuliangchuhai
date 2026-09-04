import type { paths } from "./generated/schema"

export type ContentPlanRequest =
  paths["/content-plan"]["post"]["requestBody"]["content"]["application/json"]
export type ContentPlanResponse =
  paths["/content-plan"]["post"]["responses"][200]["content"]["application/json"]

export class ContentPlanApiError extends Error {
  name = "ContentPlanApiError"
}

const planningError = "Unable to create content plan. Please try again."
const statusMessages: Partial<Record<number, string>> = {
  404: "The selected product is no longer available.",
  422: "Please check the content planning inputs.",
  500: planningError,
}

export async function createContentPlan(request: ContentPlanRequest): Promise<ContentPlanResponse> {
  const targetLanguage = request.target_language.trim()
  if (!targetLanguage) throw new ContentPlanApiError("Please enter a target language.")

  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  try {
    const response = await fetch(`${baseUrl}/content-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...request, target_language: targetLanguage }),
    })
    if (!response.ok) {
      throw new ContentPlanApiError(statusMessages[response.status] ?? planningError)
    }
    return (await response.json()) as ContentPlanResponse
  } catch (error) {
    if (error instanceof ContentPlanApiError) throw error
    throw new ContentPlanApiError(planningError)
  }
}
