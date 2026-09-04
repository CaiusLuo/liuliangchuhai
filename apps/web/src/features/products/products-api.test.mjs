import assert from "node:assert/strict"
import { afterEach, test } from "node:test"

import { getProduct, listProducts, ProductApiError } from "../../api/products.ts"

const originalFetch = globalThis.fetch
const originalBaseUrl = process.env.NEXT_PUBLIC_API_URL

afterEach(() => {
  globalThis.fetch = originalFetch
  if (originalBaseUrl === undefined) delete process.env.NEXT_PUBLIC_API_URL
  else process.env.NEXT_PUBLIC_API_URL = originalBaseUrl
})

test("catalog uses the configured API URL, no cache, and a timeout signal", async () => {
  process.env.NEXT_PUBLIC_API_URL = "https://catalog.example/api/"
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "https://catalog.example/api/products")
    assert.equal(options.cache, "no-store")
    assert.ok(options.signal instanceof AbortSignal)
    return Response.json({ items: [] })
  }
  assert.deepEqual(await listProducts(), { items: [] })
})

test("detail encodes the complete product ID and preserves optional fields", async () => {
  delete process.env.NEXT_PUBLIC_API_URL
  const product = { id: "tea /?#", price: "0", images: [], purchase_url: null }
  globalThis.fetch = async (url) => {
    assert.equal(url, "http://localhost:8000/products/tea%20%2F%3F%23")
    return Response.json(product)
  }
  assert.deepEqual(await getProduct(product.id), product)
})

test("only a detail 404 becomes an absent product", async () => {
  globalThis.fetch = async () => new Response("private backend details", { status: 404 })
  assert.equal(await getProduct("missing"), null)
  await assert.rejects(listProducts, ProductApiError)
})

for (const [scenario, response] of [
  ["HTTP failure", () => new Response("private backend details", { status: 503 })],
  ["invalid JSON", () => new Response("not JSON")],
  ["network failure", () => { throw new Error("private network details") }],
  ["timeout", () => { throw new DOMException("private timeout details", "TimeoutError") }],
]) {
  test(`${scenario} returns a stable safe error for both operations`, async () => {
    globalThis.fetch = async () => response()
    for (const operation of [listProducts, () => getProduct("tea")]) {
      await assert.rejects(operation, (error) => {
        assert.ok(error instanceof ProductApiError)
        assert.equal(error.message, "Unable to load products. Please try again.")
        return true
      })
    }
  })
}
