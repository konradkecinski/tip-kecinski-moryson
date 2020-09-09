class WRTCHandler(object):

    def __init__(self):
        self.sessions = []

    def findUser(self, user):
        i = 0
        for s in self.sessions:
            if s[2] == user:
                return i
            else:
                i += 1
        if i >= len(self.sessions):
            return False

    def add_session(self, user, sid, ip):
        i = self.findUser(user)
        if i is False:
            self.sessions.append([sid, user, user, ip])
        else:
            self.sessions[i] = [sid, user, user, ip]

        return True

    def find_user_room(self, user):
        for s in self.sessions:
            if s[2] == user:
                return s[1]
        return False

    def find_user_sid(self, user):
        for s in self.sessions:
            if s[2] == user:
                return s[0]
        return False

    def find_user_by_sid(self, sid):
        for s in self.sessions:
            if s[0] == sid:
                return s[2]
        return False

    def change_room(self, user, room):
        i = self.findUser(user)
        if i is False:
            return False
        else:
            self.sessions[i] = [self.sessions[i][0], room, user, self.sessions[i][3]]