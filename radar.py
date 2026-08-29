# 新聞雷達 v2：多了記憶——記住看過的新聞，只通知新的。

# 載入 Python 內建的模組，下面的程式會用到。
import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# 你關注的主題。換成上週選定的那個。
KEYWORD = "股市"

# 一則訊息最多列幾條新聞，減少訊息過多。
MAX_ITEMS = 5

# 雷達的記憶檔：看過的新聞連結都記在這裡。
SEEN_FILE = "seen.json"


# 組網址：把關鍵字接進 Google News 的 RSS 查詢網址（中文要先編碼）。
def make_feed_url(keyword):
    query = urllib.parse.quote(keyword)
    return (
        "https://news.google.com/rss/search?q=" + query
        + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    )


# 抓新聞：把 RSS 內容抓回來，整理成一筆一筆的新聞（標題與連結）。
def fetch_news(url):
    req = urllib.request.Request(url, headers={"User-Agent": "news-radar/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_text = resp.read()
    root = ET.fromstring(xml_text)
    items = []
    for item in root.iter("item"):
        items.append({
            "title": item.findtext("title", ""),
            "link": item.findtext("link", ""),
        })
    return items


# 讀出記憶：看過哪些新聞連結。第一次執行時檔案還不存在，就從空的開始。
def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


# 把記憶寫回檔案。
def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


# 從抓回來的新聞裡，挑出沒看過的。
def pick_new(items, seen):
    return [item for item in items if item["link"] not in seen]


# 組訊息：把新聞清單組成一則通知訊息。
def build_message(keyword, items):
    picked = items[:MAX_ITEMS]
    lines = ["【新聞雷達】「" + keyword + "」有 " + str(len(picked)) + " 則新消息"]
    for item in picked:
        lines.append("・" + item["title"])
        lines.append(item["link"])
    return "\n".join(lines)


# 送通知：用 LINE 的 broadcast API，把訊息廣播給這個 bot 的所有好友。
def send_notification(message, token):
    body = json.dumps(
        {"messages": [{"type": "text", "text": message}]}
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/broadcast",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


# 主流程：組網址、抓新聞、比對記憶、組訊息，最後送通知。
def main():
    url = make_feed_url(KEYWORD)
    items = fetch_news(url)
    if not items:
        print("這次沒有抓到任何新聞。")
        return

    seen = load_seen()
    new_items = pick_new(items, seen)

    # 不管有沒有新的，這次看過的都記下來。
    seen.update(item["link"] for item in items)
    save_seen(seen)

    if not new_items:
        print("沒有新的，不打擾你。")
        return

    message = build_message(KEYWORD, new_items)
    token = os.environ.get("LINE_TOKEN", "")
    if token == "":
        print("（還沒設定存取權杖，先把訊息印出來看看）")
        print(message)
        return
    send_notification(message, token)
    print("已送出通知：" + str(len(new_items)) + " 則是新的。")


# 執行這個檔案時，從 main() 開始跑。
if __name__ == "__main__":
    main()
