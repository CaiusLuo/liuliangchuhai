import assert from "node:assert/strict"
import { test } from "node:test"

import { featuredProductIds, selectFeaturedProducts } from "./featured-products.ts"

const product = (id) => ({ id })

test("curated products follow configured order, independent of catalog order", () => {
  const catalog = [...featuredProductIds].reverse().map(product)
  const selected = selectFeaturedProducts(catalog)
  assert.deepEqual(selected.map(({ id }) => id), [...featuredProductIds])
  assert.equal(selected[0], catalog[2])
  assert.deepEqual(catalog.map(({ id }) => id), [...featuredProductIds].reverse())
})

test("missing configured IDs are skipped without filling from unrelated products", () => {
  const tea = product(featuredProductIds[0])
  assert.deepEqual(selectFeaturedProducts([product("other"), tea]), [tea])
})

test("no matches falls back to the first three available catalog products", () => {
  const catalog = ["a", "b", "c", "d"].map(product)
  assert.deepEqual(selectFeaturedProducts(catalog), catalog.slice(0, 3))
})

test("a short fallback catalog stays short and an empty catalog stays empty", () => {
  const catalog = [product("a")]
  assert.deepEqual(selectFeaturedProducts(catalog), catalog)
  assert.deepEqual(selectFeaturedProducts([]), [])
})
