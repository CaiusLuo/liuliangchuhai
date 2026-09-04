# Content Plan Contract

`ContentContext` is immutable and contains a required nonblank `target_language`.
`ContentGenerationPlan` is immutable and contains a nonempty tuple of nonblank
`key_selling_points` plus nonblank `image_prompt`, `short_video_idea`,
`short_video_prompt`, `live_script`, and `social_caption` strings. It is material
for downstream tools, not generated media.

`ContentPlannerPort.create_content_plan(product, market, analysis, context)` is
the application-owned async capability. `CreateContentPlanUseCase` forwards the
four supplied objects unchanged and returns the port result unchanged. The
contract introduces no provider controls or provider-specific types.
