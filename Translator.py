'''
Function:
翻译软件V0.1.2,支持:
        --有道翻译
        --谷歌翻译
作者:
    Tajang

'''

import js
import sys
import time
import js2py
import random
import hashlib
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

'''有道翻译类'''


class youdao:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Referer': 'http://fanyi.youdao.com/',
            'Cookie': 'OUTFOX_SEARCH_USER_ID=-481680322@10.169.0.83;'
        }
        self.data = {
            'i': None,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': None,
            'sign': None,
            'ts': None,
            'bv': None,
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }
        self.url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

    def translate(self, word):
        ts = str(int(time.time() * 10000))
        salt = ts + str(int(random.random() * 10))
        sign = 'fanyideskweb' + word + salt + '97_3(jkMYg@T[KZQmqjTK'
        sign = hashlib.md5(sign.encode('utf-8')).hexdigest()
        bv = '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        bv = hashlib.md5(bv.encode('utf-8')).hexdigest()
        self.data['i'] = word
        self.data['salt'] = salt
        self.data['sign'] = sign
        self.data['ts'] = ts
        self.data['bv'] = bv
        res = requests.post(self.url, headers=self.headers, data=self.data)
        return [res.json()['translateResult'][0][0].get('tgt')]


'''Google翻译类'''


class google:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        self.url = 'https://translate.google.cn/translate_a/single?client=t&sl=auto&tl={}&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&tk={}&q={}'

    def translate(self, word):
        if len(word) > 4891:
            raise RuntimeError('The length of word should be less than 4891...')
        languages = ['zh-CN', 'en']
        if not self.isChinese(word):
            target_language = languages[0]
        else:
            target_language = languages[1]
        res = requests.get(self.url.format(target_language, self.getTk(word), word), headers=self.headers)
        return [res.json()[0][0][0]]

    def getTk(self, word):
        evaljs = js2py.EvalJs()
        js_code = js.gg_js_code
        evaljs.execute(js_code)
        tk = evaljs.TL(word)
        return tk

    def isChinese(self, word):
        for w in word:
            if '\u4e00' <= w <= '\u9fa5':
                return True
        return False


'''简单的Demo'''


class Translator(QWidget):
    def __init__(self, parent=None):
        super(Translator, self).__init__(parent)
        self.setWindowTitle('Tajang制作')
        self.setWindowIcon(QIcon("data/icon.ico"))
        self.Label1 = QLabel('原文')
        self.Label2 = QLabel('译文')
        self.Label1.setAlignment(Qt.AlignCenter)
        self.Label2.setAlignment(Qt.AlignCenter)
        self.TextEdit1 = QTextEdit()
        self.TextEdit2 = QTextEdit()
        self.translateButton1 = QPushButton()
        self.translateButton2 = QPushButton()
        self.translateButton1.setText('有道翻译')
        self.translateButton2.setText('谷歌翻译')
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        self.grid.addWidget(self.Label1, 1, 0)
        self.grid.addWidget(self.TextEdit1, 2, 0)
        self.grid.addWidget(self.Label2, 1, 1)
        self.grid.addWidget(self.TextEdit2, 2, 1)
        self.grid.addWidget(self.translateButton1, 3, 0)
        self.grid.addWidget(self.translateButton2, 3, 1)
        self.setLayout(self.grid)
        self.resize(400, 150)
        self.translateButton1.clicked.connect(lambda: self.translate(api='youdao'))
        self.translateButton2.clicked.connect(lambda: self.translate(api='google'))
        self.yd_translate = youdao()
        self.gg_translate = google()

    def translate(self, api='youdao'):
        word = self.TextEdit1.toPlainText()
        if not word:
            return
        if api == 'youdao':
            results = self.yd_translate.translate(word)
        elif api == 'google':
            results = self.gg_translate.translate(word)
        else:
            raise RuntimeError('Api should be <youdao> or <google>...')
        self.TextEdit2.setText(';'.join(results))


'''run'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Translator()
    demo.show()
    sys.exit(app.exec_())
