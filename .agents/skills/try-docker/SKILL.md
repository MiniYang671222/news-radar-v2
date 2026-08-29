---
name: try-docker
description: 在雷達專案裡建立一份示範用的 docker.yml workflow，讓使用者不必在本機安裝 Docker 也能跑起一個容器，並對照雲端機器與容器裡的作業系統與 Python 版本。當使用者要求試用 Docker、示範容器、跑跑看 Docker、或建立 Docker 示範 workflow 時使用。
---

# Try Docker（用 workflow 跑一個容器）

在目前的專案裡新增一份 `docker.yml`。內容是固定的，用途是示範兩件事：GitHub 的雲端電腦本來就內建 Docker，以及容器裡的環境和那台機器的環境是分開的。

## 要寫入的內容

一字不差寫成這份檔案，路徑 `.github/workflows/docker.yml`：

```yaml
name: Docker
on: workflow_dispatch
jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - run: docker run hello-world
      - name: 這台機器的環境
        run: |
          cat /etc/os-release | head -1
          python3 --version
      - name: 光碟裡的環境
        run: docker run python:3.9-slim sh -c "cat /etc/os-release | head -1; python --version"
```

## 三個步驟各自在做什麼

1. `docker run hello-world`：Docker 官方的示範 image，唯一的功能是印一段話證明 Docker 能動，而那段話本身就寫著「下載 image → 建立容器 → 執行 → 送回輸出」四個步驟。
2. **這台機器的環境**：印出 runner 自己的作業系統與 Python 版本。
3. **光碟裡的環境**：用 `python:3.9-slim` 這片現成的 image 跑一個容器，印出容器裡的作業系統與 Python 版本。它和上一步是一組對照，兩邊的作業系統與 Python 版本都會不一樣。

## 執行步驟

1. 先確認目前的資料夾是雷達專案（最外層有 `radar.py`），而且 `.github/workflows/` 存在。不成立就停下來問使用者，不要自己建立專案結構。
2. 如果 `docker.yml` 已經存在，停下來告訴使用者，不要直接覆蓋。
3. 把整份檔案內容列給使用者看，**等他確認再寫入**。
4. 寫入後回報檔案路徑，並提醒他這個 workflow 只有手動觸發，要用 `run-workflow` 或網頁上的按鈕才會跑。

## 不要做

- **不要加 `checkout`。**這個 workflow 不碰儲存庫裡的任何檔案，加了只是多花時間。
- **不要改動 image 名稱、版本或步驟順序。**這三個步驟是設計好的一組對照，換掉任何一個，對照就不成立。
- 不要把三個步驟合併成一步。分開才看得出哪一段輸出對應哪一件事。
- 不要順手建立提交或推送，那是 `create-commit-v2` 的事。
- 不要執行這個 workflow，觸發是 `run-workflow` 的事。
- 不要修改專案裡的其他檔案。
