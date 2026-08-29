---
name: setup-radar
description: 把一個檔案已經就位的雷達專案（news-radar 系列）帶到「已經推上 GitHub、可以開始運作」的狀態——先檢查檔案結構，再依序交給 create-commit-v2 與 create-repo，最後視情況建立分支規則集。當使用者要求把雷達專案設定起來、發布雷達專案、重建這週的雷達環境時使用；一般的網頁專案請改用 setup-dashboard。
---

# Setup Radar（把雷達專案立起來）

把使用者目前所在的雷達專案資料夾，從「只有檔案、沒有版本控制」帶到「已經在 GitHub 上、workflow 開始運作」的狀態。

這個 skill 和 `setup-dashboard` 是同一種東西，用的也是同一批零件，但流程不一樣。三個差別：

1. **多一段檔案結構檢查。**雷達專案的 workflow 檔案要放在 `.github/workflows/` 底下，放錯位置不會報錯，只會什麼都不發生——所以推上去之前先檢查。
2. **不開 GitHub Pages。**雷達不會產生網頁，只會送通知。
3. **不走分支與拉取請求（PR）流程。**這種專案的驗收方式是「推上去之後 workflow 自己跑綠」，不是「走一次 PR」。

## 這個 skill 怎麼運作

1. 這個 skill 自己**幾乎不執行** git 與 gh 指令。它負責的是順序：每一段交給對應的 skill 去做，做完接下一段。
2. 會用到的 skills：`create-commit-v2`、`create-repo`。
3. 其中三段沒有現成的 skill——檔案結構檢查、初始化版本控制、建立規則集——由這個 skill 自己處理。
4. **每一段結束都要回報結果，等使用者放行才進入下一段。**使用者隨時可以喊停。

## 前置檢查

執行前先確認三件事；任何一項不成立就停下來告訴使用者，避免自行補救：

1. 這個資料夾還沒有版本控制（沒有 `.git`）。已經有了就停下來回報，不要重新初始化。
2. gh 已經登入（`gh auth status`）。
3. Git 的全域 `user.name` 與 `user.email` 都有值。缺任何一項就停下來請使用者補上，不要自己代填。

## 第一段：確認檔案結構

這一段沒有對應的 skill，自己做，而且**只讀不寫**。

1. 把資料夾的實際結構列給使用者看，包含 `.github` 底下的層級。
2. 對照這份清單，缺什麼就明確指出來：
   - 專案最外層：`radar.py`、`test_radar.py`、`pyproject.toml`、`.gitignore`
   - `.github/workflows/` 底下：至少一個 `.yml` 檔案
3. 兩個最常見的錯誤，發現了要直接點名：
   - workflow 檔案放在專案最外層，沒有放進 `.github/workflows/`。
   - `.github` 少了開頭的點，變成 `github`。
4. 順便提醒使用者確認 `radar.py` 最上方的 `KEYWORD` 是不是他要盯的主題。**不要替他改**，只是提醒。
5. 結構有問題就停下來，請使用者自己調整好再繼續。結構沒問題就回報「檢查通過」，進下一段。

## 第二段：初始化版本控制

這一段也沒有對應的 skill，自己做。

1. 把即將執行的兩行指令列給使用者確認，使用者確認之前不要執行：

   ```
   git init
   ```

   ```
   git branch -M main
   ```

2. 執行後回報目前的分支名稱，應該是 `main`。

## 第三段：第一個提交

1. 交給 `create-commit-v2`，由它產生符合課程格式的提交訊息。
2. 它列出的檔案清單裡**不應該出現 `.venv`**。如果出現了，代表 `.gitignore` 沒有生效或內容不對，停下來告訴使用者，不要直接提交上去。
3. 專案裡的檔案是使用者事先放好的。不要替他新增、修改或刪除任何檔案。

## 第四段：發布到 GitHub

1. 交給 `create-repo`。儲存庫名稱依它的規範，用專案資料夾的名字。
2. **不要開 GitHub Pages。**這個專案不會產生網頁，開了也沒有東西可以看。使用者如果問起，就是這個原因。

## 第五段：分支規則集（先問，不要預設）

1. 這一段沒有對應的 skill，但**要不要做由使用者決定**。先問他一句，等他回答再動作。
2. 問的時候把判準一起給他，這是一個真正需要判斷的選擇：
   - 這個專案是**人來改、機器檢查**的：規則集該設。要防的是人的手滑。
   - 這個專案的 workflow 需要**寫回儲存庫**（例如把記錄提交回去）：規則集不能設。「main 只能透過 PR 修改」這條規則會連機器人一起擋掉，每次執行都會在最後一步失敗。
3. 使用者說**不設**，就跳過這一段，不要再勸。
4. 使用者說**要設**，設定內容固定如下，寫成一個暫存的 JSON 檔，**放在專案資料夾以外的地方**（避免被一起提交）：

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

5. 把指令與整份 JSON 內容都列給使用者確認，使用者確認之前不要執行：

   ```
   gh api --method POST repos/{owner}/{repo}/rulesets --input 暫存檔路徑
   ```

6. 執行後刪掉暫存檔，回報規則集的名稱與強制狀態。
7. **不要加入狀態檢查（`required_status_checks`）。**這個時間點檢查還沒跑過，加了也選不到；那是後面的課程要做的事。

## 收尾

1. 回報三件事：儲存庫網址、目前所在的分支、這次有沒有設規則集。
2. 提醒使用者去看儲存庫的「Actions」分頁——推送這個動作本身就會叫醒 workflow，那裡應該已經有一筆執行紀錄了。**不要替他解讀那筆紀錄**，讓他自己去看。

## 不要做

以下的事不在這個 skill 的範圍內：

- 不要開啟 GitHub Pages。
- 不要建立或修改任何檔案，包含 `radar.py` 的 `KEYWORD`。檔案由使用者事先放好。
- 不要執行 `uv` 或 `pytest`。本機要不要先跑一次，是使用者自己的事。
- 不要建立或修改 workflow 檔案。那是 `write-workflow` 的事。
- 不要開分支、發拉取請求或合併。這種專案的驗收在 Actions 分頁，不在 PR。
- 不要設定 Secret。存取權杖只能由使用者自己貼進 GitHub 的設定畫面，任何情況下都不要經手它。
- 不要一口氣跑完全部。每一段結束都停下來回報，等使用者放行。
