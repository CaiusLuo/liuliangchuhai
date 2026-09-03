import { getHealth } from "@/api/health"

export default async function Home() {
  const health = await getHealth()

  return (
    <main>
      <p className="eyebrow">Phase 0</p>
      <h1>liuliangchuhai</h1>
      <p>Architecture and provider contracts are ready for later feature work.</p>
      <dl>
        <div>
          <dt>API</dt>
          <dd>{health?.status ?? "unavailable"}</dd>
        </div>
        <div>
          <dt>LLM provider</dt>
          <dd>{health?.providers.llm.provider ?? "unavailable"}</dd>
        </div>
        <div>
          <dt>Digital-human provider</dt>
          <dd>{health?.providers.digital_human.provider ?? "unavailable"}</dd>
        </div>
      </dl>
    </main>
  )
}
