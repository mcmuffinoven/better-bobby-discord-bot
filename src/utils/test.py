from web_scrapper import WebScrapper
from selenium.webdriver.common.by import By
from postgres import Postgres

# scrapper = WebScrapper()

# scrapper.set_scrape_url("https://www.bestbuy.ca/en-ca/product/asus-rog-swift-32-4k-ultra-hd-240hz-0-03ms-gtg-oled-led-g-sync-gaming-monitor-pg32ucdm/17728627")
# scrapper.load_browser()
# print(scrapper.get_product_current_price())
# print(scrapper.get_product_name())
# scrapper.terminate_session()

db = Postgres()

name = """OtterBox Defender Case for iPad 10.9" (10th Gen) - Black"""

exist = db.check_product(name)

users, col = db.fetch_all_users()

print(exist)
