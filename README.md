# Baidubaike
百度百科API

# Feature
- [v1.2.0]() 修复动态标签解析问题
- [v1.1.0]() 支持Selenium+代理池
- [v1.0.0]() 支持获取词条摘要

# Install
```shell
git clone git@github.com:xiayouran/Baidubaike.git
cd Baidubaike
pip install -e .
```

# Usage
```python
from baidubaike import WordSearch, SearchbySelenium

# baike = WordSearch()
baike = SearchbySelenium(total_code='XvBOa', title_code='YkQdg')
result = baike.get_summary('百度百科')
print(result)
```

`获取动态标签：`

[baike](imgs/baike.jpg)

# Proxy
代理池使用详情请参考：[ProxyPool](https://github.com/Python3WebSpider/ProxyPool)
```shell
git clone git@github.com:Python3WebSpider/ProxyPool.git
cd ProxyPool

# 修改docker-compose文件，做一个专属于百度百科的代理池
TEST_URL: https://baike.baidu.com
REDIS_KEY: proxies:baidubaike

# 以docker方式启动代理池
docker compose up -d

# 使用时需要配置代理池的ip
export BAIKE_PROXY=192.168.3.224:5555
```

# Thanks
- [yakiang/Baidubaike](https://github.com/yakiang/Baidubaike)
