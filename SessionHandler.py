import secrets

class Session_Handler(object):
    def __init__(self):
        self.sessions = []

    def findUser(self, user):
        i = 0
        for s in self.sessions:
            if s[1] == user:
                return i
            else:
                i += 1
        if i >= len(self.sessions):
            return False

    def add_session(self, user):
        i= self.findUser(user)
        if i is False:
            self.sessions.append([secrets.token_hex(16), user])
        else:
            self.sessions[i] = [secrets.token_hex(16), user]

        return

    def find_user_token(self,user):
        for s in self.sessions:
            if s[1] == user:
                return s[0]
        return False

    def find_user_by_token(self, token):
        for s in self.sessions:
            if s[0] == token:
                return s[1]
        return False
