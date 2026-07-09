import { expect, test } from "@playwright/test";

test("home dashboard smoke test", async ({ page }) => {
  const response = await page.goto("/");
  expect(response?.status()).toBe(200);

  await expect(page.getByRole("heading", { name: "Flask API 요청/응답 연결" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "사건 목록" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "선택 사건" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "AI 분석 결과" })).toBeVisible();

  await expect(page.getByRole("button", { name: /evt-001/ })).toBeVisible();

  const apiErrorNotice = page.getByText("API 연결 실패: mock 사건을 표시합니다.");
  const firstEventMessage = page.getByText("환불 처리 지연 문의");
  await expect(apiErrorNotice.or(firstEventMessage)).toBeVisible();

  await page.getByRole("button", { name: /evt-002/ }).click();
  await expect(page.getByText("픽업 대기 시간 문의")).toBeVisible();
});
