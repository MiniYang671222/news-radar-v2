---
name: setup-dashboard
description: 把一個網頁專案（儀表板系列）從「檔案已經就位、還沒有版本控制」一路帶到「已推上 GitHub、網站上線、main 受規則集保護」的狀態——依序交給 create-commit-v2、create-repo、create-pages 完成，初始化與規則集自行處理，最後走一次拉取請求（PR）流程驗收。當使用者要求「把這個儀表板專案設定起來」「把這個網頁專案從頭設定到上線」「重建這週的環境」等整段流程時使用；使用者只要求其中單獨一步（例如只想提交、只想發布）時不要用這個 skill，交給對應的單一 skill。雷達類專案請改用 setup-radar。
---

# Setup Dashboard（把儀表板專案立起來）

把使用者目前所在的網頁專案資料夾，從「只有檔案、沒有版本控制」帶到「已經在 GitHub 上、網站上線、`main` 受保護」的狀態。

這個 skill 和 `setup-radar` 是同一種東西，用的也是同一批零件，但流程不一樣。三個差別：

1. **會開 GitHub Pages。**這種專案的產物是一個給人看的網站。
2. **直接建立規則集，不問。**這種專案是「人來改、機器檢查」的，規則集該設。
3. **最後會走一次拉取請求（PR）流程當驗收。**這種專案的改動由人發動，所以要確認那條路真的通。

## 這個 skill 怎麼運作

1. 這個 skill 自己**幾乎不執行** git 與 gh 指令。它負責的是順序：每一段交給對應的 skill 去做，做完接下一段。
2. 會用到的 skills：`create-commit-v2`、`create-repo`、`create-pages`。收尾的驗收流程另外會用到 `create-branch-v2`、`open-pr`、`merge-pr`。
3. 其中兩段沒有現成的 skill——初始化版本控制與建立規則集——由這個 skill 自己處理。
4. **每一段結束都要回報結果，等使用者放行才進入下一段。**使用者隨時可以喊停，也可以指定跳過某一段。

## 前置檢查

執行前先確認四件事；任何一項不成立就停下來告訴使用者，避免自行補救：

1. 使用者目前所在的資料夾就是這次要建立的專案。把完整路徑與現有檔案列給他確認。
2. 這個資料夾還沒有版本控制（沒有 `.git`）。已經有了就停下來回報，不要重新初始化。
3. gh 已經登入（`gh auth status`）。
4. Git 的全域 `user.name` 與 `user.email` 都有值。缺任何一項就停下來請使用者補上，不要自己代填。

## 第一段：初始化版本控制

這一段沒有對應的 skill，自己做。

1. 把即將執行的兩行指令列給使用者確認，使用者確認之前不要執行：

   ```
   git init
   ```

   ```
   git branch -M main
   ```

2. 執行後回報目前的分支名稱，應該是 `main`。

## 第二段：第一個提交

1. 交給 `create-commit-v2`，由它產生符合課程格式的提交訊息。
2. 專案裡的檔案是使用者事先放好的。**不要替他新增、修改或刪除任何檔案**，包括 README 與 `.gitignore`。

## 第三段：發布到 GitHub

交給 `create-repo`。儲存庫名稱依它的規範，用專案資料夾的名字。

## 第四段：開啟 GitHub Pages（有條件）

1. 先看專案根目錄有沒有 `index.html`。
2. **有**：交給 `create-pages`，等它回報網站網址。
3. **沒有**：跳過這一段，並告訴使用者跳過的原因——這個專案不會產生網頁，不需要 Pages。不要為了開 Pages 而替他建一個 `index.html`。

## 第五段：保護 main 分支（規則集）

規則集沒有對應的 skill，這一段也自己做。

1. 設定內容固定如下，寫成一個暫存的 JSON 檔，**放在專案資料夾以外的地方**（避免被一起提交）：

   ```json
   {
     "name": "protect-main",
     "target": "branch",
     "enforcement": "active",
     "conditions": {
       "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
     },
     "rules": [
       {
         "type": "pull_request",
         "parameters": {
           "required_approving_review_count": 0,
           "dismiss_stale_reviews_on_push": false,
           "require_code_owner_review": false,
           "require_last_push_approval": false,
           "required_review_thread_resolution": false
         }
       },
       { "type": "deletion" },
       { "type": "non_fast_forward" }
     ]
   }
   ```

   - `"required_approving_review_count"` 固定是 `0`：這門課的儲存庫只有使用者一個人，設成 `1` 會沒有人能核准他自己的拉取請求（PR），他會被鎖在外面。
   - 四個 `false` 是網頁設定畫面上那幾個沒有勾選的核取方塊，寫出來只是為了讓設定完整。
2. 把指令與上面整份 JSON 內容都列給使用者確認，使用者確認之前不要執行：

   ```
   gh api --method POST repos/{owner}/{repo}/rulesets --input 暫存檔路徑
   ```

   - `{owner}` 與 `{repo}` 是佔位符（placeholder），gh 會自動填入目前資料夾對應的儲存庫，不需要代換。
3. 執行後刪掉暫存檔，並用 `gh api repos/{owner}/{repo}/rulesets` 查一次，回報規則集的名稱與強制狀態。
4. **不要加入狀態檢查（`required_status_checks`）。**這個時間點還沒有任何檢查跑過，加了也選不到；那是後面的課程要做的事。

## 第六段：走一次完整流程（驗收）

1. 這一段是驗收，不是練習：確認「一筆改動能不能經過拉取請求正常進到 `main`」這條路真的通。
2. 先問使用者這次要做的改動是什麼，一句話就好。**他沒有指定就停在這裡**——第五段結束本身就是一份完整的交付。
3. 使用者說了改動內容之後，依序：
   - 交給 `create-branch-v2` 開工作分支。
   - **停下來**，請使用者自己修改檔案。改好、存檔、告訴你之後才繼續，不要替他改。
   - 交給 `create-commit-v2` 提交。
   - 交給 `open-pr` 發拉取請求，然後停下來請使用者自己看過 PR 的內容。
   - 使用者說確認過了，才交給 `merge-pr` 合併收尾。
4. 第四段有開 Pages 的話，最後請 `create-pages` 查一次建置狀態，確認網站跟著更新了。

## 回報

流程走完、或使用者中途喊停時，列出這次完成了哪幾段、跳過哪幾段，以及三項結果：儲存庫網址、網站網址（有開 Pages 的話）、目前所在的分支。

## 不要做

以下的事不在這個 skill 的範圍內：

- 不要繞過那幾個 skill 自己下 git／gh 指令。該由誰做就由誰做——初始化與規則集是唯二的例外，因為它們沒有對應的 skill。
- 不要建立或修改任何 workflow 檔案。那是 `write-workflow` 的事，也不屬於「把專案立起來」的範圍。
- 不要主動建立或修改專案裡的任何檔案。檔案由使用者事先放好，這個 skill 只負責把它們送上去。
- 不要一口氣跑完全部。每一段結束都停下來回報，等使用者放行——使用者要的是看得懂每一步，不是快。
- 第六段的改動內容不要自己想一個來做。使用者沒指定就停下來。
