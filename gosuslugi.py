from requests import get

def main():
    headers = {
        'REQUEST_AGENT': REQUEST_AGENT,
        'User-Agent': SKIP_HEADER,
        'Accept-Encoding': SKIP_HEADER,
        'Accept': None,
        'Connection': None
        }

    url = 'https://pos.gosuslugi.ru/api-service/appeals-mobile-api/public-appeal-steps-by-id/177073571'
    resp = get(url)
    print(resp.json())

if __name__ == "__main__":
    main()
