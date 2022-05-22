from io import BytesIO

import requests
import base64
import json

from PIL import Image

'''
通用文字识别
'''


class BaiduOCR:
    def __init__(self):
        with open('../log/access_token.json', 'r', encoding='utf-8') as f:
            j = json.load(f)
            self.access_token = j['access_token'] if j.get('access_token') else ''
        self.url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic" + "?access_token=" + self.access_token
        self.headers = {'content-type': 'application/x-www-form-urlencoded'}

    def get_access_token(self, your_client_id, your_client_secret):
        # client_id 为 API Key， client_secret 为 Secret Key
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(your_client_id, your_client_secret)
        response = requests.get(host).json()
        if response.get('error'):
            print('您的 API Key 或 Secret Key 存在问题，请检查后重新运行！')
            exit(response['error'])
        else:
            with open('../log/access_token.json', 'w', encoding='utf-8') as fp:
                fp.write(json.dumps(response, indent=2, ensure_ascii=False))
            if not self.access_token:
                self.url += response['access_token']

    def ocr(self, img: Image):
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue())

        params = {"image": img_base64}
        response = requests.post(self.url, data=params, headers=self.headers).json()
        return response

    @staticmethod
    def res2tags(response) -> list:
        if response:
            result = response['words_result']
            words_list = []
            for words in result:
                words_list.append(words['words'])
            return words_list
        return []

    @staticmethod
    def res2name(response) -> str:
        if response:
            result = response['words_result']
            if len(result) > 0:
                return result[0]['words']
        return '未识别'
