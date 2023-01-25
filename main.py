import os
import requests

from pathlib import Path


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(BASE_DIR,'books')).mkdir(parents=True, exist_ok=True)

    for i in range(11):
        try:
            url = f'https://tululu.org/txt.php?id={i}'
            response = requests.get(url)
            check_for_redirect(response)
            response.raise_for_status()
            filename = f'books/{i}.txt'
            with open(filename, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.HTTPError:
            print('Ошибка скачивания')







