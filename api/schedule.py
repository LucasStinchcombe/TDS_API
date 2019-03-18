"""
Schedule
"""
import re
from datetime import datetime, timedelta
import requests

from api.common.constants import HEADERS, DATA
from api.common.utils import toyota_req, get_datetime
from api.common import _get_cancel_meta

SESSION_START_TIMES = [timedelta(hours=7, minutes=50),
                       timedelta(hours=8, minutes=50),
                       timedelta(hours=9, minutes=50),
                       timedelta(hours=10, minutes=50),
                       timedelta(hours=11, minutes=50),
                       timedelta(hours=12, minutes=50),
                       timedelta(hours=13, minutes=50),
                       timedelta(hours=14, minutes=50),
                       timedelta(hours=16, minutes=00),
                       timedelta(hours=17, minutes=00),
                       timedelta(hours=18, minutes=00),
                       timedelta(hours=19, minutes=00),
                       timedelta(hours=20, minutes=00)]

SESSION_IDX = {}
#pylint: disable=consider-using-enumerate
for j in range(len(SESSION_START_TIMES)):
    SESSION_IDX[SESSION_START_TIMES[j]] = j + 1


def get(cookies):
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

    #pylint: disable=R0801
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
    reg = (r'<a href=.*b\.carModelCd=([0-9]*).*'
           + 'b\.groupCd=([0-9]*).*>' + date_reg + '</a>'
           + '<br>[\r\t\n]*' + sched_reg + '<br>')

    retval = []
    for match in re.finditer(reg, res.text):
        car_model_cd = match.group(1)
        group_cd = match.group(2)

        session_dt = get_datetime(int(match.group(3)),
                                  int(match.group(4)))

        sessions = list(match.group(5).replace(' ', ''))
        for i in range(len(sessions)):
            if sessions[i] != 'X':
                retval.append({
                    'datetime': session_dt + SESSION_START_TIMES[i],
                    'car_model_cd': car_model_cd,
                    'group_cd': group_cd,
                    'status': sessions[i]
                })

    retval.sort(key=lambda x: x['datetime'])
    return retval


def register(cookies, session):
    """
    Register for section for month, day period.

    :param date: datetime date object
    :param session: session returned from availability.get()
    """

    date_string = session['datetime'].strftime('%Y%m%d')
    time_delta = (session['datetime']
                  - datetime(year=session['datetime'].year,
                             month=session['datetime'].month,
                             day=session['datetime'].day))

    session_idx = SESSION_IDX[time_delta]
    token_url = 'https://www.e-license.jp/el25/mobile/m03d.action'
    params = {
        'b.carModelCd': session['car_model_cd'],
        'b.infoPeriodNumber': session_idx,
        'b.dateInformationType': date_string,
        'b.instructorCd': 0,
        'b.page': 1,
        'b.instructorTypeCd': 0,
        'b.processCd': 'V',
        'b.kamokuCd': 0,
        'b.nominationInstructorCd': 0,
        'b.groupCd': session['group_cd']
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
        'b.changeInstructorFlg': 0,
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


def cancel(cookies, session):
    """
    Cancel session

    :param cookies: cookies from login()
    :param session: session
    """

    session = _get_cancel_meta(cookies, session)

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
