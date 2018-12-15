pip install -r requirements.txt


Only first 24 pages allowed.


# Prerequirements

You should open api url (for example https://realty.yandex.ru/gate/react-page/get/?rgid=187&type=SELL&category=APARTMENT&_format=react&_pageType=search&_providers=react-search-data&page=1) in browser and copy-paste cookies into "cookies.txt" file (see example.cookies.txt). Cookies can have different keys set. In this case you should copy only cookies that exists in your case. It would be great, if you are logged in Yandex account. You can see your account username in `yandex_login` cookie.

Also I think cookies may be "headers sensetive", so you should copy your headers too.


# Change output fields

If you want to change output fields, you should edit `raw_to_array` function in crawler.py.