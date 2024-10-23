# -*- coding: utf-8 -*-
# Author  : liyanpeng
# Email   : yanpeng.li@cumt.edu.cn
# Datetime: 2024/10/22 15:09
# Filename: proxy.py
import os
import requests


ProxyIP = os.environ.get('BAIKE_PROXY', '192.168.3.224:5555')


def get_random_proxy():
    url = 'http://{}/random'.format(ProxyIP)
    return requests.get(url).text.strip()
