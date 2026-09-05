"use client"

import { useRef, useState, type FormEvent } from "react"

import {
  ContentPlanApiError,
  createContentPlan,
  type ContentPlanRequest,
  type ContentPlanResponse,
} from "@/api/content-plan"

import styles from "./analysis.module.css"

type ContentPlanState =
  | { status: "ready" | "generating" }
  | { status: "error"; message: string }
  | { status: "success"; result: ContentPlanResponse }

export default function ContentPlanSection({
  request,
}: {
  request: Omit<ContentPlanRequest, "target_language">
}) {
  const [language, setLanguage] = useState("English")
  const [plan, setPlan] = useState<ContentPlanState>({ status: "ready" })
  const inFlight = useRef(false)
  const generating = plan.status === "generating"

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (inFlight.current || !language.trim()) return
    inFlight.current = true
    setPlan({ status: "generating" })
    try {
      const result = await createContentPlan({ ...request, target_language: language.trim() })
      setPlan({ status: "success", result })
    } catch (error) {
      setPlan({
        status: "error",
        message: error instanceof ContentPlanApiError
          ? error.message : "Unable to create content plan. Please try again.",
      })
    } finally {
      inFlight.current = false
    }
  }

  const textSections = plan.status === "success" ? [
    ["Image prompt", plan.result.image_prompt],
    ["Short video idea", plan.result.short_video_idea],
    ["Short video prompt", plan.result.short_video_prompt],
    ["Live script", plan.result.live_script],
    ["Social caption", plan.result.social_caption],
  ] as const : []

  return (
    <section className={styles.contentPlan} aria-labelledby="content-plan-title" aria-busy={generating}>
      <h2 id="content-plan-title">Content plan</h2>
      <p className={styles.muted}>
        Prepare marketing copy and creative prompts from this analysis. No images or videos are generated; review product claims and local suitability before use.
      </p>
      <form onSubmit={submit}>
        <fieldset className={styles.fields} disabled={generating}>
          <label htmlFor="content-language">Target language</label>
          <input
            id="content-language"
            value={language}
            onChange={(event) => {
              setLanguage(event.target.value)
              setPlan({ status: "ready" })
            }}
            required
          />
          <button className={styles.submitButton} type="submit" disabled={generating || !language.trim()}>
            {generating ? "Generating…" : "Generate content plan"}
          </button>
        </fieldset>
      </form>
      <p className={styles.status} role="status" aria-live="polite">
        {generating ? "Generating content plan…" : plan.status === "success" ? "Content plan ready." : ""}
      </p>
      {plan.status === "error" && <p className={styles.error} role="alert">{plan.message}</p>}
      {plan.status === "success" && (
        <div className={styles.sections}>
          <section>
            <h3>Key selling points</h3>
            <ul>{plan.result.key_selling_points.map((point, index) => <li key={`${index}-${point}`}>{point}</li>)}</ul>
          </section>
          {textSections.map(([title, text]) => (
            <section key={title}>
              <h3>{title}</h3>
              <p>{text}</p>
            </section>
          ))}
        </div>
      )}
    </section>
  )
}
