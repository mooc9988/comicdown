from my_rename import rename_pic
from bs4 import BeautifulSoup
import requests
import os
import threading
import re

requests.adapters.DEFAULT_RETRIES = 5


def get_pic_list(furl, mpath):
    '''''''''
    爬取图片下载地址，参数为：
    @para 漫画地址
    @para 保存路径
    '''''''''
    down_list = []
    # 以下为代理设置
    proxy = {'http':'socks5://127.0.0.1:10808','https':'socks5h://127.0.0.1:10808'}
    r = requests.get(furl,proxies=proxy)
    # r = requests.get(furl)
    soup = BeautifulSoup(r.content, "lxml")
    name_tmp = soup.select('div[id="info"] h2')
    if not name_tmp:
        name_tmp = soup.select('div[id="info"] h1')
    pattern = re.compile(r'[/\\\|♡•\*"・:\?♥〜♪]')
    comic_name = re.sub(pattern, '', name_tmp[0].get_text())  # 处理漫画名称中的特殊字符
    temp = soup.select(
        'body div[id="content"] div[id="thumbnail-container"] div[class="thumbs"] div[class="thumb-container"] a[class="gallerythumb"] img')  # 获取当前页面各图片区域
    mpath += ('\\' + comic_name)
    if not os.path.exists(mpath):
        os.mkdir(mpath)  # 若章节目录未创建则此时创建
    t_list = temp[1]['src'].split('/')
    pic_burl = 'https://i' + t_list[-4][1:] + \
        '/' + t_list[-3] + '/' + t_list[-2] + '/'
    for i in range(1, len(temp) // 2 + 1):
        geshi = temp[2 * i - 1]['src'].split('.')[-1]
        down_list.append(str(i) + '.' + geshi)
    print('漫画图片地址已经获取完毕，共%s张!' % len(down_list))
    print(('准备下载  %s' % comic_name.encode('GBK', 'ignore').decode('GBk')))
    return (mpath, pic_burl, down_list)


def comic_down(pic_burl, down_list, path, num_each_thread):
    '''''''''
    下载图片，参数为：
    @para 图片基本下载地址，下载列表，存储路径，一个线程最大下载图片数
    '''''''''
    os.chdir(path)
    print('开始下载了！')
    havendown = os.listdir(path)  # 删除已有图片
    if havendown:
        if len(havendown) == len(down_list):
            print("漫画已经下载过，跳过！")
            return
        down_list = [item for item in down_list if item not in havendown]
    threads = []
    for i in range(len(down_list) // num_each_thread + 1):  # 一个进程只下8张图片
        # ch_curl = 'curl --silent '
        ch_curl = 'curl --silent --socks5-hostname 127.0.0.1:10808 '
        temp = down_list[num_each_thread * i:num_each_thread * (i + 1)]
        for item in temp:
            ch_curl += '-O %s ' % (pic_burl + item)
        threads.append(downThread(ch_curl))
    for item in threads:
        item.start()
    for item in threads:
        item.join()
    print('下载完毕！')
    rename_pic(path)

# 爬取真实图片地址的类


class myThread (threading.Thread):
    down_list = []

    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        r = requests.get(self.url)
        soup1 = BeautifulSoup(r.content, "lxml")
        url = 'https:' + \
            soup1.select('span[id="imgarea"] a img')[0]['src']  # 找到图片真实下载地址
        name = soup1.select('span[id="imgarea"] a img')[0]['src'].split('/')[-1]
        # 获取锁，用于线程同步
        threadLock.acquire()
        myThread.down_list.append((url, name))
        # 释放锁，开启下一个线程
        threadLock.release()

# 下载图片的线程，实际上启用了cmd成为多进程


class downThread (threading.Thread):
    def __init__(self, item):
        threading.Thread.__init__(self)
        self.item = item

    def run(self):
        os.system(self.item)
        # r = requests.get(self.item[0])
        # with open(self.item[1], 'wb') as f:
        #     f.write(r.content)
        #     f.close()


if __name__ == '__main__':
    burl = 'https://nhentai.net/g/'  # 漫画主界面
    path = 'D:\\test'  # 保存路径 364060
    dd = []
    for item in dd:
        (mpath, pic_burl, pic_list) = get_pic_list("%s%d" % (burl, item), path)
        if(len(pic_list)):
            comic_down(pic_burl, pic_list, mpath, 8)
