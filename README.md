# Baidubaike
百度百科API

# Feature
- [v1.0.0]() 支持获取词条摘要

# Install
```shell
git clone git@github.com:xiayouran/Baidubaike.git
cd Baidubaike
pip install -e .
```

# Usage
```python
from baidubaike import WordSearch

baike = WordSearch()
result = baike.get_summary('百度百科')
print(result)
```

# Thanks
- [yakiang/Baidubaike](https://github.com/yakiang/Baidubaike)
