import argparse
import os
import time

import requests

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib3.exceptions import HTTPError


def download_txt(url, payload, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    sanitized_filename = sanitize_filename(filename)
    book_path = os.path.join(folder, sanitized_filename)
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
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename)
    book_image_path = os.path.join(folder, sanitized_filename)
    with open(book_image_path, 'wb') as file:
        file.write(response.content)
    return book_image_path


def parse_book_page(response):

    soup = BeautifulSoup(response.text, 'lxml')

    # автор и название
    title, author = soup.find('h1').text.replace('\xa0', '').split('::')
    author = author.strip()
    title = title.strip()

    # комментарии
    raw_comments = soup.find_all('div', class_='texts')
    comments = [comment.find('span').text for comment in raw_comments]

    # жанры
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in raw_genres]

    # обложка

    img_short_path = soup.find('div', class_='bookimage').find('img')['src']
    img_path = urljoin(response.url, img_short_path)

    book_description = {
        'author': author,
        'title': title,
        'genres': genres,
        'comments': comments,
        'cover': img_path
    }

    return book_description


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def main():
    parser = argparse.ArgumentParser(
                 description='Скачиваем книги с сайта tululu.org'
                                    )
    parser.add_argument('start_id',
                        nargs='?',
                        help='С какого id начнем',
                        type=int,
                        default=1
                        )
    parser.add_argument('end_id',
                        nargs='?',
                        help='На каком id закончим',
                        type=int,
                        default=10)
    args = parser.parse_args()

    book_start_id = args.start_id
    book_end_id = args.end_id

    if book_start_id > book_end_id:
        book_start_id, book_end_id = book_end_id, book_start_id

    project_dir = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(project_dir, 'books'))\
        .mkdir(parents=True, exist_ok=True)
    Path(os.path.join(project_dir, 'images'))\
        .mkdir(parents=True, exist_ok=True)

    for book_id in range(book_start_id, book_end_id):
        try:
            url = 'https://tululu.org'
            response = requests.get(urljoin(url, f'b{book_id}/'),
                                    allow_redirects=True
                                    )
            print(book_id)
            check_for_redirect(response)
            response.raise_for_status()
            book_description = parse_book_page(response)
            book_download_url = f'{urljoin(url,"txt.php")}'
            book_download_params = {'id': book_id}
            book_filename = f'{book_id}. {book_description["title"]}.txt'
            book_img_filename = f'{book_id}. {book_description["title"]}.jpg'
            download_txt(book_download_url,
                         book_download_params,
                         book_filename
                         )
            download_img(book_description['cover'], book_img_filename)
        except HTTPError:
            print('Ошибка скачивания')
        except requests.exceptions.ConnectionError:
            attempt_to_connect = 0
            print('Проблемы с подключением...')
            while attempt_to_connect < 15:
                time.sleep(1.5)
                attempt_to_connect += 1
            pass


if __name__ == '__main__':
    main()
