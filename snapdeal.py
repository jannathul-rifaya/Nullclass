import time
import re
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG =================

OUTPUT_CSV = "snapdeal_products.csv"
HEADLESS = False
PAGE_WAIT = 3
SCROLL_PAUSE = 2
MAX_PAGES_PER_SUB = 5
MAX_PRODUCTS_PER_PAGE = None  # set int to limit

BASE_SECTIONS = {
    "Accessories": "https://www.snapdeal.com/search?keyword=accessories",
    "Mobiles": "https://www.snapdeal.com/search?keyword=mobile",
    "Men Clothing": "https://www.snapdeal.com/search?keyword=mens%20clothing",
}

# ================= DRIVER =================

chrome_options = Options()
if HEADLESS:
    chrome_options.add_argument("--headless=new")

chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

wait = WebDriverWait(driver, 10)

# ================= HELPERS =================

def human_sleep(sec=2):
    time.sleep(sec)

def safe_text(el):
    try:
        return el.text.strip()
    except:
        return ""

def safe_attr(el, attr):
    try:
        return el.get_attribute(attr)
    except:
        return ""

def clean_int(txt):
    if not txt:
        return 0
    nums = re.findall(r"\d+", txt.replace(",", ""))
    return int(nums[0]) if nums else 0

def scroll_to_bottom(driver, max_scrolls=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ================= SUB-CATEGORIES =================

def get_left_sub_category_links(driver, left_x_threshold=400):
    subcards = []
    seen = set()

    EXCLUDE = {
        "price","brand","rating","size","colour","color","discount",
        "customer","ship","cod","delivery","availability","seller",
        "apply","clear","sort","view","more","less","newest",
        "fourstar","threestar","twostar","onestar"
    }

    anchors = driver.find_elements(By.XPATH, "//a[@href]")
    for a in anchors:
        text = safe_text(a)
        href = safe_attr(a, "href")

        if not text or not href:
            continue

        if len(text) < 3 or len(text) > 60:
            continue

        if any(k in text.lower() for k in EXCLUDE):
            continue

        if re.fullmatch(r"[\d\W_]+", text):
            continue

        parsed = urlparse(href)
        if "snapdeal" not in parsed.netloc:
            continue

        loc = a.location
        if loc.get("x", 9999) > left_x_threshold:
            continue

        key = (text.lower(), href)
        if key in seen:
            continue

        seen.add(key)
        subcards.append({"sub_category": text, "url": href})

    return subcards

# ================= PAGINATION =================

def click_next_page(driver):
    current_url = driver.current_url
    selectors = [
        "a[rel='next']",
        "a.next",
        "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'next')]"
    ]

    for sel in selectors:
        try:
            btn = driver.find_element(By.XPATH, sel) if sel.startswith("//") \
                else driver.find_element(By.CSS_SELECTOR, sel)
            btn.click()
            time.sleep(2)
            return driver.current_url != current_url
        except:
            continue

    return False

# ================= DEEP SCRAPE =================

def deep_scrape_product_url(driver, url):
    data = {
        "brand": "",
        "full_description": "",
        "seller": "",
        "availability": "",
        "rating": "",
        "reviews_count": 0,
        "breadcrumbs": "",
        "image_url_detail": ""
    }

    if not url:
        return data

    parent = driver.current_window_handle

    try:
        driver.execute_script("window.open(arguments[0]);", url)
        wait.until(EC.number_of_windows_to_be(2))

        for h in driver.window_handles:
            if h != parent:
                driver.switch_to.window(h)
                break

        human_sleep(2)

        try:
            data["brand"] = safe_text(driver.find_element(By.CSS_SELECTOR, ".brand-name"))
        except:
            pass

        try:
            data["rating"] = safe_text(driver.find_element(By.CSS_SELECTOR, ".rating-value"))
        except:
            pass

        try:
            rc = safe_text(driver.find_element(By.CSS_SELECTOR, ".rating-count"))
            data["reviews_count"] = clean_int(rc)
        except:
            pass

        try:
            data["availability"] = safe_text(driver.find_element(By.CSS_SELECTOR, ".availability-message"))
        except:
            data["availability"] = "In Stock"

        try:
            data["seller"] = safe_text(driver.find_element(By.CSS_SELECTOR, ".pdp-seller-name"))
        except:
            pass

        try:
            crumbs = driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb li")
            data["breadcrumbs"] = "<".join(safe_text(c) for c in crumbs if safe_text(c))
        except:
            pass

        images = []
        for img in driver.find_elements(By.TAG_NAME, "img"):
            src = safe_attr(img, "src")
            if src and "snapdeal" in src:
                images.append(src)

        data["image_url_detail"] = ",".join(dict.fromkeys(images))[:2000]

    except:
        pass
    finally:
        try:
            driver.close()
            driver.switch_to.window(parent)
        except:
            pass

    return data

# ================= LISTING SCRAPE =================

def scrape_listing_cards(section, subcat, page):
    items = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")

    for card in cards:
        name = safe_text(card.find_element(By.CLASS_NAME, "product-title")) \
            if card.find_elements(By.CLASS_NAME, "product-title") else ""

        price = safe_text(card.find_element(By.CLASS_NAME, "product-price")) \
            if card.find_elements(By.CLASS_NAME, "product-price") else ""

        url = safe_attr(card.find_element(By.TAG_NAME, "a"), "href") \
            if card.find_elements(By.TAG_NAME, "a") else ""

        extra = deep_scrape_product_url(driver, url)

        audience_text = name.lower()
        if any(k in audience_text for k in ["woman","girl","ladies","female"]):
            audience = "female"
        elif any(k in audience_text for k in ["men","boy","male"]):
            audience = "male"
        elif any(k in audience_text for k in ["kid","child","children"]):
            audience = "children"
        else:
            audience = "unspecified"

        row = {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "top_section": section,
            "sub_category": subcat,
            "product_name": name,
            "brand_heuristic_listing": extra.get("brand") or (name.split()[0] if name else ""),
            "price": price,
            "original_price": "",
            "discount": "",
            "rating_listing": "",
            "rating_detail": extra.get("rating"),
            "reviews_count_listing": "",
            "reviews_count_detail": extra.get("reviews_count"),
            "target_audience": audience,
            "availability": extra.get("availability"),
            "seller": extra.get("seller"),
            "product_url": url,
            "image_url_listing": "",
            "image_url_detail": extra.get("image_url_detail"),
            "short_description": "",
            "full_description": extra.get("full_description"),
            "bread_crumbs": extra.get("breadcrumbs"),
            "page": page
        }

        items.append(row)

    return items

# ================= MAIN =================

all_rows = []

for section, base_url in BASE_SECTIONS.items():
    print(f"\n=== SECTION: {section} ===")
    driver.get(base_url)
    human_sleep(PAGE_WAIT)
    scroll_to_bottom(driver)

    subcats = get_left_sub_category_links(driver)
    if not subcats:
        subcats = [{"sub_category": section, "url": base_url}]

    for sc in subcats:
        print("Sub-category:", sc["sub_category"])
        driver.get(sc["url"])
        human_sleep(PAGE_WAIT)

        total = 0

        for page in range(1, MAX_PAGES_PER_SUB + 1):
            print("Page", page)
            scroll_to_bottom(driver)

            items = scrape_listing_cards(section, sc["sub_category"], page)
            if not items:
                break

            all_rows.extend(items)
            total += len(items)

            if not click_next_page(driver):
                break

        print(f"Collected {total} products")

# ================= SAVE =================

columns = [
    "created_at","top_section","sub_category","product_name",
    "brand_heuristic_listing","price","original_price","discount",
    "rating_listing","rating_detail","reviews_count_listing",
    "reviews_count_detail","target_audience","availability","seller",
    "product_url","image_url_listing","image_url_detail",
    "short_description","full_description","bread_crumbs","page"
]

df = pd.DataFrame(all_rows, columns=columns)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print("DONE — rows:", len(df))

driver.quit()