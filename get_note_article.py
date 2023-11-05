import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


def initialize_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    return driver


def close_driver(driver):
    driver.close()
    driver.quit()


def get_notes(url: str, driver, folder: str = "data"):
    all_path = f"{url}/all"
    os.makedirs(folder, exist_ok=True)

    driver.get(all_path)
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)
    time.sleep(10)

    last_height = driver.execute_script("return document.body.scrollHeight")
    print(f"{last_height=}")
    # もっと見るボタンがある場合はクリックして、スクロールを繰り返す
    try:
        element = driver.find_element(By.CLASS_NAME, "o-loadMoreButton")
        element.click()
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)
        time.sleep(5)
    except Exception:
        # 挙動が不安定なので、クリック・スクロールは手動で完了してから次の処理に移る
        print("No more button")
        yesno = input("Do you want to continue? [y/n]: ")
        if yesno == "y":
            pass
        else:
            return
    while True:
        actions = ActionChains(driver)
        scroll_class = driver.find_element(By.CLASS_NAME, "o-footer")
        actions.move_to_element(scroll_class)
        actions.perform()
        time.sleep(5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"{last_height=}, {new_height=}")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    article_links = list(set([f"{url}{link}" for link in links if link.startswith('/n/')]))
    for article_link in tqdm(article_links):
        get_article(article_link, driver, folder)
        time.sleep(1)


def get_article(url: str, driver, folder: str = "data"):
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    try:
        title = soup.find(class_="o-noteContentHeader__title").get_text().strip()

        content = soup.find("div", class_="note-common-styles__textnote-body").get_text().strip()
        # content = soup.find("div", class_="p-article__content").get_text().strip()
        # \u3000を全角スペース、\u00a0を半角スペースに置換、「。」の後に改行を入れる
        content = content.replace("\u3000", "　").replace("\u00a0", " ").replace("。", "。\n")

        content = f"{title}\n\n{content}"
        with open(f"{folder}/{title}.txt", "w") as f:
            f.write(content)

    except AttributeError:
        print(f"AttributeError: {url}")


def main():
    root_url = "https://voice.pkshatech.com"
    driver = initialize_driver()
    get_notes(root_url, driver)
    close_driver(driver)


if __name__ == "__main__":
    main()
