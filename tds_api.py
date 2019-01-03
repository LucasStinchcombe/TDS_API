# coding=utf-8
"""
Toyota Driving School API
"""
import re
import requests
from constants import HEADERS, DATA
from utils import toyota_req, get_datetime

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
    params.update(DATA)

    res = toyota_req(
        requests.get(url,
                     headers=HEADERS,
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

        session_dt = get_datetime(int(match.group(2)),
                                  int(match.group(3)))
        retval.append({
            "date": session_dt,
            "schedule": list(match.group(4).replace(' ', '')),
            "car_model_cd": car_model_cd
        })

    return sorted(retval, key=lambda x: x["date"])

def register(cookies, session, period_idx):
    """
    Register for section for month, day period.

    :param date: datetime date object
    :param session: session returned from get_availability()
    :param period_idx: index in session schedule of period to register
    """

    register_date = session['date']
    car_model_cd = session['car_model_cd']

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

    params.update(DATA)
    token_res = toyota_req(
        requests.get(token_url,
                     params=params,
                     headers=HEADERS,
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

    res = toyota_req(
        requests.post(register_url,
                      headers=HEADERS,
                      data=data,
                      cookies=cookies)
    )

    if re.search('<font class="error"><BR>！', res.text):
        return False

    return res

def get_cancel_choices(cookies):
    """
    Get choices for cancel.

    :param cookies: cookies from login()
    """
    url = 'https://www.e-license.jp/el25/mobile/m02a.action'

    params = {
        'b.processCd': 'F',
    }

    params.update(DATA)
    res = toyota_req(
        requests.get(url,
                     headers=HEADERS,
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

        session_dt = get_datetime(int(match.group(3)),
                                  int(match.group(4)),
                                  int(match.group(5)),
                                  int(match.group(6)))

        retval.append({
            'datetime': session_dt,
            'reserved_cds':reserved_cds,
            'checkbox_reserved_cds': checkbox_reserved_cds
        })

    return sorted(retval, key=lambda x: x['datetime'])

def cancel(cookies, session):
    """
    Cancel session from cancel_choices()

    :param cookies: cookies from login()
    """

    url = 'https://www.e-license.jp/el25/mobile/m14a.action'

    data = {
        'b.naiyousentakuCd': 0,
        'reservedCds': session['reserved_cds'],
        '__checkbox_reservedCds': session['checkbox_reserved_cds'],
        'method\x3AdoDelete': '\x8E\xC0\x8Ds',
        'b.page': 1
    }

    data.update(DATA)
    res = toyota_req(
        requests.post(url,
                      headers=HEADERS,
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
        'b.reservedCd': session['reserved_cds'],
        'b.page': 1,
        'b.naiyousentakuCd': 0
    }

    url = 'https://www.e-license.jp/el25/mobile/m14b.action'
    data.update(DATA)

    res = toyota_req(
        requests.post(url,
                      headers=HEADERS,
                      data=data,
                      cookies=cookies))

    if not re.search('ｷｬﾝｾﾙしました', res.text):
        return False

    return res
