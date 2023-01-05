import config
import requests
import json
import locale

def get_account_info(keys):
    locale.setlocale(locale.LC_ALL, '')

    r = requests.get(f'{config.BASE_URL}/v2/account', headers=keys)
    account = json.loads(r.content)

    account_info = {
        'Portfolio Value': locale.currency(float(account['portfolio_value']), grouping=True),
        'Cash': locale.currency(float(account['cash']), grouping=True),
        'Position Market Value': locale.currency(float(account['position_market_value']), grouping=True),
        'Long Market Value': locale.currency(float(account['long_market_value']), grouping=True),
        'Short Market Value': locale.currency(float(account['short_market_value']), grouping=True),
    }
    print(json.dumps(account_info, indent=4))

if __name__ == '__main__':
    get_account_info(config.KEYS)
