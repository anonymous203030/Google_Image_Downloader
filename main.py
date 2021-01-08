import os
import sqlite3
import urllib.request
import time
import magic
import requests


class ImageDownloader:
    def __init__(self):
        pass

    def GetUrls(self, keyword_to_search, start, limit, extensions=None):
        if extensions == None:
            extensions = {'.jpg', '.png', '.ico', '.gif', '.jpeg'}
        links = []
        spam = ('https://www.google.com/logos', 'https://www.google.com/favicon.ico')
        for word in keyword_to_search:
            try:
                os.makedirs(word)
                print('Directory Created')
            except OSError as e:
                if e.errno != 17:
                    print('error')
                    raise
            print('starting url')
            url = f'https://www.google.com/search?q={word}' \
                  f'&biw=1536&bih=674&tbm=isch&sxsrf=ACYBGNSXXpS6YmAKUiLKKBs6xWb4uUY5gA:' \
                  f'1581168823770&source=lnms&sa=X&ved=0ahUKEwioj8jwiMLnAhW9AhAIHbXTBMMQ_AUI3QUoAQ'
            print(url)
            download_page_time = time.time()
            raw_html = self.DownloadPage(url)
            print('DOWNLOAD PAGE TIME:', time.time() - download_page_time)
            end_object = -1
            j = 0

            while j < limit:
                print('-------Starting-------')
                if j < start:
                    j +=1
                else:
                    raw_html_time = time.time()
                    while True:
                        try:

                            new_line = raw_html.find('"https://', end_object + 1)
                            end_object = raw_html.find('"', new_line + 1)
                            buffor = raw_html.find('\\', new_line + 1, end_object)

                            if buffor != -1:
                                object_raw = (raw_html[new_line + 1:buffor])
                            else:
                                object_raw = (raw_html[new_line + 1:end_object])

                            if any(extension in object_raw for extension in extensions):
                                break
                        except Exception as e:
                            break
                    all = self.DatabaseInside(object_raw)
                    print(f'{len(all)} in Database.')
                    if len(all) == 0:
                        print('RAW HTML FIND TIME', time.time() - raw_html_time)
                        photo_url_time = time.time()
                        path = word.replace(" ", "_")
                        print(path)
                        try:
                            print(f'Photo {j} of {word} starting....')
                            r = requests.get(object_raw, allow_redirects=True, timeout=0.3)
                            if ('html' not in str(r.content)):
                                mime = magic.Magic(mime=True)
                                file_type = mime.from_buffer(r.content)
                                file_extension = f'.{file_type.split("/")[1]}'
                                if file_extension not in extensions:
                                    raise ValueError()
                                if j == 0 or object_raw in spam:
                                    j += 1
                                    raise
                                links.append(object_raw)
                                print("PHOTO URL TIME", time.time() - photo_url_time)
                                file_creating = time.time()
                                dir_direction = str(word) + "_" + str(j) + file_extension
                                with open(os.path.join(path, dir_direction), 'wb') as file:
                                    file.write(r.content)
                                    self.DatabaseConnect(object_raw, word)
                                    print(f'Photo {j} of {word} COMPLETED.GUT')
                                print("FILE CREATING TIME", time.time() - file_creating)
                        except Exception as e:
                            print("EXCEPTION", e)
                            j -= 1
                j += 1
        return links, keyword_to_search

    def DownloadPage(self, url):
        try:
            print('Downloading Page')
            headers = {}
            headers[
                'User-Agent'] = "Mozilla/6.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
            respData = str(urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read())
            print('Downloaded Page')
            return respData

        except Exception as e:
            print('ERRORROROROROORORRR', e)
            exit(0)

    def DatabaseConnect(self, urls, keyword):
        print('Including into Database')
        time0 = time.time()
        conn = sqlite3.connect('Images.db')

        conn.execute("INSERT INTO ImageUrls (URL, NAME)"
                     f"VALUES ('{urls}', '{keyword}')")
        conn.commit()

        conn.close()
        return print('Ended Dbase including', time.time() - time0)

    def DatabaseInside(self, url):
        print('Executing From Database')
        time0 = time.time()
        conn = sqlite3.connect('Images.db')
        all = conn.execute(f'SELECT URL FROM ImageUrls WHERE URL="{url}"')
        all_urls = all.fetchall()
        # conn.commit()
        conn.close()
        return all_urls


if __name__ == '__main__':
    number = int(input('Input Number Of Words You Wanna Search: '))
    words = []
    for x in range(number):
        words.append(input(f'Input word number {x + 1}: '))
    time0 = time.time()
    limit = int(input('Input Limit: '))
    start = int(input('Start From Number: '))
    ImageDownloader().GetUrls(words, start, limit)
    print("TOTAL TIME", time.time() - time0)
