import argparse
import os
import requests

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()

    if check_for_redirect(response) == 0:
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

    if check_for_redirect(response) == 0:
        sanitized_filename = sanitize_filename(filename)
        book_image_path = os.path.join(folder, sanitized_filename)
        with open(book_image_path, 'wb') as file:
            file.write(response.content)

    return book_image_path


def parse_book_page(url):

    book_description = {}
    book = []
    comments = []
    genres = []

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    # автор и название
    title_author = soup.find('h1').text.replace('\xa0', '').split('::')

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

    # обложка

    img_short_path = soup.find('div', class_='bookimage').find('img')['src']
    img_path = urljoin('https://tululu.org/', img_short_path)

    book_description['cover'] = img_path

    return book_description


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError
        return 1
    else:
        return 0


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                 description='Скачиваем книги с сайта tululu.org'
                                    )
    parser.add_argument('--start_id', help='С какого id начнем', type=int, default=1)
    parser.add_argument('--end_id', help='На каком id закончим', type=int, default=10)
    args = parser.parse_args()

    start_id = parser.start_id
    end_id = parser.end_id

    if start_id > end_id:
        start_id, end_id = end_id, start_id

    base_dir = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(base_dir, 'books')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(base_dir, 'images')).mkdir(parents=True, exist_ok=True)

    for i in range(start_id, end_id):
        try:
            book_url = f'https://tululu.org/b{i}/'
            book_description = parse_book_page(book_url)
            book_download_url = f'https://tululu.org/txt.php?id={i}'
            book_filename = f'{i}. {book_description["title"]}.txt'
            book_img_filename = f'{i}. {book_description["title"]}.jpg'
            download_txt(book_download_url, book_filename)
            download_img(book_description['cover'], book_img_filename)
        except requests.exceptions.HTTPError:
            print('Ошибка скачивания')
