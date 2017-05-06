# Class Writer

class Writer():
    def __init__(self, name, surname, id, wikiEntry, website):
        self._name = name
        self._surname = surname
        self._id = id
        self._wikiEntry = wikiEntry
        self._website = website

    @property
    def getName(self):
        return self._name

    @property
    def getSurname(self):
        return self._surname

    @property
    def getId(self):
        return self._id

    @property
    def getWikientry(self):
        return self._wikiEntry

    @property
    def getWebsite(self):
        return self._website

    def setName(self, x):
        self._name = x

    def setSurname(self, x):
        self._surname = x

    def setWikientry(self, x):
        self._wikiEntry = x

    def setWebsitet(self, x):
        self._website = x

    def setId(self, x):
        self._id =x