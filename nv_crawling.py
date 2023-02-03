import requests
from bs4 import BeautifulSoup
import pandas as pd
from logging.config import dictConfig
import logging
import os
import re
from datetime import datetime

def log(msg):
    logging.info(msg)

filePath, fileName = os.path.split(__file__)
logFolder = os.path.join(filePath , 'logs')
os.makedirs(logFolder, exist_ok = True)
logfilepath = os.path.join(logFolder, fileName.split('.')[0] + '_' +re.sub('-', '', datetime.now().strftime('%Y%m%d')) + '.log')

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s --- %(message)s',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': logfilepath,
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})


def NS_users_crawler(ticker, page):
    # User-Agent 설정
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}
    result_df = pd.DataFrame([])

    n_ = 0
    for page in range(1, page):
        n_ += 1
        if (n_ % 30 == 0):
            log('================== Page ' + str(page) + ' is done ==================')
            result_df.to_csv(os.path.join(filePath,'naver_ds_' + datetime.now().strftime('%Y-%m-%d') + '.csv'), encoding = 'utf-8-sig', index = False)
        url = "https://finance.naver.com/item/board.naver?code=%s&page=%s" % (ticker, str(page))
        # html → parsing
        html = requests.get(url, headers=headers).content
        # 한글 깨짐 방지 decode
        soup = BeautifulSoup(html.decode('euc-kr', 'replace'), 'html.parser')
        table = soup.find('table', {'class': 'type2'})
        tb = table.select('tbody > tr')

        for i in range(2, len(tb)):
            if len(tb[i].select('td > span')) > 0:
                date = tb[i].select('td > span')[0].text
                title = tb[i].select('td.title > a')[0]['title']
                views = tb[i].select('td > span')[1].text
                pos = tb[i].select('td > strong')[0].text
                neg = tb[i].select('td > strong')[1].text
                table = pd.DataFrame({'날짜': [date], '제목': [title], '조회': [views], '공감': [pos], '비공감': [neg]})
                result_df = pd.concat([result_df,table])

    return result_df

def main():
    NS_users_crawler('034020', 30000)

if __name__=="__main__":
    main()