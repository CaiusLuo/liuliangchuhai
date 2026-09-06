import assert from "node:assert/strict"
import { test } from "node:test"

import { isUsableImageSource } from "./image-source.ts"

test("absolute http(s) sources stay usable regardless of case", () => {
  for (const src of [
    "https://example.invalid/noodle.jpg",
    "http://example.invalid/tea.png",
    "HTTPS://example.invalid/egg.jpg",
  ]) {
    assert.equal(isUsableImageSource(src), true, src)
  }
})

test("root-relative demo assets are usable", () => {
  for (const src of [
    "/products/liuzhou-luosifen.svg",
    "/products/qinzhou-nixing-pottery.svg",
  ]) {
    assert.equal(isUsableImageSource(src), true, src)
  }
})

test("a missing or empty source is never usable", () => {
  for (const src of [undefined, ""]) {
    assert.equal(isUsableImageSource(src), false, String(src))
  }
})

test("sources that leave the origin or carry a foreign scheme are rejected", () => {
  for (const src of [
    "//example.invalid/tea.jpg",
    "/\\example.invalid/tea.jpg",
    "javascript:alert(1)",
    "data:image/svg+xml,<svg/>",
    "products/liuzhou-luosifen.svg",
    " /products/liuzhou-luosifen.svg",
  ]) {
    assert.equal(isUsableImageSource(src), false, src)
  }
})
