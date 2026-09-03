import type { paths } from "./generated/schema"

export type HealthResponse =
  paths["/health"]["get"]["responses"][200]["content"]["application/json"]

export async function getHealth(): Promise<HealthResponse | null> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

  try {
    const response = await fetch(`${baseUrl}/health`, { cache: "no-store" })
    if (!response.ok) return null
    return (await response.json()) as HealthResponse
  } catch {
    return null
  }
}
