import { readFileSync } from "node:fs"
import { expect, test } from "@playwright/test"
import en from "../src/shared/i18n/locales/en/home.json" with { type: "json" }

const fixture = JSON.parse(
  readFileSync(new URL("../../backend/tests/fixtures/catalog-card.json", import.meta.url), "utf8"),
)

test("one action corrects a conflict, survives reload, and undo restores review", async ({
  page,
  context,
}, info) => {
  await context.addInitScript(() => localStorage.setItem("app-locale", "en"))
  await page.goto("/")
  const input = page.getByLabel(en.extraction.inputLabel)
  const run = page.getByRole("button", { name: en.extraction.run })
  const text = `${fixture.conflict}\nOffer ${Date.now()}`
  await input.fill(text)
  await run.click()
  const row = page
    .locator("dl > div")
    .filter({ has: page.getByText(fixture.color, { exact: true }) })
  const accept = page.getByRole("button", {
    name: en.feedback.accept.replace("{{value}}", fixture.white),
    exact: true,
  })
  await expect(accept).toBeVisible()
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: info.outputPath("review.png"), fullPage: true })
  await accept.click()
  await expect(row.getByRole("button", { name: en.feedback.undo })).toBeVisible()
  await page.reload()
  await input.fill(text)
  await run.click()
  await expect(row.getByRole("button", { name: en.feedback.undo })).toBeVisible()
  await row.getByRole("button", { name: en.feedback.undo }).click()
  await expect(accept).toBeVisible()
})

test("manual correction proposes a scoped alias and the next card reuses it", async ({
  page,
  context,
}, info) => {
  await context.addInitScript(() => localStorage.setItem("app-locale", "en"))
  await page.setViewportSize({ width: 375, height: 1000 })
  await page.goto("/")
  const input = page.getByLabel(en.extraction.inputLabel)
  const run = page.getByRole("button", { name: en.extraction.run })
  const text = `${fixture.unknown}\nOffer ${Date.now()}`
  const row = page
    .locator("dl > div")
    .filter({ has: page.getByText(fixture.color, { exact: true }) })
  await input.fill(text)
  await run.click()
  await row.getByRole("button", { name: en.feedback.manual }).click()
  await row.getByLabel(en.feedback.value).fill(fixture.black)
  await row.getByLabel(en.feedback.quote).fill(fixture.aliasQuote)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: info.outputPath("alias-form.png"), fullPage: true })
  await row.getByRole("button", { name: en.feedback.saveLearn }).click()
  await expect(row.getByRole("button", { name: en.feedback.undo })).toBeVisible()
  await input.fill(fixture.nextUnknown)
  await run.click()
  await expect(row.getByText(fixture.black, { exact: true })).toBeVisible()
  await expect(row.getByRole("button", { name: en.feedback.undo })).toHaveCount(0)
  await input.fill(text)
  await run.click()
  await row.getByRole("button", { name: en.feedback.undo }).click()
  await input.fill(fixture.nextUnknown)
  await run.click()
  await expect(row.getByText(en.extraction.states.not_stated)).toBeVisible()
})
