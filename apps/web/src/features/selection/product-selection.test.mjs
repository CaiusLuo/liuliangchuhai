import assert from "node:assert/strict"
import { test } from "node:test"

import { resolveProductSelection } from "./product-selection.ts"

const products = [{ id: "first" }, { id: "second" }]

test("preselection waits for the canonical catalog and requires an exact match", () => {
  assert.equal(resolveProductSelection([], "first", null), "")
  assert.equal(resolveProductSelection(products, "first", null), "first")
  for (const initialId of ["", "invalid-id", " first "]) {
    assert.equal(resolveProductSelection(products, initialId, null), "")
  }
})

test("manual choices, including clearing the selector, take precedence", () => {
  assert.equal(resolveProductSelection(products, "first", "second"), "second")
  assert.equal(resolveProductSelection(products, "first", ""), "")
  assert.equal(resolveProductSelection([...products], "first", "second"), "second")
  assert.equal(resolveProductSelection(products, "second", ""), "")
})

test("a selection absent from the catalog is never submitted", () => {
  assert.equal(resolveProductSelection(products, "first", "removed"), "")
  assert.equal(resolveProductSelection([], "first", "second"), "")
})
