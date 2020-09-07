import sqlite3
import EncryptionHandler
import collections
import json

AES = EncryptionHandler.AES_Handler('test')

class SQL_Handler(object):
    def __init__(self):
        None

    def executeQuery(self, query):
        conn = sqlite3.connect(r"database.db")
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

    def executeModify(self, query):
        conn = sqlite3.connect(r"database.db")
        cursor = conn.cursor()
        print(query)
        cursor.execute(query)
        conn.commit()
        conn.close()

    def insertUserTemplate(self, name, mail, passwd):
        return "INSERT INTO users (name, passwd, mail, creation_timestamp, last_login)" \
               "VALUES('{0}','{1}','{2}',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);".format(name, AES.encrypt(passwd).decode(), mail)

    def getIdTemplate(self, name):
        return "SELECT id FROM users WHERE name='{0}';".format(name)

    def getNameTemplate(self, id):
        return "SELECT name FROM users WHERE id='{0}';".format(id)

    def approveTemplate(self, name1, name2):
        id1 = self.executeQuery(self.getIdTemplate(name1))[0][0]
        id2 = self.executeQuery(self.getIdTemplate(name2))[0][0]
        return "UPDATE friends SET approved=1 WHERE (id_user={0} AND id_friend={1}) OR (id_user={1} AND id_friend = {0})".format(id1, id2)

    def insertFriendsTemplate(self, name1, name2):
        id1 = self.executeQuery(self.getIdTemplate(name1))[0][0]
        id2 = self.executeQuery(self.getIdTemplate(name2))[0][0]
        return "INSERT INTO friends (id_user, id_friend, approved, timestamp)" \
               "VALUES({0},{1},0,CURRENT_TIMESTAMP);".format(id1, id2)

    def checkPasswdTemplate(self, name):
        return "SELECT passwd from users WHERE name = '{0}'".format(name)

    def updateLastloginTemplate(self, name):
        return " UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE name = '{0}'".format(name)

    def getFriendsTemplate(self, id):
        return """SELECT CASE
WHEN x.id1 = {0}
THEN x.name2
ELSE x.name1
END AS friend_name
FROM
(SELECT t.id1, t.name1, t.id2, u.name name2 
FROM users u LEFT JOIN
(SELECT u.id id1, u.name name1, f.id_friend id2
FROM users u LEFT JOIN
(SELECT id_user, id_friend 
FROM friends
WHERE approved = 1
AND (id_user = {0} OR  id_friend = {0})) f
ON u.id = f.id_user) t
ON u.id = t.id2) x
WHERE id1 is NOT NULL
AND id2 is NOT NULL;""".format(id)

    def getNotificationsTemplate(self, id):
        return """SELECT id_user FROM friends WHERE approved=0 AND id_friend == {0}""".format(id)

    def addUser(self, name, mail, passwd):
        otheruser= self.executeQuery(self.getIdTemplate(name))
        if len(otheruser) == 0:
            self.executeModify(self.insertUserTemplate(name, mail, passwd))
            return "Success"
        else:
            return "Fail"

    def addFriends(self, name1, name2):
        otheruser = self.executeQuery(self.getIdTemplate(name2))
        if len(otheruser) > 0:
            self.executeModify(self.insertFriendsTemplate(name1, name2))
        else:
            return "Fail"

    def approveInvitation(self, name1, name2):
        otheruser = self.executeQuery(self.getIdTemplate(name2))
        if len(otheruser) > 0:
            self.executeModify(self.approveTemplate(name1, name2))
        else:
            return "Fail"

    def checkPasswd(self, user, passwd):
        correct_passwd = self.executeQuery(self.checkPasswdTemplate(user))[0][0]
        correct_passwd = AES.decrypt(correct_passwd)
        if correct_passwd == passwd:
            return True
        else:
            return False

    def getFriends(self, user):
        id = self.executeQuery(self.getIdTemplate(user))
        if len(id) > 0:
            return self.executeQuery(self.getFriendsTemplate(id[0][0]))
        else:
            return "Fail"

    def getNotifications(self, user):
        id = self.executeQuery(self.getIdTemplate(user))
        if len(id) > 0:
            return self.executeQuery(self.getNotificationsTemplate(id[0][0]))
        else:
            return "Fail"

    def updateLastlogin(self, user):
        return self.executeModify(self.updateLastloginTemplate(user))

    def friends_to_json(self, data, new_token):
        # objects_list = []
        # token_d = collections.OrderedDict()
        # token_d['token'] = new_token
        # objects_list.append(token_d)
        # for row in data:
        #     d = collections.OrderedDict()
        #     d['friend_name'] = row.friend_name
        #     objects_list.append(d)
        # j = json.dumps(objects_list)
        j = {
            "token" : new_token,
            "friends" : []
        }
        for row in data:
            print(row)
            j["friends"].append({"name": row[0]})
        return j

    def notifications_to_json(self, data, new_token):
        j = {
            "token": new_token,
            "friends": []
        }
        for row in data:
            print(row)
            j["friends"].append({"name": self.executeQuery(self.getNameTemplate(row[0]))[0][0]})
        return j
