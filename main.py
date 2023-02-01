import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import ValidationError, validate_filename
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit


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
    response = requests.get(book_url)

    check_for_redirect(response)

    response.raise_for_status()

    sanitized_filename = sanitize_filename(filename)

    book_path =  os.path.join(folder, sanitized_filename)

    with open(book_path, 'wb') as file:
        file.write(response.content)

    return book_path


def download_img(url, filename, folder='images/'):
    """Функция для скачивания обложек.
    Args:
        url (str): Cсылка на страницу с описанием.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохраняем обложку.
    """
    response = requests.get(url)

    check_for_redirect(response)

    response.raise_for_status()

    sanitized_filename = sanitize_filename(filename)

    book_image_path =  os.path.join(folder, sanitized_filename)

    with open(book_image_path, 'wb') as file:
        file.write(response.content)

    return book_image_path


def get_book_genre(url):
    genres = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    for genre in raw_genres:
        genres.append(genre.text)
    return genres


def parse_book_page(url):

    book_description = {}
    book = []
    comments = []
    genres = []
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    # автор и название
    title_author = soup.find('h1').text.replace('\xa0', '').split('::')
    print(title_author)

    for elem in title_author:
        elem = elem.strip()
        book.append(elem)

    book_description['author'] = book[1]
    book_description['title'] = book[0]

    # комментарии
    raw_comments = soup.find_all('div', class_='texts')

    for comment in raw_comments:
        comments.append(comment.find('span').text)

    book_description['comments'] = comments

    # жанры
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    for genre in raw_genres:
        genres.append(genre.text)

    book_description['genres'] = genres

    return book_description


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(BASE_DIR,'books')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(BASE_DIR, 'images')).mkdir(parents=True, exist_ok=True)

    for i in range(1,11):
        try:
            book_url = f'https://tululu.org/b{i}/'
            print(parse_book_page(book_url))
        except requests.exceptions.HTTPError:
            print('Ошибка скачивания')







