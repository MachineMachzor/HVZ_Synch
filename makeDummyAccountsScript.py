# import requests


# print("Passwords = usernames, these lists are USERNAMES")
# dummyAccs = [f"dummy{i}" for i in range(1,11)]
# print(dummyAccs)
# adminAccs = ['admin', 'allisonB', 'chrisC', 'gabeV', 'jamesG', 'johnD', 'jordanM', 'katieK', 'tannerF'] 
# print(adminAccs)
# for dummyAcc in dummyAccs:
#     url = "http://127.0.0.1:8000/apiVerifyRegister"
#     payload = {
#         "username": dummyAcc,
#         "password": dummyAcc,
#         "passwordReenter": dummyAcc
#     } #Register all dummies
#     reqTxt = requests.post(url, json=payload)
#     print(reqTxt.text)

# presidents = ['admin', 'jamesG', 'jordanM']


# for adminAcc in adminAccs:
#     url = "http://127.0.0.1:8000/apiVerifyRegister"
#     payload = {
#         "username": adminAcc,
#         "password": adminAcc,
#         "passwordReenter": adminAcc
#     } #Register all admins
#     reqTxt = requests.post(url, json=payload)
#     print(reqTxt.text)

#     url = "http://127.0.0.1:8000/makeAdmin" #Make all admins, admins 
#     payload = {
#         "username": adminAcc,
#         "webPass": "t2]9k4%,AyW$k}fU",
#         "makeAdmin": True
#     }
#     reqTxt = requests.post(url, json=payload)
#     print(reqTxt.text)

#     if adminAcc in presidents:
#         url = "http://127.0.0.1:8000/makePresidentOrVP" #Make all admins, admins 
#         payload = {
#             "username": adminAcc,
#             "webPass": "t2]9k4%,AyW$k}fU",
#             "makeAdmin": True
#         }
#         reqTxt = requests.post(url, json=payload)
#         print(reqTxt.text)



import requests


print("Passwords = usernames, these lists are USERNAMES")
dummyAccs = [f"dummy{i}" for i in range(1,11)]
print(dummyAccs)
adminAccs = ['admin'] 
print(adminAccs)
for dummyAcc in dummyAccs:
    url = "http://127.0.0.1:8000/apiVerifyRegister"
    payload = {
        "username": dummyAcc,
        "password": dummyAcc,
        "passwordReenter": dummyAcc
    } #Register all dummies
    reqTxt = requests.post(url, json=payload)
    print(reqTxt.text)


adminAccs = ['eboard', 'admin'] 
presidents = ['admin']


#eboard, then admin pass
passwords = ['justForEboard', 'aVerySecurePassword']


for adminAcc in adminAccs:
    url = "http://127.0.0.1:8000/apiVerifyRegister"
    payload = {
        "username": adminAcc,
        "password": passwords[adminAccs.index(adminAcc)],
        "passwordReenter": passwords[adminAccs.index(adminAcc)]
    } #Register all admins
    reqTxt = requests.post(url, json=payload)
    print(reqTxt.text)

    url = "http://127.0.0.1:8000/makeAdmin" #Make all admins, admins 
    payload = {
        "username": adminAcc,
        "webPass": "t2]9k4%,AyW$k}fU",
        "makeAdmin": True
    }
    reqTxt = requests.post(url, json=payload)
    print(reqTxt.text)

    if adminAcc in presidents:
        url = "http://127.0.0.1:8000/makePresidentOrVP" #Make all admins, admins 
        payload = {
            "username": adminAcc,
            "webPass": "t2]9k4%,AyW$k}fU",
            "makeAdmin": True
        }
        reqTxt = requests.post(url, json=payload)
        print(reqTxt.text)