import threading

def my_func(session_cookie) :
    session_cookie.append("abcd")
    return session_cookie


session_cookie = []

thread = threading.Thread(target=my_func, args=(session_cookie,))
thread.start()
thread.join()

print(session_cookie)