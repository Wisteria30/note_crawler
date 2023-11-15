import os
import time

from bs4 import BeautifulSoup
from tqdm import tqdm
import requests



def get_success(url: str, folder: str = "success_data"):
    all_path = f"{url}/all"
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.select('.case-list-box a')
        span_clients = soup.select('.case-lead-box span')

        links = [a.get('href') for a in a_tags]  # /success/xxx?lang=ja
        article_links = [f"https://aisaas.pkshatech.com{link}" for link in links]
        clients = [span.text for span in span_clients]
        client_names = [f"{link.split('?')[0].split('/')[2]}_{client}" for client, link in zip(clients, links, strict=True)]

        for article_link, client in tqdm(zip(article_links, client_names, strict=True), total=len(article_links)):
            get_article(article_link, client, folder=folder)
            time.sleep(0.1)
    else:
        print("Failed to retrieve the webpage.")


def get_article(url: str, client_name: str, folder: str = "success_data"):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        classes = [".success_in_sec2", ".success_in_sec3", ".success_in_sec4"]
        contents = []

        for class_ in classes:
            content = soup.select_one(class_).get_text().strip()
            # \nが二つ以上続く場合は、一つにする
            content = "\n".join([c for c in content.split("\n") if c != ""])
            contents.append(content)

        content = "\n\n".join(contents)

        with open(f"{folder}/{client_name}.txt", "w") as f:
            f.write(content)
    else:
        print("Failed to retrieve the webpage.")


def main():
    root_url = "https://aisaas.pkshatech.com/success/"
    get_success(root_url)


if __name__ == "__main__":
    main()
