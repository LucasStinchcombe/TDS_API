## Toyota Driving School API

```python
import api

username = 'user'
password = 'password'

# get cookies for use with all subsequent calls
cookies = api.login(username, password)

schedule = api.schedule.get(cookies)

# a session with status 'O' is available
# 'J' means you have scheduled it.

# schedule a session
api.schedule.register(cookies, schedule[0])

# cancel a session
api.schedule.cancel(cookies, schedule[0])
```
