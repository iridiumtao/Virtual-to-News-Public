from news.proxy import get_need_proxy


def proxy():
    start_crawlers = ['sslproxies', 'coolproxie']
    # start_crawlers = ['coolproxie']
    site_used = 'httpbin.org/ip'
    # site_used = 'icanhazip.com'
    only_http = True
    file_path = './news/assets/proxy.csv'
    get_need_proxy(start_crawlers, site_used, only_http, file_path)


proxy()

# from requests import adapters
# import requests
# from news.common.agent import headers
# from loguru import logger
# from time import sleep

# def proxy_check_available(meta: dict, site_used: str = 'httpbin.org/ip'):
#     adapters.DEFAULT_RETRIES = meta['retry']
#     timeout = meta['timeout']
#     proxy = meta['proxy']
#     url = ''
#     if meta['scheme'] == 'https':
#         url = 'https' + '://' + site_used
#         proxies = {'https': proxy}
#     elif meta['scheme'] == 'http':
#         url = 'http' + '://' + site_used
#         proxies = {'http': proxy}
#     else:
#         url = 'http' + '://' + site_used
#         proxies = {'http': proxy}

#     try:
#         response = requests.get(
#             url,
#             timeout=timeout,
#             proxies=proxies,
#             # verify=False,
#             headers=headers())

#     except requests.exceptions.ProxyError:
#         logger.info(f'proxy連接不上：{proxy}')
#     except requests.exceptions.ConnectTimeout:
#         logger.info(f'連接超時：{proxy}')
#     except requests.exceptions.ReadTimeout:
#         logger.info(f'讀取超時：{proxy}')
#     except requests.exceptions.ConnectionError:
#         sleep(2)
#         logger.info(f'ConnectionError：{proxy}')
#         # proxy_check_available(meta)
#     except requests.exceptions.ChunkedEncodingError:
#         if site_used == 'icanhazip.com':
#             site_used = 'httpbin.org/ip'
#         if site_used == 'httpbin.org/ip':
#             site_used = 'icanhazip.com'
#         logger.info(f'ChunkedEncodingError 被伺服器擋：{site_used}')
#         proxy_check_available(meta, site_used)
#     else:
#         if response.status_code == 200:
#             content = response.text
#             logger.info(f'可以用的proxy{proxy}，response：{content}')
#             return meta
#         elif response.status_code == 502:
#             logger.info(f'response502 防火牆擋：{site_used}')
#             proxy_check_available(meta, site_used)
#         else:
#             logger.info(f'TODO error{response}')

# meta = {
#     'port': 8118,
#     'proxy': 'http://161.97.126.37:8118',
#     'retry': 3,
#     'timeout': 3,
#     'scheme': 'http',
#     'ip': '161.97.126.37',
# }
# proxy_check_available(meta)