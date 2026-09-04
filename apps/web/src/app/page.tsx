import type { Metadata } from "next"
import Link from "next/link"
import { Suspense } from "react"

import { FeaturedProducts, HeroExample } from "@/features/landing/CatalogShowcase"
import styles from "./page.module.css"

// Stream catalog sections separately so the introduction never waits for the API.
export const dynamic = "force-dynamic"

export const metadata: Metadata = {
  title: "Local roots. New horizons. | liuliangchuhai",
  description: "Explore ASEAN market possibilities for Chinese local products with an AI-assisted market strategy demo.",
}

const steps = [
  ["Select Product", "Start with a local specialty. Get to know its origins, ingredients, and cultural story."],
  ["Analyze Market", "Choose an ASEAN market and an audience to explore positioning, opportunities, and risks."],
  ["Generate Strategy", "Turn the analysis into a content plan, from a social caption to a short video concept."],
]

const outputs = [
  ["Market recommendation", "A starting point for exploring fit, strengths, and risks."],
  ["Customer segments", "Audience context to focus your market exploration."],
  ["Cultural positioning", "The local story and traditions behind your product."],
  ["Marketing suggestions", "Suggested directions to consider in your planning."],
  ["Content directions", "Ideas for social captions, product imagery, and video."],
]

export default function Home() {
  return (
    <div className={styles.landing}>
      <a className={styles.skipLink} href="#main-content">Skip to content</a>
      <header className={styles.navigation}>
        <Link href="/" className={styles.brand} aria-label="liuliangchuhai home">
          <span className={styles.brandMark} aria-hidden="true">↗</span>
          <span>liuliangchuhai<span className={styles.brandCaption}>LOCAL ROOTS. NEW HORIZONS.</span></span>
        </Link>
        <nav aria-label="Main navigation">
          <Link className={styles.navProducts} href="/products">Products</Link>
          <Link className={styles.navAction} href="/analysis">Start Analysis <span aria-hidden="true">↗</span></Link>
        </nav>
      </header>
      <main id="main-content" className={styles.main}>
        <section className={styles.hero} aria-labelledby="hero-title">
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}><span className={styles.dot} /> AI-ASSISTED MARKET STRATEGY · DEMO</p>
            <h1 id="hero-title">Chinese products.<br /><em>ASEAN</em><br />possibilities.</h1>
            <p className={styles.intro}>Turn local products from Guangxi, China into new market possibilities with AI-assisted analysis and content strategy.</p>
          </div>
          <div className={styles.heroVisual}>
            <Suspense fallback={<div className={styles.visualLoading} role="status">Local roots. New horizons.<span>Loading a catalog example…</span></div>}>
              <HeroExample />
            </Suspense>
          </div>
          <div className={styles.heroActions}>
            <div className={styles.actions}>
              <Link className={styles.primary} href="/analysis">Start Analysis <span aria-hidden="true">↗</span></Link>
              <Link className={styles.secondary} href="/products">Explore Products <span aria-hidden="true">→</span></Link>
            </div>
            <p className={styles.heroNote}>A product story. A new market. A place to begin.</p>
          </div>
        </section>
        <section className={styles.workflow} aria-labelledby="workflow-title">
          <div className={styles.sectionHeading}>
            <p className={styles.eyebrow}>THE JOURNEY</p>
            <h2 id="workflow-title">From local roots to new markets.</h2>
          </div>
          <ol className={styles.steps}>
            {steps.map(([title, description], index) => (
              <li key={title}>
                <span className={styles.stepNumber}>0{index + 1}</span>
                <div><h3>{title}</h3><p>{description}</p></div>
              </li>
            ))}
          </ol>
        </section>
        <section className={styles.featured} aria-labelledby="featured-title">
          <div className={styles.featuredHeading}>
            <div className={styles.sectionHeading}>
              <p className={styles.eyebrow}>ROOTED IN GUANGXI</p>
              <h2 id="featured-title">Small origins. Big stories.</h2>
              <p>Explore featured products, handpicked for this demo.</p>
            </div>
            <Link className={styles.textLink} href="/products">Explore all products <span aria-hidden="true">↗</span></Link>
          </div>
          <Suspense fallback={<div className={styles.catalogState} role="status">Loading featured products…</div>}>
            <FeaturedProducts />
          </Suspense>
        </section>
        <section className={styles.outputs} aria-labelledby="outputs-title">
          <div className={styles.outputIntro}>
            <p className={styles.eyebrow}>BEYOND THE FIRST IDEA</p>
            <h2 id="outputs-title">A clearer direction.<br /><em>A creative starting point.</em></h2>
            <p>Explore the shape of a market strategy, then take it into a content plan.</p>
            <p className={styles.demoNote}>This demo uses sample outputs to show the workflow. Market assumptions still need validation; some analysis fields may be empty.</p>
          </div>
          <ul className={styles.outputList}>
            {outputs.map(([title, description], index) => (
              <li key={title}>
                <span aria-hidden="true">0{index + 1}</span>
                <div><h3>{title}</h3><p>{description}</p></div>
                <span className={styles.outputArrow} aria-hidden="true">↗</span>
              </li>
            ))}
          </ul>
        </section>
        <section className={styles.finalCta} aria-labelledby="cta-title">
          <p className={styles.eyebrow}>YOUR NEXT CHAPTER</p>
          <h2 id="cta-title">Ready to explore new markets?</h2>
          <p>Start with a product. Discover where its story could go.</p>
          <Link className={styles.primary} href="/analysis">Start Demo <span aria-hidden="true">↗</span></Link>
        </section>
      </main>
      <footer className={styles.footer}>
        <span>liuliangchuhai <span className={styles.footerChinese}>流量出海</span></span>
        <span>Guangxi, China <span aria-hidden="true">→</span> ASEAN markets</span>
        <span>An AI-assisted strategy demo</span>
      </footer>
    </div>
  )
}
