import requests

import json

sessionid = None
sessionid2 = None

class APITesterClient:
    def __init__(self, serviceAddress):
        self._serviceAddress = serviceAddress

    def test_hello(self):
        response = requests.get(self._serviceAddress + '/hello')
        print("Test Hello:\n" + str(response.text))

    def test_register(self, name, mail, passwd):
        json_to_send = {
            "name" : name,
            "mail" : mail,
            "password" : passwd
        }
        mypost = requests.post(self._serviceAddress + '/register', json=json_to_send)
        print("POST /register")
        print(mypost.text)

    def test_login(self, name, passwd):
        json_to_send = {
            "name": name,
            "password": passwd
        }
        mypost = requests.post(self._serviceAddress + '/login', json=json_to_send)
        print("POST /login")
        print(mypost.text)
        return mypost.text

    def test_add_friend(self, session, friend):
        json_to_send = {
            "token": session,
            "friend": friend
        }
        mypost = requests.post(self._serviceAddress + '/friends', json=json_to_send)
        print("POST /friends")
        print(mypost.text)
        return mypost.text

    def test_approve_friend(self, session, friend):
        json_to_send = {
            "token": session,
            "friend": friend
        }
        mypost = requests.post(self._serviceAddress + '/approve', json=json_to_send)
        print("POST /approve")
        print(mypost.text)
        return mypost.text

    def test_get_friends(self, session):
        response = requests.get(self._serviceAddress + '/friends/' + str(session))
        print("GET /friends")
        print(response.text)
        return json.loads(response.text)["token"]

    def test_get_notifications(self, session):
        response = requests.get(self._serviceAddress + '/notifications?token=' + str(session))
        print("GET /notifications")
        print(response.text)
        return json.loads(response.text)["token"]

tester = APITesterClient("http://localhost:5000")
tester.test_hello()
#tester.test_register('konrad', 'jakismail@op.pl', 'haslo123')
#tester.test_register('konrad3', 'jakismail2@op.pl', 'haslo123')
sessionid = tester.test_login('konrad', 'haslo123')
sessionid = tester.test_add_friend(sessionid, 'konrad3')
sessionid2 = tester.test_login('konrad3', 'haslo123')
#sessionid2 = tester.test_approve_friend(sessionid2, 'konrad')
sessionid2 = tester.test_get_notifications(sessionid2)
