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

    def add_session(self, user, ip):
        i= self.findUser(user)
        if i is False:
            self.sessions.append([secrets.token_hex(16), user, ip])
        else:
            self.sessions[i] = [secrets.token_hex(16), user, ip]

        return True

    def find_user_token(self, user):
        for s in self.sessions:
            if s[1] == user:
                return s[0]
        return False

    def find_user_by_token(self, token):
        for s in self.sessions:
            if s[0] == token:
                return s[1]
        return False

    def find_user_ip(self, user):
        for s in self.sessions:
            if s[1] == user:
                return s[2]
        return False

    def find_user_by_ip(self, ip):
        for s in self.sessions:
            if s[2] == ip:
                return s[1]
        return False
