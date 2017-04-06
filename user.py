# Class User

class User():
    def __init__(self, username="", passwd="", dni="", id=""):
        self._username = username
        self._passwd = passwd
        self._dni = dni
        self._id = id

    @property
    def getUsername(self):
        return self._username

    @property
    def getPasswd(self):
        return self._passwd

    @property
    def getDni(self):
        return self._dni

    @property
    def getId(self):
        return self._id

    def setUsername(self, x):
        self._username = x

    def setPasswd(self, x):
       self._passwd = x

    def setDni(self, x):
        self._dni = x

    def setId(self, x):
        self._id = x

