import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import ValidationError, validate_filename
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit


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


def download_comments(url):
    comments = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    post_text = soup.find_all('div', class_='texts')

    for p in post_text:
        comments.append(p.find('span').text)
    return comments


def get_book_genre(url):
    genres = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    for genre in raw_genres:
        genres.append(genre.text)
    return genres


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(BASE_DIR,'books')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(BASE_DIR, 'images')).mkdir(parents=True, exist_ok=True)

    for i in range(11):
        try:
            book_url = f'https://tululu.org/b{i}/'
            response = requests.get(book_url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            [title, author]  = get_book_info(book_url)
            filename = f'{i}.{title}.txt'
            download_url = f'https://tululu.org/txt.php?id={i}'
            book_path = download_txt(download_url, filename)
            print(f'Книга {title} сохранена в {book_path}')
            book_image = soup.find('div', class_='bookimage').find('img')['src']
            book_cover_full_path = urljoin('https://tululu.org', book_image)
            print(book_cover_full_path)
            image_name = urlparse(book_cover_full_path).path.split('/')[-1]
            img_path = download_img(book_cover_full_path, image_name)
            print(print(f'Обложка сохранена в {img_path}'))
            comments = download_comments(book_url)
            print(comments)
            genres = get_book_genre(book_url)
            print(genres)

        except requests.exceptions.HTTPError:
            print('Ошибка скачивания')







