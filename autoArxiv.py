from gc import callbacks
from urllib import request, parse
import requests
import json
import os
from bs4 import BeautifulSoup
from alive_progress import alive_bar
from urllib.request import urlretrieve

# 消息推送类
class MessagePost(object):
    def __init__(self, text, meowKey, mailgunUrl, mailgunKey, emailSrc, emailDst): 
        self.text = text
        self.meowKey = meowKey
        self.mailgunUrl = mailgunUrl
        self.mailgunKey = mailgunKey
        self.emailSrc = emailSrc
        self.emailDst = emailDst

    # 通过喵提醒推送通知到微信
    def meowPush(self):
        page = request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id": self.meowKey, "text": self.text, "type": "json"}))
        result = page.read()
        jsonObj = json.loads(result)
        if (jsonObj["code"] == 0):
            print("\nReminder message was sent successfully")
        else:
            print("\nReminder message failed to be sent,wrong code:" + str(jsonObj["code"]) + ",describe:" + jsonObj["msg"])

    # 基于mailgun的邮件推送
    def mailgunPush(self, content):
        return requests.post(
            self.mailgunUrl,
            auth = ("api", self.mailgunKey),
            data = {
                "from": self.emailSrc,
                "to": self.emailDst,
                "subject": "search results",
                "text": content
            }
        )

# 论文监控类
class ArxivMonitor:
    def __init__(self, keywords, field):
        self.keywords = keywords
        self.field = field
        keywords = keywords.replace(' ', '+')
        self.session = requests.session()

    # 根据关键词搜索,返回搜索结果
    def search(self):
        # Electrical Engineering and Systems Science
        url = 'https://arxiv.org/search/'+ self.field + '?'
        params = {
            'query': self.keywords,
            'searchtype': 'all',
            'abstracts': 'show',
            'order': '-announced_date_first',
            'size': '50',
        }
        response = self.session.get(url, params=params)
        # 解析
        contents = BeautifulSoup(response.text, features='lxml')

        def text_strip(soup_search):
            if soup_search != None:
                return soup_search.text.strip()
            else:
                return ""

        def text_format(text):
            text = text.replace('\n', '')
            text, text_clean = text.split(' '), []
            for item in text:
                if item: text_clean.append(item)
            text = ' '.join(text_clean)
            return text

        # 以文章url为key, 文章其余属性为value构建字典
        res = {}
        arxiv_ordered_lists = contents.find('ol')
        arxiv_results = arxiv_ordered_lists.find_all('li', attrs = {'class': 'arxiv-result'})

        for arxiv_result in arxiv_results:
            paper_title = text_strip(arxiv_result.find('p', attrs = {'class' : 'title'}))
            paper_authors = text_format(text_strip(arxiv_result.find('p', attrs = {'class' : 'authors'})))
            paper_abstract = text_format(text_strip(arxiv_result.find('p', attrs = {'class' : 'abstract'})))
            paper_comments = text_format(text_strip(arxiv_result.find('p', attrs = {'class' : 'comments'})))
            paper_url = arxiv_result.find('p', attrs={'class' : 'list-title'}).find('a').attrs['href']
            
            if paper_url == None: 
                continue
            
            paper_content = {
                'title' : paper_title,
                'authors' : paper_authors,
                'abstract' : paper_abstract,
                'paper_comments' : paper_comments,
                'url' : paper_url
            }
            # 添加本篇文章
            res[paper_content['url']] = paper_content

        return res

# 下载类
class HttpDownloader:
    def __init__(self):
        self.downloadedPaper = []
        self.isUpdate = False
    
    # 如果本地文件不存在,创建一个
    def checkLocalFile(self):
        flag = False
        if (not os.path.exists('remember.txt')):
            with open('remember.txt', 'w') as f:
                f.write('')
            flag = True
        
        if (not os.path.exists('config.json')):
            config_json = (
                '{\"keywords\":\"\",\"field\":\"\",\"message\":{\"meowKey\":\"\",\"mailgunUrl\":\"\",\"mailgunKey\":\"\",\"emailSrc\":\"\",\"emailDst\":\"\"}}'
            )
            with open('config.json', 'w') as f:
                f.write(config_json)
            flag = True

        if (flag):
            exit(1)

    # 加载本地文件
    def loadLoaclFile(self, localfilepath):
        with open(localfilepath, 'r') as f:
            while(1):
                line = f.readline()
                if not line:
                    break
                # print(line)
                self.downloadedPaper.append(str(line))

    # 判断文章是否下载过
    def wasDownloaded(self, url):
        if ((url+'\n') in self.downloadedPaper):
            return True
        return False

    # 添加一条下载记录
    def addRecord(self, url):
        self.downloadedPaper.append(url)

    # 更新本地记录
    def updateLocalFile(self, localfilepath):
        with open(localfilepath, 'w') as f:
            for record in self.downloadedPaper:
                f.write(record.replace('\n', '') + '\n')

    # 回调函数:下载进度
    def callbackinfo(self, done, block, size):
        per = 100.0 * (done * block) / size
        if per > 100:
            per = 100
        print ('\r' + '%.2f%%' % per, end = ' ')

    # 执行下载
    def downloadPaper(self, url, savepath):
        url = url.replace('abs', 'pdf') + '.pdf'
        download_success = False

        if (self.wasDownloaded(url)):
                print('该文章已下载过')
                return download_success

        illegals = [':', '\\', '\'', ' ', '?', '!', '*', '|']
        for illegal in illegals:
            if (illegal in savepath):
                savepath = savepath.replace(illegal, '_')

        try:
            urlretrieve(url, filename = savepath + '.pdf', reporthook=self.callbackinfo)
            download_success = True
            self.isUpdate = True
            self.addRecord(url)
        except Exception as e:
            print(e)
            download_success = False
        
        return download_success

# '''
# 输出到文件以检查结果
# '''
# def output_debug_file(content):
#     with open('debug_res.txt', 'a', encoding='utf_8') as f:
#         f.write(str(content))

def main():
    savepath = './'+ 'search_results' +'/'
    os.makedirs(savepath, exist_ok=True)

    downloader = HttpDownloader()
    downloader.checkLocalFile()
    downloader.loadLoaclFile('remember.txt')

    with open('config.json', 'r') as f:
        config_info = json.load(f)

    messagePost = MessagePost(
            "", 
            meowKey = config_info['message']['meowKey'],
            mailgunKey = config_info['message']['mailgunKey'],
            mailgunUrl = config_info['message']['mailgunUrl'],
            emailSrc = config_info['message']['emailSrc'],
            emailDst = config_info['message']['emailDst']
        )
    
    monitor = ArxivMonitor(keywords=config_info['keywords'], field=config_info['field'])
    search_res = monitor.search()

    cnt = 0
    for url, paper in search_res.items():
        cnt += 1
        print('\n正在获取第' + str(cnt) + '篇文章...')
        paper_savepath = savepath + paper['title'].replace(' ', '_')
        downloader.downloadPaper(paper['url'], paper_savepath)

    downloader.updateLocalFile('remember.txt')

main()