---
name: create-pages
description: 用 GitHub CLI（gh）管理目前專案的 GitHub Pages——開啟（以 main 分支的根目錄為發布來源）、查詢建置狀態與網站網址，或把發布來源切換成 GitHub Actions。當使用者要求開啟 GitHub Pages、讓網站上線、查 Pages 狀態，或要把部署改成由 workflow 執行時使用。
---

# Create Pages（開啟 GitHub Pages）

為目前專案對應的 GitHub 儲存庫開啟 GitHub Pages。發布來源固定為 `main` 分支的根目錄 `/`，開啟後等建置完成，回報網站網址。

## 前置檢查

執行前先確認兩件事；任何一項不成立就停下來告訴使用者，避免自行補救：

1. 這個專案已經綁定 GitHub 遠端（`git remote -v` 看得到 `origin`）；還沒綁定，請使用者先把專案發布到 GitHub。
2. 專案根目錄有 `index.html`（GitHub Pages 認定的網站首頁）；沒有的話先提醒使用者，由他決定要不要繼續。

## 執行步驟

1. Pages 的設定沒有專門的 gh 子指令，用萬用的 `gh api` 直接對 GitHub 發請求。把即將執行的指令列給使用者確認，使用者確認之前不要執行：

   ```
   gh api --method POST repos/{owner}/{repo}/pages -f "source[branch]=main" -f "source[path]=/"
   ```

   - `{owner}` 與 `{repo}` 是佔位符（placeholder），gh 會自動填入目前資料夾對應的儲存庫，不需要代換。
   - `-f "source[branch]=main"` 與 `-f "source[path]=/"`：發布來源固定為 `main` 分支的根目錄。
2. 使用者確認後執行。若回應 `HTTP 409`，代表這個儲存庫的 Pages 已經開啟過，不算失敗，直接進行下一步。
3. 查詢建置狀態：`gh api repos/{owner}/{repo}/pages --jq .status`，顯示 `built` 代表網站已經建好；還在建置（`null` 或 `building`）就稍等再查，查詢幾次仍未完成就如實回報目前狀態，請使用者稍後再問。
4. 查出網站網址並回報：`gh api repos/{owner}/{repo}/pages --jq .html_url`。

## 切換發布來源到 GitHub Actions

使用者若要求把部署改成由自己的 workflow 執行（例如 `deploy.yml`），不要重跑上面的開啟步驟，改走這一段：

1. 把即將執行的指令列給使用者確認，使用者確認之前不要執行：

   ```
   gh api --method PUT repos/{owner}/{repo}/pages -f build_type=workflow
   ```

   - `build_type=workflow`：發布來源從「某一條分支」改成「GitHub Actions 的 workflow」。原本的 `source` 設定不再生效。
2. 執行後用 `gh api repos/{owner}/{repo}/pages --jq .build_type` 確認回傳的是 `workflow`。
3. 回報時提醒使用者兩件事：切換之後 GitHub 不會再自己發布網站，要等 workflow 發布內容；這一步不會觸發部署，網站要等下一次 `deploy.yml` 跑完才更新。
4. 使用者想立刻跑一次部署，那是 `run-workflow` 的事，不要在這裡代跑。

## 只是查狀態的情況

使用者若只是想確認建置狀態或網站網址（例如合併新內容後想知道網站更新了沒），直接執行第 3、4 步的查詢並回報就好，不要重新執行第 1 步的開啟設定。

## 不要做

以下的事不在這個 skill 的範圍內。Pages 開好、回報完網址，這次任務就結束了，下一步等使用者開口：

- 不要修改任何檔案、不要提交、不要推送。
- 不要更改 Pages 以外的任何儲存庫設定。
- 只執行這些指令：`git remote -v`、`gh auth status`，以及僅限 `repos/{owner}/{repo}/pages` 這個位置的 `gh api` 開啟、切換與查詢。清單以外的 git／gh 指令一律不執行。
