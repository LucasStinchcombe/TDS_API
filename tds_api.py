# coding=utf-8
"""
Toyota Driving School API
"""

from datetime import datetime

import re
import requests

_HEADERS = {
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

_DATA = {
    'b.wordsStudentNo': '\x8b\xb3\x8f\x4b\x90\xb6\x94\xd4\x8d\x86',
    'b.schoolCd': 'LAtcyKgwukI\x2BbrGQYS\x2B1OA\x3D\x3D',
    'server': '',
}


def _toyota_req(res):
    """
    Filters out expired session responses.
    """
    res.encoding = 'shift_jis'

    if re.search('接続を切りました', res.text):
        return None

    return res


def _get_datetime(month, day, hour=0, minute=0):
    """
    Get datetime given just month, day, hour.

    Toyota Driving School website does not display year so it is infered
    from current year and month displayed.
    """

    cur_year = datetime.now().year
    cur_month = datetime.now().month

    year = cur_year
    if cur_month == 12 and month != 12:
        year += 1

    return datetime(year, month, day, hour, minute)


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

    data.update(_DATA)
    res = _toyota_req(
        requests.post(url, headers=_HEADERS, data=data)
    )

    reg = '教習生'
    if re.search(reg, res.text):
        return res.cookies

    return None


def get_availability(cookies):
    """
    get availability.

    :param cookies: cookies from login()
    :return context: array of tuple (date, schedule, car_model_cd) \
            sorted by date
    """

    url = 'https://www.e-license.jp/el25/mobile/m02a.action'

    params = {
        'b.processCd' : 'A',
        'b.kamokuCd': '0',
    }

    params.update(_DATA)

    res = _toyota_req(
        requests.get(url,
                     headers=_HEADERS,
                     params=params,
                     cookies=cookies)
    )

    if not res:
        return None

    date_reg = r'(.*)月(.*)日\(.*\)'
    sched_reg = r'([XO -J]*)'
    reg = (r'<a href=.*b\.carModelCd=([0-9]*).*>' + date_reg + '</a>'
           + '<br>[\r\t\n]*' + sched_reg + '<br>')

    retval = []
    for match in re.finditer(reg, res.text):
        car_model_cd = match.group(1)

        month = int(match.group(2))
        day = int(match.group(3))

        session_dt = _get_datetime(month, day)

        retval.append((session_dt,
                       list(match.group(4).replace(' ', '')),
                       car_model_cd))

    return sorted(retval, key=lambda x: x[0])


def register(cookies, session, period_idx):
    """
    Register for section for month, day period.

    :param date: datetime date object
    :param session: session returned from get_availability()
    :param period_idx: index in session schedule of period to register
    """

    register_date = session[0]
    car_model_cd = session[2]

    date_string = register_date.strftime('%Y%m%d')
    token_url = 'https://www.e-license.jp/el25/mobile/m03d.action'
    params = {
        'b.carModelCd': car_model_cd,
        'b.infoPeriodNumber': period_idx + 1,
        'b.dateInformationType': date_string,
        'b.instructorCd': 0,
        'b.page': 1,
        'b.instructorTypeCd': 0,
        'b.groupCd': 1,
        'b.processCd': 'V',
        'b.kamokuCd': 0,
        'b.nominationInstructorCd': 0
    }

    params.update(_DATA)
    token_res = _toyota_req(
        requests.get(token_url,
                     params=params,
                     headers=_HEADERS,
                     cookies=cookies)
    )

    if not token_res:
        return None

    token = re.search('<input type="hidden" ' \
                      'name="token" value="(.*)" />',
                      token_res.text).group(1).encode('shift_jis')

    register_url = 'https://www.e-license.jp/el25/mobile/m03e.action'

    data = {
        'struts.token.name': 'token',
        'token': token,
        'method\x3AdoYes': '\x82\xCD\x82\xA2',
        'b.changeInstructorFlg': 0
    }
    data.update(params)

    return _toyota_req(
        requests.post(register_url,
                      headers=_HEADERS,
                      data=data,
                      cookies=cookies)
    )


def cancel_choices(cookies):
    """
    Get choices for cancel.

    :param cookies: cookies from login()
    """
    url = 'https://www.e-license.jp/el25/mobile/m02a.action'

    params = {
        'b.processCd': 'F',
    }

    params.update(_DATA)
    res = _toyota_req(
        requests.get(url,
                     headers=_HEADERS,
                     params=params,
                     cookies=cookies)
    )

    if not res:
        return None

    input_reg = '<input .* value="([0-9]*)" .*>'
    date_reg = '<font .*>([0-9]*)/([0-9]*) ([0-9]*):([0-9]*).*</font>'
    reg = ('<td.*>.*' + input_reg + input_reg + '</td>' +
           '[\r\t\n]*<td>' + date_reg + '</td>')

    retval = []
    for match in re.finditer(reg, res.text):
        reserved_cds = match.group(1)
        checkbox_reserved_cds = match.group(2)

        session_dt = _get_datetime(int(match.group(3)),
                                   int(match.group(4)),
                                   int(match.group(5)),
                                   int(match.group(6)))

        retval.append((session_dt, reserved_cds, checkbox_reserved_cds))

    return sorted(retval, key=lambda x: x[0])


def cancel(cookies, session):
    """
    Cancel session from cancel_choices()

    :param cookies: cookies from login()
    """

    url = 'https://www.e-license.jp/el25/mobile/m14a.action'

    data = {
        'b.naiyousentakuCd': 0,
        'reservedCds': session[1],
        '__checkbox_reservedCds': session[2],
        'method\x3AdoDelete': '\x8E\xC0\x8Ds',
        'b.page': 1
    }

    data.update(_DATA)
    res = _toyota_req(
        requests.post(url,
                      headers=_HEADERS,
                      data=data,
                      cookies=cookies))

    if not res:
        return None

    reg_token = '<input .* name="token" value="(.*)" .*/>'
    token = re.search(reg_token, res.text).group(1).encode('shift_jis')

    data = {
        'struts.token.name': 'token',
        'token': token,
        'method\x3AdoDelete': '\x82\xCD\x82\xA2',
        'b.reservedCd': session[1],
        'b.page': 1,
        'b.naiyousentakuCd': 0
    }

    url = 'https://www.e-license.jp/el25/mobile/m14b.action'
    data.update(_DATA)
    return _toyota_req(
        requests.post(url,
                      headers=_HEADERS,
                      data=data,
                      cookies=cookies))
