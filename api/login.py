"""
Login
"""
import re
import requests

from api.common.constants import HEADERS, DATA
from api.common.utils import toyota_req

def login(username, password):
    """
    Login to toyota driving school.

    :param username: username
    :param password: password
    :return: cookies
    """
    url = 'https://www.e-license.jp/el25/mobile/p01a.action'

    data = {
        'b.studentId': username,
        'b.password': password,
        'method\x3AdoLogin': '\x83\x8D\x83\x4f\x83\x43\x83\x93',
        'b.kamokuCd': '',
    }

    data.update(DATA)
    res = toyota_req(
        requests.post(url, headers=HEADERS, data=data)
    )

    reg = '教習生'
    if re.search(reg, res.text):
        return res.cookies

    return None
