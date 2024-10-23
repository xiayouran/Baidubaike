# -*- coding: utf-8 -*-
# Author  : liyanpeng
# Email   : yanpeng.li@cumt.edu.cn
# Datetime: 2024/10/22 12:35
# Filename: setup.py
from distutils.core import setup

dependencies = [
    "selenium",
    "beautifulsoup4",
    "requests"
]

setup(
    name='baidubaike',
    packages=['baidubaike'],
    version='1.0.0',
    description='A wrapper of Baidu Baike',
    author='liyanpeng',
    author_email='yanpeng.li@cumt.edu.cn',
    url='https://github.com/xiayouran/Baidubaike',
    download_url='',
    keywords=['baidu', 'wiki', 'baike', 'API', 'html'],
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache License',
        'Programming Language :: Python :: 3'
    ]
)
