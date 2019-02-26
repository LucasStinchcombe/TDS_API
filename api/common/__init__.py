"""
common module
"""
import re
import requests

from api.common.constants import HEADERS, DATA
from api.common.utils import toyota_req, get_datetime

# HELPER for cancel
def _get_cancel_meta(cookies, session):
    """
    Get meta data for cancel

    :param cookies: cookies
    :param session: session to cancel
    """
    url = 'https://www.e-license.jp/el25/mobile/m02a.action'

    params = {
        'b.processCd': 'F',
    }

    #pylint: disable=duplicate-code
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

    for match in re.finditer(reg, res.text):
        session_dt = get_datetime(int(match.group(3)),
                                  int(match.group(4)),
                                  int(match.group(5)),
                                  int(match.group(6)))

        if session_dt == session['datetime']:
            session['reserved_cds'] = match.group(1)
            session['checkbox_reserved_cds'] = match.group(2)
            return session

    return None
