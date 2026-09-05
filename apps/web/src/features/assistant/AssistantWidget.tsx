"use client"

import Link from "next/link"
import { useEffect, useRef, useState } from "react"

import { assistantErrorMessage, createAssistantRequest, replyToAssistant } from "@/api/assistant"
import type { AssistantSuggestedAction } from "@/api/assistant"
import type { AssistantProduct } from "./AssistantProvider"
import { assistantActionHref } from "./navigation"
import styles from "./assistant.module.css"

type ChatMessage = {
  role: "user" | "assistant"
  content: string
  suggestedAction?: AssistantSuggestedAction
}

export function AssistantWidget({ product, conversationKey }: {
  product: AssistantProduct | null
  conversationKey: string
}) {
  const [open, setOpen] = useState(false)
  const launcher = useRef<HTMLButtonElement>(null)
  function close() {
    setOpen(false)
    launcher.current?.focus({ preventScroll: true })
  }

  return (
    <aside lang="zh-CN" aria-label="商品助手" className={styles.widget}
      onKeyDown={(event) => {
        if (event.key === "Escape" && open) {
          event.stopPropagation()
          close()
        }
      }}>
      <section id="assistant-panel" role="dialog" aria-modal="false" aria-labelledby="assistant-title"
        aria-describedby="assistant-scope" hidden={!open} className={styles.panel}>
        <header className={styles.header}>
          <div>
            <p className={styles.eyebrow}>GUANGXI · PRODUCT GUIDE</p>
            <h2 id="assistant-title">桂品 AI 助手</h2>
            <p className={styles.subtitle}>了解商品 · 文化背景 · 出海分析</p>
          </div>
          <button type="button" className={styles.close} onClick={close} aria-label="收起助手">×</button>
        </header>
        <p id="assistant-scope" className={styles.scope}>仅提供当前 Demo 商品及跨境展示相关咨询</p>
        {product && <p className={styles.context}>当前商品 · {product.name}</p>}
        <Conversation key={conversationKey} product={product} open={open} onNavigate={close} />
      </section>
      <button ref={launcher} className={styles.launcher} type="button"
        aria-label={open ? "收起桂品 AI 助手" : "打开桂品 AI 助手"}
        aria-expanded={open} aria-controls="assistant-panel"
        onClick={() => open ? close() : setOpen(true)}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M5 4h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 3v-3a2 2 0 0 1-2-2V7a3 3 0 0 1 3-3Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
          <path d="M7 9h10M7 13h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
        <span>AI</span>
      </button>
    </aside>
  )
}

function Conversation({ product, open, onNavigate }: {
  product: AssistantProduct | null
  open: boolean
  onNavigate: () => void
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [failedMessage, setFailedMessage] = useState<string | null>(null)
  const inFlight = useRef(false)
  const mounted = useRef(true)
  const inputRef = useRef<HTMLInputElement>(null)
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    mounted.current = true
    return () => { mounted.current = false }
  }, [])
  useEffect(() => {
    if (open) inputRef.current?.focus({ preventScroll: true })
  }, [open])
  useEffect(() => {
    if (open && logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [messages, sending, failedMessage, open])

  async function submit(value: string, retry = false) {
    const message = value.trim()
    if (!message || inFlight.current) return
    inFlight.current = true
    setSending(true)
    setFailedMessage(null)
    if (!retry) {
      setMessages((previous) => [...previous, { role: "user", content: message }])
      setInput("")
    }
    try {
      const reply = await replyToAssistant(createAssistantRequest(message, product?.id))
      if (!mounted.current) return
      setMessages((previous) => [...previous, {
        role: "assistant", content: reply.message,
        suggestedAction: reply.suggested_action ?? undefined,
      }])
    } catch {
      if (mounted.current) setFailedMessage(message)
    } finally {
      inFlight.current = false
      if (mounted.current) setSending(false)
    }
  }

  const prompts = product
    ? ["这个商品有什么特点？", "有什么文化背景？", "适合进入哪些海外市场？"]
    : ["你能帮我了解哪些商品？", "如何了解商品文化背景？", "如何开始出海分析？"]

  return (
    <>
      <div ref={logRef} className={styles.conversation}>
        {messages.length === 0 && <div className={styles.empty}>
          <span className={styles.welcomeMark} aria-hidden="true">桂</span>
          <h3>从一个小问题开始</h3>
          <p>{product ? "一起了解这件广西特色商品。" : "浏览广西特色商品，发现它们的文化与可能性。"}</p>
          <div className={styles.prompts}>
            {prompts.map((prompt) => <button key={prompt} type="button" onClick={() => void submit(prompt)}
              disabled={sending}>{prompt}<span aria-hidden="true">↗</span></button>)}
          </div>
        </div>}
        <div role="log" aria-label="助手对话" aria-live="polite" aria-relevant="additions" className={styles.messages}>
          {messages.map((message, index) => <div key={index}
            className={message.role === "user" ? styles.userMessage : styles.assistantMessage}>
            <span className={styles.role}>{message.role === "user" ? "你" : "桂品 AI 助手"}</span>
            <p>{message.content}</p>
            {message.suggestedAction && <Link className={styles.action}
              href={assistantActionHref(message.suggestedAction)} onClick={onNavigate}>
              {message.suggestedAction.type === "view_product" ? "查看商品" : "开始出海分析"}
              <span aria-hidden="true">↗</span>
            </Link>}
          </div>)}
        </div>
        {sending && <p role="status" className={styles.thinking}>AI 正在思考...</p>}
        {failedMessage && <div role="alert" className={styles.error}>
          <p>{assistantErrorMessage}</p>
          <button type="button" onClick={() => void submit(failedMessage, true)} className={styles.retry}>重试</button>
        </div>}
      </div>
      <form className={styles.composer} onSubmit={(event) => { event.preventDefault(); void submit(input) }}>
        <label htmlFor="assistant-input">想了解什么？</label>
        <div className={styles.inputRow}>
          <input ref={inputRef} id="assistant-input" value={input} onChange={(event) => setInput(event.target.value)}
            placeholder="问问商品、文化或出海分析" autoComplete="off"
            onKeyDown={(event) => {
              if (event.key === "Enter" && event.nativeEvent.isComposing) event.preventDefault()
            }} />
          <button className={styles.send} type="submit" disabled={sending || !input.trim()}>发送</button>
        </div>
      </form>
    </>
  )
}
