import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import ValidationError, validate_filename
from pathvalidate import sanitize_filename


def get_book_info(url):

    book_info = []

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    post_text = soup.find('h1').text.replace('\xa0', '').split('::')

    for text in post_text:
        text = text.strip()
        book_info.append(text)

    return book_info


def get_book_id(url):
    id =  re.findall('[0-9]+', url)
    return id


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    sanitized_filename = sanitize_filename(filename)

    book_path =  os.path.join(folder, sanitized_filename)

    with open(book_path, 'wb') as file:
        file.write(response.content)

    return book_path


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(BASE_DIR,'books')).mkdir(parents=True, exist_ok=True)

    for i in range(11):
        try:
            book_url = f'https://tululu.org/b{i}/'
            response = requests.get(book_url)
            check_for_redirect(response)
            response.raise_for_status()
            [title, author]  = get_book_info(book_url)
            filename = f'{i}.{title}.txt'
            download_url = f'https://tululu.org/txt.php?id={i}'
            book_path = download_txt(download_url, filename)
            print(f'Книга {title} сохранена в {book_path}')
        except requests.exceptions.HTTPError:
            print('Ошибка скачивания')







