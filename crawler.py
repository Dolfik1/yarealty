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
        self.data = []

    def write(self, data):
        self.data += self.converter(data)

    def __enter__(self):
        self.file = open(self.path, 'w', encoding="utf8")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        json.dump(self.data, self.file)
        self.file.close()

def read_cookies():
    with open("./cookies.txt") as f:
        { cookie.split(" ", 2)[0]: cookie.split(" ", 2)[1] for cookie in f  }

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
    cookies = read_cookies()
    
    url = API_URL.format(args.rgid, args.type, args.category, page_number)
    r = requests.get(url, headers=headers, cookies=cookies)
    return r.json()

def try_extract_value(dic, path):
    keys = path.split(".")
    dv = dic
    for key in keys:
        if not key in dv:
            return None
        dv = dv[key]
    return dv

def raw_to_array(raw_data):
    extract = try_extract_value
    for e in raw_data['response']['search']['offers']['entities']:
        price_per_m2 = None
        if extract(e, "price.unitPerPart") == "SQUARE_METER":
            price_per_m2 = extract(e, "price.valuePerPart")

        floor = None
        floorsOffered = extract(e, "floorsOffered")
        if type(floorsOffered) is list and len(floorsOffered) > 0:
            floor = floorsOffered[0]

        header = "{0} м², {1}-комнатная".format(
            extract(e, "area.value"),
            extract(e, "roomsTotal"))

        yield {
                 "header": header,
                 "advert_type": extract(e, "offerType"),
                 "date_of_public": extract(e, "creationDate"),
                 "price": extract(e, "price.value"),
                 "sale_type": None,
                 "description": extract(e, "description"),
                 "additional_info": None,
                 "seller": {
                    "seller_name": extract(e, "author.name"),
                    "seller_phone": None # phone is encrypted
                 },
                 "house": {
                    "total_floor": extract(e, "floorsTotal"),
                    "elevator": "да" if extract(e, "building.improvements.LIFT") else "нет",
                    "home_type": extract(e, "building.buildingType"),
                    "year_of_construction": extract(e, "building.builtYear"),
                    "state": extract(e, "building.buildingState"),
                    "address": {
                        "address": extract(e, "location.geocoderAddress"),
                        "city_name": None,
                        "latitude": extract(e, "location.point.latitude"),
                        "longitude": extract(e, "location.point.longitude"),
                    }
                 },
                 "apartments": {
                    "price_per_m2": price_per_m2,
                    "floor": floor,
                    "room_count": extract(e, "roomsTotal"),
                    "picture": extract(e, "fullImages"),
                    "repairs": None,
                    "bathroom_type": extract(e, "house.bathroomUnit"),
                    "window_view": extract(e, "house.windowView"),
                    "furniture": extract(e, "apartment.improvements.NO_FURNITURE") is True,
                    "ceiling_height": extract(e, "ceilingHeight"),
                    "balcony": 1 if extract(e, "house.balconyType") is not None else 0,
                    "area": {
                        "total_area": extract(e, "area.value"),
                        "living_area": extract(e, "livingSpace.value"),
                        "rooms_area": extract(e, "livingSpace.value"),
                        "kitchen_area": extract(e, "kitchenSpace.value")
                    }
                 }
              }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, default='output/output.json',
                       help='directory to save parsed data')
    parser.add_argument('--page_number', type=int, default=1,
                       help='page number to start')
    parser.add_argument('--delay', type=float, default=10,
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
                print("Waiting {0} seconds".format(args.delay))
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
