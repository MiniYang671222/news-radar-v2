---
name: create-repo
description: 用 GitHub CLI（gh）將目前的專案發布到 GitHub——建立與專案資料夾同名的公開儲存庫、綁定為遠端 origin，並推送現有的提交。當使用者要求建立 GitHub 儲存庫、把專案發布或推上 GitHub 時使用。
---

# Create Repo（發布專案到 GitHub）

把使用者目前所在的專案資料夾發布到 GitHub：在 GitHub 上建立同名的公開儲存庫（repository）、綁定成本機的遠端 `origin`，並把現有的提交推送上去。

## 前置檢查

執行前先確認三件事；任何一項不成立就停下來告訴使用者，避免自行補救：

1. 目前資料夾已經是 Git 儲存庫，而且至少有一筆提交（`git log --oneline`）；還沒初始化或還沒提交，請使用者先完成那一步。
2. gh 已經登入（`gh auth status`）。
3. 這個專案還沒綁定過遠端（`git remote -v` 應該是空的）；已經綁定過就直接回報，不要重建。

## 執行步驟

1. 儲存庫名稱使用「專案資料夾的名字」——和本機同名，之後對照起來最不容易搞混。
2. 把即將執行的指令列給使用者確認，使用者確認之前不要執行：

   ```
   gh repo create 資料夾名稱 --source . --public --push
   ```

   - `--source .`：用目前這個資料夾當作來源，gh 會順便把新儲存庫綁定成本機的遠端 `origin`。
   - `--public`：建成公開儲存庫；免費帳號要在公開儲存庫上才能使用 GitHub Pages。
   - `--push`：建立並綁定完成後，把本機目前的提交推送上去。
3. 使用者確認後執行，回報建立好的儲存庫網址。

## 不要做

以下的事不在這個 skill 的範圍內。儲存庫建好、回報完網址，這次任務就結束了，下一步等使用者開口：

- 不要開啟 GitHub Pages、不要開分支、不要發拉取請求。
- 不要主動建立或修改任何檔案（README、.gitignore 都不要自行新增）。
- 只執行這些指令：`git log`、`git remote -v`、`git status`、`gh auth status`、`gh repo create`、`gh repo view`。清單以外的 git／gh 指令一律不執行。
