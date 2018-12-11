import time
import json
import argparse
import requests
import csv
import io

API_URL = "https://realty.yandex.ru/gate/react-page/get/?rgid={0}&type={1}&category={2}&page={3}&_format=react&_pageType=search&_providers=react-search-data"


class OutputWriter:
    def __init__(self, path, converter):
        self.converter = converter
        self.path = path

    def write(self, data):
        for v in self.converter(data):
            self.csv_writer.writerow(v)

    def __enter__(self):
        self.csv_file = open(self.path, 'a', encoding="utf8", newline='')
        self.csv_writer = csv.writer(self.csv_file, delimiter=';', quotechar='"')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.csv_file.close()

def make_request(args, page_number):
    headers = { 
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, br",
                "Accept-Language":"ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Cache-Control":"max-age=0",
                "Connection":"keep-alive",
                "Host":"realty.yandex.ru",
                "Upgrade-Insecure-Requests":"1",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0" 
              }
    cookies = {
                "_ym_uid":"",
                "bltsr":"",
                "device_id":'',
                "from":"",
                "from_lifetime":"",
                "fuid01":"",
                "i":"",
                "L":"",
                "mda":"",
                "my":"",
                "rheftjdd":"",
                "Session_id":"",
                "sessionid2":"",
                "subscription_popup_count":"",
                "subscription_popup_shown":"",
                "suid":"",
                "X-Vertis-DC":"",
                "yandex_gid":"",
                "yandex_login":"",
                "yandexuid":"",
                "yc":"",
                "yp":"",
                "ys":"",
                "zm":""
              }
    
    url = API_URL.format(args.rgid, args.type, args.category, page_number)
    r = requests.get(url, headers=headers, cookies=cookies)
    return r.json()

def raw_to_array(raw_data):
    for e in raw_data['response']['search']['offers']['entities']:
        yield [ 
                e['offerId'],
                e['location']['geocoderAddress'],
                e['location']['point']['latitude'],
                e['location']['point']['longitude'] 
              ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, default='output/output.csv',
                       help='directory to save parsed data')
    parser.add_argument('--page_number', type=int, default=1,
                       help='page number to start')
    parser.add_argument('--delay', type=float, default=3,
                       help='delay between requests')
    parser.add_argument('--rgid', type=int, default=187,
                       help='region id')
    parser.add_argument('--type', type=str, default="SELL",
                       help='realty type')
    parser.add_argument('--category', type=str, default="APARTMENT",
                       help='realty category')
    args = parser.parse_args()


    current_page = args.page_number
    with OutputWriter(args.output_file, raw_to_array) as writer:
        while True:
            try:
                print("Processing page {}...".format(current_page))
                result = make_request(args, current_page)

                if 'error' in result:
                    break

                writer.write(result)

                current_page += 1
                time.sleep(args.delay)
            except Exception as e:
                print(e)
                print("Unknown exception, waiting 60 seconds.")
                time.sleep(60)
            except KeyboardInterrupt:
                print("Finishing...")
                break
    print("Done")


if __name__ == '__main__':
    main()
