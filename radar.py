# 新聞雷達 v3：加上重試機制，並修正「已讀」判斷時機。

import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

# 你關注的主題。
KEYWORD = "股市"

# 一則訊息最多列幾條新聞，減少訊息過多。
MAX_ITEMS = 5

# 雷達的記憶檔：看過的新聞連結都記在這裡。
SEEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen.json")

# 網路呼叫失敗時的重試次數與間隔（秒）。
MAX_RETRIES = 2
RETRY_DELAY = 3


# 組網址：把關鍵字接進 Google News 的 RSS 查詢網址（中文要先編碼）。
def make_feed_url(keyword):
    query = urllib.parse.quote(keyword)
    return (
        "https://news.google.com/rss/search?q=" + query
        + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    )


# 共用的重試包裝：把任何函式包起來，失敗時重試幾次。
def with_retry(func, *args, what="動作", **kwargs):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):  # 第一次嘗試 + MAX_RETRIES 次重試
        try:
            return func(*args, **kwargs)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ET.ParseError) as e:
            last_error = e
            print(f"（{what}失敗，第 {attempt} 次嘗試：{e}）")
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    raise last_error


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
    except json.JSONDecodeError:
        print("（seen.json 內容損毀，當作空記錄重新開始）")
        return set()


# 把記憶寫回檔案（先寫暫存檔再取代，避免中途中斷造成檔案損毀）。
def save_seen(seen):
    tmp_file = SEEN_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, SEEN_FILE)


# 從抓回來的新聞裡，挑出沒看過的。
def pick_new(items, seen):
    return [item for item in items if item["link"] not in seen]


# 組訊息：把新聞清單組成一則通知訊息（強制限制最多 MAX_ITEMS 則）。
def build_message(keyword, items):
    # 強制截取前 MAX_ITEMS 則新聞，確保訊息不超過上限
    display_items = items[:MAX_ITEMS]
    
    lines = ["【新聞雷達】「" + keyword + "」有 " + str(len(display_items)) + " 則新消息"]
    for item in display_items:
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

    try:
        items = with_retry(fetch_news, url, what="抓新聞")
    except Exception as e:
        print(f"抓新聞最終失敗，這次先放棄：{e}")
        return

    if not items:
        print("這次沒有抓到任何新聞。")
        return

    seen = load_seen()
    new_items = pick_new(items, seen)

    if not new_items:
        # 沒有新的，把這次看到的舊新聞也記一下（避免以後重複判斷），但不影響邏輯。
        seen.update(item["link"] for item in items)
        save_seen(seen)
        print("沒有新的，不打擾你。")
        return

    # 只取這次要通知的部分；超過 MAX_ITEMS 的新聞留到下次再通知。
    to_send = new_items[:MAX_ITEMS]
    remaining = new_items[MAX_ITEMS:]

    message = build_message(KEYWORD, to_send)
    token = os.environ.get("LINE_TOKEN", "")

    if token == "":
        print("（還沒設定存取權杖，先把訊息印出來看看）")
        print(message)
        # 沒有真的發送，所以不 mark as seen，下次會重新嘗試發送同樣的新聞。
        return

    try:
        with_retry(send_notification, message, token, what="發送通知")
    except Exception as e:
        print(f"發送通知最終失敗，這次不標記已讀，下次會重試：{e}")
        return

    # 發送成功後才標記已讀：已發送的 + 這次沒抓到的舊新聞。
    # 注意：remaining（超過 MAX_ITEMS 的）故意不加進 seen，讓它們下次還能被通知到。
    already_seen_but_old = {item["link"] for item in items} - {item["link"] for item in new_items}
    seen.update(already_seen_but_old)
    seen.update(item["link"] for item in to_send)
    save_seen(seen)

    print("已送出通知：" + str(len(to_send)) + " 則。")
    if remaining:
        print(f"還有 {len(remaining)} 則新消息留到下次通知。")


# 執行這個檔案時，從 main() 開始跑。
if __name__ == "__main__":
    main()