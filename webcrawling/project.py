import re
import json
import time
from urllib.parse import quote
from playwright.sync_api import sync_playwright

TARGET_MODELS = ["카니발", "쏘렌토", "스포티지", "K5", "모닝", "레이"]

BASE_URL = (
    "https://www.encar.com/dc/dc_carsearchlist.do?carType=kor#!"
    "%7B%22action%22%3A%22(And.Hidden.N._.(C.CarType.Y._.Manufacturer.%EA%B8%B0%EC%95%84.))%22%2C"
    "%22toggle%22%3A%7B%7D,%22layer%22%3A%22%22,%22sort%22%3A%22ModifiedDate%22,"
    "%22page%22%3A1,%22limit%22%3A20,%22searchKey%22%3A%22%22,%22loginCheck%22%3Afalse%7D"
)

OUTPUT_JSONL = "encar_kia_target_models.jsonl"

def normalize_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def detect_target_model(text: str):
    for model in TARGET_MODELS:
        if model.lower() in text.lower():
            return model
    return None

def extract_price(text: str):
    m = re.search(r"([\d,]+)\s*만원", text)
    return m.group(1).replace(",", "") if m else None

def extract_year(text: str):
    m = re.search(r"(\d{2}/\d{2}식)", text)
    return m.group(1) if m else None

def extract_km(text: str):
    m = re.search(r"([\d,]+)\s*km", text, re.I)
    return m.group(1).replace(",", "") if m else None

def extract_region(text: str):
    regions = [
        "서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종",
        "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
    ]
    for r in regions:
        if r in text:
            return r
    return None

def save_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def make_page_url(page_num: int):
    state = {
        "action": "(And.Hidden.N._.(C.CarType.Y._.Manufacturer.기아.))",
        "toggle": {},
        "layer": "",
        "sort": "ModifiedDate",
        "page": page_num,
        "limit": 20,
        "searchKey": "",
        "loginCheck": False
    }
    return "https://www.encar.com/dc/dc_carsearchlist.do?carType=kor#!" + quote(
        json.dumps(state, ensure_ascii=False, separators=(",", ":")),
        safe=""
    )

def extract_card_candidates(page):
    js = """
    () => {
      const anchors = Array.from(document.querySelectorAll('a[href*="dc_cardetailview.do"], a[href*="carid="]'));
      const seen = new Set();
      const rows = [];

      function pickContainer(a) {
        let el = a;
        for (let i = 0; i < 6 && el; i++, el = el.parentElement) {
          const txt = (el.innerText || '').trim();
          if (txt.length > 30) return el;
        }
        return a;
      }

      for (const a of anchors) {
        const href = a.href || a.getAttribute('href') || '';
        if (!href) continue;
        const m = href.match(/carid=(\\d+)/);
        const carId = m ? m[1] : href;
        if (seen.has(carId)) continue;
        seen.add(carId);

        const container = pickContainer(a);
        const text = (container.innerText || a.innerText || '').replace(/\\s+/g, ' ').trim();

        rows.push({
          car_id: carId,
          detail_url: href.startsWith('http') ? href : ('https://www.encar.com' + href),
          raw_text: text
        });
      }
      return rows;
    }
    """
    return page.evaluate(js)

def extract_detail_fields(detail_page):
    js = """
    () => {
      const bodyText = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();

      function findByLabel(labels) {
        for (const label of labels) {
          const re = new RegExp(label + "\\\\s*[:：]?\\\\s*([^\\\\n]+)");
          const m = bodyText.match(re);
          if (m) return m[1].trim();
        }
        return null;
      }

      return {
        full_text: bodyText,
        fuel: findByLabel(['연료']),
        transmission: findByLabel(['변속기']),
        color: findByLabel(['색상']),
        displacement: findByLabel(['배기량']),
        accident: findByLabel(['사고유무', '사고 여부']),
        seller_type: findByLabel(['판매자', '판매자유형'])
      };
    }
    """
    return detail_page.evaluate(js)

def scrape(max_pages=2, headless=True, with_detail=True):
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1440, "height": 2000},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/145.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        for page_num in range(1, max_pages + 1):
            url = make_page_url(page_num)
            print(f"[LIST] page={page_num}")

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            candidates = extract_card_candidates(page)
            if not candidates:
                print("후보 차량이 없어 종료합니다.")
                break

            for item in candidates:
                text = normalize_text(item.get("raw_text", ""))
                target_model = detect_target_model(text)

                if not target_model:
                    continue

                row = {
                    "page": page_num,
                    "target_model": target_model,
                    "car_id": item.get("car_id"),
                    "detail_url": item.get("detail_url"),
                    "title_or_text": text,
                    "price_manwon": extract_price(text),
                    "year_text": extract_year(text),
                    "mileage_km": extract_km(text),
                    "region": extract_region(text),
                }

                if with_detail and row["detail_url"]:
                    try:
                        dpage = context.new_page()
                        dpage.goto(row["detail_url"], wait_until="domcontentloaded", timeout=60000)
                        dpage.wait_for_timeout(2500)
                        detail = extract_detail_fields(dpage)
                        dpage.close()
                        row.update(detail)
                    except Exception as e:
                        row["detail_error"] = str(e)

                rows.append(row)

            save_jsonl(rows, OUTPUT_JSONL)
            time.sleep(1.5)

        browser.close()

    return rows

if __name__ == "__main__":
    data = scrape(max_pages=30, headless=True, with_detail=True)
    print(f"저장 완료: {OUTPUT_JSONL}, 총 {len(data)}건")