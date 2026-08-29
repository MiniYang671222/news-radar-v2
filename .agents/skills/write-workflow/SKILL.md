---
name: write-workflow
description: 使用者要建立或修改 GitHub Actions 的 workflow 檔案時使用。涵蓋新增 workflow、加步驟、改觸發事件等需求。產出一律先列出完整檔案內容給使用者確認，再寫入檔案。
---

# 撰寫 workflow

幫使用者建立或修改 `.github/workflows/` 下方的 workflow 檔案，遵守本課程的固定規範。

## 課程規範

- 檔案一律放在 `.github/workflows/` 下方，副檔名用 `.yml`。
- 縮排一律兩個空格，不用 Tab。
- `runs-on` 一律用 `ubuntu-latest`。
- 用到現成積木（`uses`）時一律指定版本，例如 `actions/checkout@v7`。
- 執行指令的步驟若不只一個，每個步驟都加上簡短的中文 `name`。
- 觸發事件沒特別指定時，預設用 `on: push`。
- 不主動加入使用者沒要求的步驟或事件。

## 執行步驟

1. 先確認需求：要新建檔案還是修改現有檔案；修改的話，先讀現有內容。
2. 組出完整的檔案內容，**整份列出來給使用者確認**，並用一兩句話說明每個步驟在做什麼。
3. 使用者同意後才寫入檔案。
4. 寫入後提醒使用者：建立提交、推上去之後，到 Actions 分頁確認執行結果。

## 不要做

- 不執行任何 `git` 或 `gh` 指令（提交交給 create-commit-v2、推送與 PR 交給 open-pr）。
- 不修改 `.github/workflows/` 以外的任何檔案。
- 不使用 `secrets` 以外的 `${{ }}` 進階語法，除非使用者主動要求。
- 使用者沒確認前，不寫入任何內容。
