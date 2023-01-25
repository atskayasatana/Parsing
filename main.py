import os
import requests

from pathlib import Path


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    Path(os.path.join(BASE_DIR,'books')).mkdir(parents=True, exist_ok=True)

    for i in range(11):
        url = f'https://tululu.org/txt.php?id={i}'
        response = requests.get(url)
        response.raise_for_status()
        filename = f'books/{i}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)



