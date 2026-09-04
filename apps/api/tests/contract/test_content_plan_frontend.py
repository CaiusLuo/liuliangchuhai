import subprocess
from pathlib import Path


def test_frontend_adapter_preserves_analysis_and_masks_failures(tmp_path: Path) -> None:
    web = Path(__file__).resolve().parents[4] / "apps/web"
    compiled = subprocess.run(
        [
            "pnpm",
            "exec",
            "tsc",
            "--strict",
            "--skipLibCheck",
            "--target",
            "ES2020",
            "--module",
            "commonjs",
            "--outDir",
            str(tmp_path),
            "src/api/content-plan.ts",
        ],
        cwd=web,
        capture_output=True,
        text=True,
        check=False,
    )
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    script = tmp_path / "adapter.cjs"
    script.write_text(
        """
const assert = require('node:assert/strict');
const { createContentPlan, ContentPlanApiError } = require('./content-plan.js');
const request = {
  product_id: 'luosifen', country: 'Vietnam', target_audience: null, market_notes: 'Notes',
  target_language: ' English ',
  analysis: {
    recommendation: 'caution', score: 50, summary: 'Supplied analysis', target_audiences: [],
    strengths: ['Strength'], risks: [], cultural_advantages: [],
    marketing_suggestions: [], content_directions: ['Direction'],
  },
};
const result = {
  key_selling_points: ['Point'], image_prompt: 'Image', short_video_idea: 'Idea',
  short_video_prompt: 'Video', live_script: 'Live', social_caption: 'Social',
};
(async () => {
  process.env.NEXT_PUBLIC_API_URL = 'http://test';
  let calls = 0;
  global.fetch = async (url, options) => {
    calls++;
    assert.equal(url, 'http://test/content-plan');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(options.body), { ...request, target_language: 'English' });
    return { ok: true, json: async () => result };
  };
  assert.deepEqual(await createContentPlan(request), result);
  assert.equal(calls, 1);
  assert.equal(request.target_language, ' English ');
  await assert.rejects(createContentPlan({ ...request, target_language: ' ' }), {
    name: 'ContentPlanApiError', message: 'Please enter a target language.',
  });
  assert.equal(calls, 1);
  for (const [status, message] of [
    [404, 'The selected product is no longer available.'],
    [422, 'Please check the content planning inputs.'],
    [500, 'Unable to create content plan. Please try again.'],
    [502, 'Unable to create content plan. Please try again.'],
  ]) {
    global.fetch = async () => ({
      ok: false, status, json: async () => ({ message: 'private provider secret' }),
    });
    await assert.rejects(createContentPlan(request), { name: 'ContentPlanApiError', message });
  }
  for (const broken of [
    async () => { throw Error('private network diagnostic'); },
    async () => ({ ok: true, json: async () => { throw Error('private invalid JSON'); } }),
  ]) {
    global.fetch = broken;
    await assert.rejects(createContentPlan(request), error =>
      error instanceof ContentPlanApiError &&
      error.message === 'Unable to create content plan. Please try again.');
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["node", str(script)],
        cwd=web,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
