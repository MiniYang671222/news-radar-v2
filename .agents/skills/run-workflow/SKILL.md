---
name: run-workflow
description: 用 GitHub CLI（gh）手動觸發一個 workflow、等它跑完、回報結果——失敗時把失敗步驟的日誌抓回來並用中文解釋原因。當使用者要求觸發或執行 workflow、跑一次雷達、想知道剛才那次跑得怎麼樣，或想知道最近一次為什麼失敗時使用。
---

# Run Workflow（觸發 workflow 並回報結果）

替使用者手動觸發一個 workflow，等它執行完成，把結果回報清楚。失敗的時候，把失敗步驟的日誌抓回來，用中文說明原因。

這個 skill 做的是「跑起來、看結果」，不改任何檔案。要改 workflow 的內容是 `write-workflow` 的事。

## 前置檢查

執行前先確認兩件事；任何一項不成立就停下來告訴使用者，避免自行補救：

1. gh 已經登入（`gh auth status`）。
2. 目標 workflow 的檔案已經在 GitHub 上的 `main` 分支——還沒推上去，GitHub 那邊就沒有它，觸發會失敗。

## 執行步驟

1. 先確認要跑哪一個。使用者沒指名時，用 `gh workflow list` 把可用的 workflow 列出來請他選，不要自己挑。
2. 只有帶 `workflow_dispatch` 的 workflow 才能手動觸發。目標沒有這個觸發條件時，停下來說明原因，**不要改檔案替他加上去**。
3. 把即將執行的指令列給使用者確認，使用者確認之前不要執行：

   ```
   gh workflow run 檔名.yml
   ```

4. 使用者確認後執行。GitHub 要幾秒才會建立那筆執行紀錄，稍等一下再用 `gh run list --workflow 檔名.yml --limit 1` 取得它的編號。
5. 用 `gh run watch 編號` 等它跑完；中途不要重複觸發。
6. 成功就回報四件事：workflow 名稱、狀態、花了多久，以及執行紀錄裡的輸出重點（例如雷達這次送了幾則通知）。需要完整輸出時用 `gh run view 編號 --log`。
7. 失敗就用 `gh run view 編號 --log-failed` 只抓失敗步驟的日誌。先把原始訊息貼出來，再用中文說明是哪一步、為什麼失敗、建議怎麼修。**先解釋，不要動手改。**

## 只是查結果的情況

使用者若只想知道最近一次跑得怎麼樣，沒有要重新觸發，就跳過第 1 到 4 步：用 `gh run list --limit 5` 找到那一筆，再照第 6、7 步回報。

## 不要做

以下的事不在這個 skill 的範圍內。回報完結果，這次任務就結束了，下一步等使用者開口：

- 不要修改任何檔案，包含 workflow、程式與設定。失敗原因說明白就好，怎麼修由使用者決定。
- 不要建立、修改或刪除 Secrets，也不要把日誌裡出現的權杖或金鑰複述出來。
- 不要提交、推送、開分支、發 PR 或合併。
- 只執行這些指令：`gh auth status`、`gh workflow list`、`gh workflow run`、`gh run list`、`gh run view`、`gh run watch`。清單以外的 git／gh 指令一律不執行。
