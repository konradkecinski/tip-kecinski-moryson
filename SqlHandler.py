import pyodbc
import EncryptionHandler
import collections
import json

AES = EncryptionHandler.AES_Handler('test')


class SQL_Handler(object):
    def __init__(self):
        None

    def executeQuery(self, query):
        conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=.\KONRADKSQL;'
                              'Database=TIP;'
                              'Trusted_Connection=yes;')
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.cancel()
        conn.close()
        return data

    def executeModify(self, query):
        conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=.\KONRADKSQL;'
                              'Database=TIP;'
                              'Trusted_Connection=yes;')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.cancel()
        conn.close()

    def insertUserTemplate(self, name, mail, passwd):
        return "INSERT INTO users (name, passwd, mail, creation_timestamp, last_login)" \
               "VALUES('{0}','{1}','{2}',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);".format(name, AES.encrypt(passwd), mail)

    def getIdTemplate(self, name):
        return "SELECT id FROM users WHERE name='{0}';".format(name)

    def approveTemplate(self,name1, name2):
        id1 = self.executeQuery(self.getIdTemplate(name1))[0][0]
        id2 = self.executeQuery(self.getIdTemplate(name2))[0][0]
        return "UPDATE friends SET approved=0 WHERE id_user={0} AND id_friend={1}".format(id1, id2)

    def insertFriendsTemplate(self, name1, name2):
        id1 = self.executeQuery(self.getIdTemplate(name1))[0][0]
        id2 = self.executeQuery(self.getIdTemplate(name2))[0][0]
        return "INSERT INTO friends (id_user, id_friend, approved, timestamp)" \
               "VALUES({0},{1},0,CURRENT_TIMESTAMP);".format(id1, id2)

    def checkPasswdTemplate(self, name):
        return "SELECT passwd from users WHERE name = '{0}'".format(name)

    def getFriendsTemplate(self, name):
        return """SELECT CASE 
WHEN x.name1 = '{0}'
THEN x.name2 
ELSE x.name1 
END as friend_name 
FROM 
(SELECT t.name1, u.name name2 
FROM users u LEFT JOIN 
(SELECT u.name name1, f.id_friend 
FROM users u LEFT JOIN friends f 
ON u.id = f.id_user WHERE f.approved = 0) t 
ON u.id = t.id_friend) x
WHERE x.name1 is NOT NULL
AND x.name2 is NOT NULL""".format(name)

    def addUser(self, name, mail, passwd):
        self.executeModify(self.insertUserTemplate(name, mail, passwd))

    def addFriends(self, name1, name2):
        self.executeModify(self.insertFriendsTemplate(name1, name2))

    def approveInvitation(self, name1, name2):
        self.executeModify(self.approveTemplate(name1, name2))

    def checkPasswd(self, user, passwd):
        correct_passwd = self.executeQuery(self.checkPasswdTemplate(user))[0][0]
        correct_passwd = AES.decrypt(correct_passwd)
        if correct_passwd == passwd:
            return True
        else:
            return False

    def getFriends(self, user):
        return self.executeQuery(self.getFriendsTemplate(user))

    def friends_to_json(self, data, new_token):
        objects_list = []
        token_d = collections.OrderedDict()
        token_d['token'] = new_token
        objects_list.append(token_d)
        for row in data:
            d = collections.OrderedDict()
            d['friend_name'] = row.friend_name
            objects_list.append(d)
        j = json.dumps(objects_list)
        return j
