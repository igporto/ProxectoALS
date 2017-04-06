# Class Book

class Book():
    def __init__(self, author, title, genre, front, synopsis, id):
        self._author = author
        self._title = title
        self._genre = genre
        self._front = front
        self._synopsis = synopsis
        self._id = id

    @property
    def getAuthor(self):
        return self._author

    @property
    def getTitle(self):
        return self._title

    @property
    def getGenre(self):
        return self._genre

    @property
    def getFront(self):
        return self._front

    @property
    def getSynopsis(self):
        return self._synopsis

    def getId(self):
        return self._id

    def setAuthor(self, x):
        self._author = x

    def setTitle(self, x):
        self._title = x

    def setGenre(self, x):
        self._genre = x

    def setFront(self, x):
        self._front = x

    def setSynopsis(self, x):
        self._synopsis = x

    def setId(self, x):
        self._id =x

