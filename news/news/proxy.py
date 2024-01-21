from bs4 import BeautifulSoup
import requests
from enum import Enum
from requests import adapters
from loguru import logger
from time import sleep
from news.common.agent import headers
import pandas as pd
import json
from os.path import isfile


class CrawlerMethod(str, Enum):
    sslproxies = "sslproxies"


def proxy_check_available(meta: dict, site_used: str = 'httpbin.org/ip'):
    adapters.DEFAULT_RETRIES = meta['retry']
    timeout = meta['timeout']
    proxy = meta['proxy']
    url = ''
    if meta['scheme'] == 'https':
        url = 'https' + '://' + site_used
        proxies = {'https': proxy}
    elif meta['scheme'] == 'http':
        url = 'http' + '://' + site_used
        proxies = {'http': proxy}
    else:
        url = 'http' + '://' + site_used
        proxies = {'http': proxy}

    try:
        response = requests.get(
            url,
            timeout=timeout,
            proxies=proxies,
            # verify=False,
            headers=headers())

    except requests.exceptions.ProxyError:
        logger.info(f'proxy連接不上：{proxy}')
    except requests.exceptions.ConnectTimeout:
        logger.info(f'連接超時：{proxy}')
    except requests.exceptions.ReadTimeout:
        logger.info(f'讀取超時：{proxy}')
    except requests.exceptions.ConnectionError:
        sleep(2)
        logger.info(f'ConnectionError：{proxy}')
        # proxy_check_available(meta)
    except requests.exceptions.ChunkedEncodingError:
        if site_used == 'icanhazip.com':
            site_used = 'httpbin.org/ip'
        if site_used == 'httpbin.org/ip':
            site_used = 'icanhazip.com'
        logger.info(f'ChunkedEncodingError 被伺服器擋：{site_used}')
        proxy_check_available(meta, site_used)
    else:
        logger.info(f'可以用的proxy{proxy}')
        return meta
        # if response.status_code == 200:
        #     content = response.text
        #     logger.info(f'可以用的proxy{proxy}，response：{content}')
        #     return meta
        # elif response.status_code == 502:
        #     logger.info(f'response502 防火牆擋：{site_used}')
        #     proxy_check_available(meta, site_used)
        # else:
        #     logger.info(f'TODO error{response}')


def sslproxies(url: str, only_http: bool, site_used: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    trs = soup.select("div.table-responsive table.table-striped tr")
    for tr in trs:
        tds = tr.select("td")
        if len(tds) > 6:
            ip = tds[0].text
            port = tds[1].text
            # country_code = tds[2].text
            country = tds[3].text
            anonymity = tds[4].text
            gooogle = tds[5].text
            https = tds[6].text
            if only_http:
                scheme = 'http'
            else:
                if https == 'yes':
                    scheme = 'https'
                else:
                    scheme = 'http'

            proxy = "%s://%s:%s" % (scheme, ip, port)
            meta = {
                'port': port,
                'proxy': proxy,
                'retry': 3,
                'timeout': 3,
                'scheme': scheme,
                'ip': ip,
                'country': country,
                'anonymity': anonymity,
                'gooogle': gooogle
            }

            yield proxy_check_available(meta, site_used)


def get_proxy(need_proxy, proxys_df: pd):
    # num = 5
    # i = 0
    # while True and i < num:
    #     i += 1
    while True:
        try:
            meta = next(need_proxy)
        except StopIteration:
            break
        else:
            if meta:
                proxy_df = pd.DataFrame(meta.values())
                proxys_df = pd.concat([proxys_df, proxy_df], axis=1)
    return proxys_df


def coolproxie(url: str, site_used: str):

    response = requests.get(url)
    response_text = response.text
    response_json = json.loads(response_text)
    for res in response_json:
        ip = res['ip']
        port = res['port']
        # country_code=res['country_code']
        country_name = res['country_name']
        if res['anonymous']:
            anonymity = 'anonymous'
        else:
            anonymity = 'unknown'

        proxy = "%s://%s:%s" % ('http', ip, port)
        meta = {
            'port': port,
            'proxy': proxy,
            'retry': 3,
            'timeout': 3,
            'scheme': 'Unknown',
            'ip': ip,
            'country_name': country_name,
            'anonymity': anonymity,
            'gooogle': 'Unknown'
        }
        yield proxy_check_available(meta, site_used)


def get_need_proxy(start_crawlers: str, site_used: str, only_http: bool,
                   file_path: str):
    sslproxies_url = 'https://www.sslproxies.org'
    coolproxie_url = 'https://cool-proxy.net/proxies.json'
    if isfile(file_path):
        proxys_df = pd.read_csv(file_path).T.reset_index().drop(['index'],
                                                                axis=1)
    else:
        proxys_df = pd.DataFrame()

    if 'sslproxies' in start_crawlers:
        s = sslproxies(sslproxies_url,
                       only_http=only_http,
                       site_used=site_used)
        proxys_df = get_proxy(need_proxy=s, proxys_df=proxys_df)
    if 'coolproxie' in start_crawlers:
        c = coolproxie(coolproxie_url, site_used=site_used)
        proxys_df = get_proxy(need_proxy=c, proxys_df=proxys_df)

    # proxys_df.index = [
    #     'port', 'proxy', 'retry', 'timeout', 'scheme', 'ip', 'country_name',
    #     'anonymity', 'gooogle'
    # ]
    proxys_df = proxys_df.T
    proxys_df.columns = [
        'port', 'proxy', 'retry', 'timeout', 'scheme', 'ip', 'country_name',
        'anonymity', 'gooogle'
    ]
    proxys_df.drop_duplicates(subset='proxy', keep='first', inplace=True)
    proxys_df.to_csv(file_path, index=False)


if __name__ == '__main__':
    start_crawlers = ['sslproxies','coolproxie']
    start_crawlers = []
    site_used = 'httpbin.org/ip'
    # site_used = 'icanhazip.com'
    only_http = True
    file_path = './proxy.csv'
    get_need_proxy(start_crawlers, site_used, only_http, file_path)
