// Catalog image sources are either an absolute http(s) URL or a root-relative
// path served from apps/web/public. Anything else (protocol-relative hosts,
// backslash variants, javascript:/data: URLs, bare relative paths) stays
// unusable so the surrounding component keeps rendering its placeholder.
const absoluteHttp = /^https?:\/\//i
const rootRelative = /^\/(?![/\\])/

export function isUsableImageSource(src?: string): src is string {
  if (!src) return false
  return absoluteHttp.test(src) || rootRelative.test(src)
}
