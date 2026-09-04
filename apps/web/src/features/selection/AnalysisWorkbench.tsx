"use client"

import { useEffect, useRef, useState, type FormEvent } from "react"

import {
  analyzeProduct,
  listProducts,
  SelectionApiError,
  type ProductAnalysisRequest,
  type ProductAnalysisResponse,
  type ProductListResponse,
} from "@/api/selection"

import ContentPlanSection from "./ContentPlanSection"
import styles from "./analysis.module.css"

type CatalogState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; products: ProductListResponse["items"] }

type AnalysisState =
  | { status: "idle" | "submitting" }
  | { status: "error"; message: string }
  | { status: "success"; result: ProductAnalysisResponse; request: ProductAnalysisRequest }

const recommendationLabels: Record<ProductAnalysisResponse["recommendation"], string> = {
  strong_fit: "Strong fit",
  fit: "Fit",
  caution: "Caution",
  not_recommended: "Not recommended",
}

function AnalysisReport({ result }: { result: ProductAnalysisResponse }) {
  const sections = [
    ["Target audiences", result.target_audiences],
    ["Strengths", result.strengths],
    ["Risks", result.risks],
    ["Cultural advantages", result.cultural_advantages],
    ["Marketing suggestions", result.marketing_suggestions],
    ["Content directions", result.content_directions],
  ] as const

  return (
    <>
      <p className={styles.recommendation}>{recommendationLabels[result.recommendation]}</p>
      <p className={styles.score}>Heuristic score: {result.score} / 100</p>
      <p className={styles.muted}>
        This is a heuristic planning indicator, not a probability or sales forecast.
      </p>
      <h3>Summary</h3>
      <p>{result.summary}</p>
      <div className={styles.sections}>
        {sections.map(([title, items]) => (
          <section key={title}>
            <h3>{title}</h3>
            {items.length ? (
              <ul>{items.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul>
            ) : <p className={styles.muted}>None provided.</p>}
          </section>
        ))}
      </div>
    </>
  )
}

export default function AnalysisWorkbench() {
  const [catalog, setCatalog] = useState<CatalogState>({ status: "loading" })
  const [catalogAttempt, setCatalogAttempt] = useState(0)
  const [analysis, setAnalysis] = useState<AnalysisState>({ status: "idle" })
  const [productId, setProductId] = useState("")
  const [country, setCountry] = useState("")
  const [targetAudience, setTargetAudience] = useState("")
  const [marketNotes, setMarketNotes] = useState("")
  const inFlight = useRef(false)

  useEffect(() => {
    let active = true
    listProducts().then(
      (response) => {
        if (active) setCatalog({ status: "ready", products: response.items })
      },
      (error: unknown) => {
        if (active) setCatalog({
          status: "error",
          message: error instanceof SelectionApiError
            ? error.message : "Unable to load products. Please try again.",
        })
      },
    )
    return () => { active = false }
  }, [catalogAttempt])

  const products = catalog.status === "ready" ? catalog.products : []
  const catalogReady = catalog.status === "ready" && products.length > 0
  const submitting = analysis.status === "submitting"
  const canSubmit = catalogReady && Boolean(productId.trim() && country.trim()) && !submitting

  function retryCatalog() {
    setCatalog({ status: "loading" })
    setProductId("")
    setAnalysis({ status: "idle" })
    setCatalogAttempt((attempt) => attempt + 1)
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (inFlight.current) return

    const request: ProductAnalysisRequest = {
      product_id: productId.trim(),
      country: country.trim(),
      target_audience: targetAudience.trim() || null,
      market_notes: marketNotes.trim() || null,
    }
    if (!catalogReady || !request.product_id || !request.country) {
      setAnalysis({ status: "error", message: "Please check the form inputs." })
      return
    }

    inFlight.current = true
    setAnalysis({ status: "submitting" })
    try {
      const result = await analyzeProduct(request)
      setAnalysis({ status: "success", result, request })
    } catch (error) {
      setAnalysis({
        status: "error",
        message: error instanceof SelectionApiError
          ? error.message : "Unable to run analysis. Please try again.",
      })
    } finally {
      inFlight.current = false
    }
  }

  return (
    <>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Product · Market analysis</p>
        <h1>Explore a product&apos;s market fit</h1>
        <p>Choose a catalog product and a target market to build a structured planning report.</p>
      </header>
      <div className={styles.layout}>
        <section className={styles.panel} aria-labelledby="analysis-form-title">
          <h2 id="analysis-form-title">Set the context</h2>
          <p className={styles.muted}>Product and country are required.</p>
          {catalog.status === "loading" && <p role="status">Loading products…</p>}
          {catalog.status === "error" && (
            <div>
              <p className={styles.error} role="alert">{catalog.message}</p>
              <button className={styles.secondaryButton} onClick={retryCatalog}>Retry catalog</button>
            </div>
          )}
          {catalog.status === "ready" && !products.length && (
            <div>
              <p role="status">No products are available.</p>
              <button className={styles.secondaryButton} onClick={retryCatalog}>Reload catalog</button>
            </div>
          )}
          <form
            onSubmit={submit}
            onChange={() => { if (!inFlight.current) setAnalysis({ status: "idle" }) }}
            noValidate
          >
            <fieldset className={styles.fields} disabled={!catalogReady || submitting}>
              <label htmlFor="analysis-product">Product</label>
              <select id="analysis-product" value={productId} onChange={(e) => setProductId(e.target.value)} required>
                <option value="">Select a product</option>
                {products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}
              </select>
              <label htmlFor="analysis-country">Country</label>
              <input id="analysis-country" value={country} onChange={(e) => setCountry(e.target.value)} required />
              <label htmlFor="analysis-audience">Target audience <span>(optional)</span></label>
              <input id="analysis-audience" value={targetAudience} onChange={(e) => setTargetAudience(e.target.value)} />
              <label htmlFor="analysis-notes">Market notes <span>(optional)</span></label>
              <textarea id="analysis-notes" rows={4} value={marketNotes} onChange={(e) => setMarketNotes(e.target.value)} />
              <button className={styles.submitButton} type="submit" disabled={!canSubmit}>
                {submitting ? "Analyzing…" : "Analyze product"}
              </button>
            </fieldset>
          </form>
          <p className={styles.status} role="status" aria-live="polite">
            {submitting ? "Analyzing your selected product…" : analysis.status === "success" ? "Analysis complete." : ""}
          </p>
          {analysis.status === "error" && <p className={styles.error} role="alert">{analysis.message}</p>}
        </section>
        <section className={`${styles.panel} ${styles.report}`} aria-labelledby="analysis-result-title" aria-busy={submitting}>
          <h2 id="analysis-result-title">Analysis report</h2>
          {analysis.status === "success" ? (
            <>
              <AnalysisReport result={analysis.result} />
              <ContentPlanSection request={{ ...analysis.request, analysis: analysis.result }} />
            </>
          ) : (
            <p className={styles.muted}>
              {submitting ? "Your report is being prepared." : "Submit a product and market to see the recommendation, strengths, risks and suggested directions."}
            </p>
          )}
        </section>
      </div>
    </>
  )
}
