# autoArxiv

一个用python实现的，以arxiv为数据源的学术论文爬虫。用喵提醒来实现推送功能。后续可能会更新谷歌学术源和scihub源。

## tips
1. `Arxiv`搜索接口
    ```python
        '''
        根据关键词搜索,返回搜索结果
        '''
        def search(self):
            # Electrical Engineering and Systems Science
            url = 'https://arxiv.org/search/eess?'
            params = {
                'query': self.keywords,
                'searchtype': 'all',
                'abstracts': 'show',
                'order': '-announced_date_first',
                'size': '50',
            }
    ```
    此处的搜索接口以电气工程为例，其他接口展示如下：
    ```python
    {
        'physics':'https://arxiv.org/search/physics',
        'Computer Science':'https://arxiv.org/search/cs',
        'Mathematics' : 'https://arxiv.org/search/math',
        'Quantitative Biology' : 'https://arxiv.org/search/q-bio',
        'Quantitative Finance' : 'https://arxiv.org/search/q-fin',
        'Statistics' : 'https://arxiv.org/search/stat',
        'Economics' : 'https://arxiv.org/search/econ'
    }
    ```
2. 配置信息
   
   脚本初次运行会生成`remember.txt`与`config.json`两个配置文件。
   其中前者用来缓存已经下载过的文章，后者用来配置文献检索信息。
   ```json
   {"keywords" : "battery equalization","field" : "eess"}
   ```
   `keyword`的值填写关键字，`field`的值填写该关键字对应的研究领域(填写方式请参考`Arxiv`搜索接口)