# coding=utf-8
"""
Constants for TDS API
"""

HEADERS = {
    'Connection':'keep-alive',
    'Pragma':'no-cache',
    'Cache-Control':'no-cache',
    'Origin':'https://www.e-license.jp',
    'Upgrade-Insecure-Requests':'1',
    'Content-Type':'application/x-www-form-urlencoded',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/68.0.3440.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;' \
               'q=0.9,image/webp,image/apng,*/*;' \
               'q=0.8',
    'Referer': 'https://www.e-license.jp/el25/mobile?' \
               'abc=LAtcyKgwukI\x2BbrGQYS\x2B1OA\x3D\x3D',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'en-US,en;q=0.9',
}

DATA = {
    'b.wordsStudentNo': '\x8b\xb3\x8f\x4b\x90\xb6\x94\xd4\x8d\x86',
    'b.schoolCd': 'LAtcyKgwukI\x2BbrGQYS\x2B1OA\x3D\x3D',
    'server': '',
}
