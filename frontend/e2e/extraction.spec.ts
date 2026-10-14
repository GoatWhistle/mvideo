import { readFileSync } from "node:fs"
import { readFile } from "node:fs/promises"
import AxeBuilder from "@axe-core/playwright"
import { expect, test } from "@playwright/test"
import common from "../src/shared/i18n/locales/en/common.json" with { type: "json" }
import en from "../src/shared/i18n/locales/en/home.json" with { type: "json" }
import ru from "../src/shared/i18n/locales/ru/home.json" with { type: "json" }

const fixture = JSON.parse(
  readFileSync(new URL("../../backend/tests/fixtures/catalog-card.json", import.meta.url), "utf8"),
)

for (const width of [375, 1440]) {
  for (const theme of ["light", "dark"]) {
    for (const locale of ["ru", "en"] as const) {
      test(`extract and export ${width} ${theme} ${locale}`, async ({ page, context }, info) => {
        const copy = locale === "ru" ? ru.extraction : en.extraction
        await page.setViewportSize({ width, height: 1000 })
        await context.addInitScript(
          ({ theme, locale }) => {
            localStorage.setItem("app-theme", theme)
            localStorage.setItem("app-locale", locale)
          },
          { theme, locale },
        )
        await page.goto("/")
        await page.getByLabel(copy.inputLabel).fill(fixture.card)
        await page.getByRole("button", { name: copy.run }).click()
        const downloadButton = page.getByRole("button", { name: copy.export })
        await expect(downloadButton).toBeVisible()
        await expect(page.getByText(fixture.weight, { exact: true })).toBeVisible()
        await expect(page.getByText(fixture.ram, { exact: true })).toBeVisible()
        await page.getByRole("button", { name: fixture.quote, exact: true }).click()
        await expect(page.locator("mark")).toHaveText(fixture.quote)
        expect(
          await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
        ).toBe(true)
        await page.evaluate(() => window.scrollTo(0, 0))
        await page.screenshot({ path: info.outputPath("filled-card.png"), fullPage: true })
        const audit = await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
        expect(
          audit.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })),
        ).toEqual([])
        const downloadPromise = page.waitForEvent("download")
        await downloadButton.click()
        const download = await downloadPromise
        const path = info.outputPath("product-card.json")
        await download.saveAs(path)
        const result = JSON.parse(await readFile(path, "utf8"))
        expect(result.category_id).toBe(761)
        expect(
          result.fields.find(
            (field: { attribute: string }) => field.attribute === fixture.attribute,
          ).value,
        ).toBe(fixture.weight)
        expect(result.fields.every((field: { state: string }) => field.state === "accepted")).toBe(
          true,
        )
      })
    }
  }
}

test("only ambiguous category asks for selection and retry recovers from network failure", async ({
  page,
  context,
}) => {
  await context.addInitScript(() => localStorage.setItem("app-locale", "en"))
  await page.goto("/")
  await page.getByLabel(en.extraction.inputLabel).fill("Samsung Galaxy S26 12/256GB Black")
  await page.getByRole("button", { name: en.extraction.run }).click()
  await expect(page.getByRole("status")).toHaveText(en.extraction.chooseCategory)
  await page.getByRole("button", { name: fixture.category, exact: true }).click()
  await expect(page.getByRole("button", { name: en.extraction.export })).toBeVisible()
  await page.route("**/api/v1/extract/stream", (route) => route.abort())
  await page.getByRole("button", { name: en.extraction.run }).click()
  await expect(page.getByRole("alert")).toBeVisible()
  await page.unroute("**/api/v1/extract/stream")
  await page.getByRole("button", { name: common.action.retry, exact: true }).click()
  await expect(page.getByRole("status")).toHaveText(en.extraction.chooseCategory)
})

test("pending extraction blocks duplicates and cancellation allows a fresh run", async ({
  page,
  context,
}) => {
  await context.addInitScript(() => localStorage.setItem("app-locale", "en"))
  let release: () => void = () => undefined
  const gate = new Promise<void>((resolve) => {
    release = resolve
  })
  let requests = 0
  await page.route("**/api/v1/extract/stream", async (route) => {
    requests += 1
    await gate
    await route.continue()
  })
  await page.goto("/")
  const input = page.getByLabel(en.extraction.inputLabel)
  await input.fill(fixture.card)
  const run = page.getByRole("button", { name: en.extraction.run })
  await run.click()
  await expect(input).toBeDisabled()
  await expect(run).toHaveAttribute("aria-busy", "true")
  await run.dispatchEvent("click")
  expect(requests).toBe(1)
  await page.getByRole("button", { name: en.extraction.cancel }).click()
  await expect(input).toBeEnabled()
  release()
  await page.unrouteAll({ behavior: "wait" })
  await run.click()
  await expect(page.getByRole("button", { name: en.extraction.export })).toBeVisible()
})
