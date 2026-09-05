import assert from "node:assert/strict"
import { afterEach, test } from "node:test"

import { assistantActionHref } from "./navigation.ts"
import {
  AssistantApiError, assistantErrorMessage, createAssistantRequest, replyToAssistant,
} from "../../api/assistant.ts"

const originalFetch = globalThis.fetch
const originalBaseUrl = process.env.NEXT_PUBLIC_API_URL

afterEach(() => {
  globalThis.fetch = originalFetch
  if (originalBaseUrl === undefined) delete process.env.NEXT_PUBLIC_API_URL
  else process.env.NEXT_PUBLIC_API_URL = originalBaseUrl
})

test("semantic actions map to existing routes and encode the complete product ID", () => {
  const product_id = "tea /?#"
  assert.equal(assistantActionHref({ type: "view_product", product_id }), "/products/tea%20%2F%3F%23")
  assert.equal(assistantActionHref({ type: "start_analysis", product_id }), "/analysis?product_id=tea%20%2F%3F%23")
})

test("request construction sends canonical ID only in product context", () => {
  assert.deepEqual(createAssistantRequest("Question", "tea"), { message: "Question", product_id: "tea" })
  assert.deepEqual(createAssistantRequest("Question"), { message: "Question" })
})

for (const productId of [undefined, "wuzhou-liubao-tea"]) {
  test(`HTTP request contains only the current message (context: ${productId})`, async () => {
    process.env.NEXT_PUBLIC_API_URL = "https://demo.example/api/"
    const reply = { message: "Answer", suggested_action: null }
    globalThis.fetch = async (url, options) => {
      assert.equal(url, "https://demo.example/api/assistant/chat")
      assert.equal(options.method, "POST")
      assert.equal(options.headers["Content-Type"], "application/json")
      assert.ok(options.signal instanceof AbortSignal)
      assert.deepEqual(JSON.parse(options.body), createAssistantRequest("Current question", productId))
      return Response.json(reply)
    }
    assert.deepEqual(await replyToAssistant({
      ...createAssistantRequest("Current question", productId),
      messages: [{ role: "user", content: "Previous question" }],
      product: { name: "Client-created data" },
    }), reply)
  })
}

for (const status of [404, 422, 502, 503, 500]) {
  test(`HTTP ${status} has a stable public error without backend details`, async () => {
    globalThis.fetch = async () => new Response("private backend diagnostic", { status })
    await assert.rejects(() => replyToAssistant({ message: "Question" }), {
      name: "AssistantApiError", message: assistantErrorMessage,
    })
  })
}

for (const failure of [
  () => { throw new Error("private network error") },
  () => { throw new DOMException("private timeout", "TimeoutError") },
  () => new Response("not JSON"),
]) {
  test("transport and JSON failures are normalized", async () => {
    globalThis.fetch = async () => failure()
    await assert.rejects(() => replyToAssistant({ message: "Question" }), (error) => {
      assert.ok(error instanceof AssistantApiError)
      assert.equal(error.message, assistantErrorMessage)
      return true
    })
  })
}

test("blank messages do not send a request", async () => {
  globalThis.fetch = async () => assert.fail("must not fetch")
  await assert.rejects(() => replyToAssistant({ message: " \n\t" }), AssistantApiError)
})
