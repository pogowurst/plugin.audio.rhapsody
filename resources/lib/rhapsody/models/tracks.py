from metadata import *


class Base(object):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        try:
            self.duration = data['duration']
        except KeyError:
            try:
                self.duration = data['playbackSeconds']
            except KeyError:
                self.duration = None


class List(Base):
    def __init__(self, data):
        import albums
        import artists

        super(List, self).__init__(data)
        self.artist = artists.Base(data['artist'])
        self.album = albums.Base(data['album'])


class Detail(List):
    def __init__(self, data):
        super(Detail, self).__init__(data)


class Tracks(MetadataList, MetadataDetail):
    url_base = 'tracks'
    list_class = List
    detail_class = Detail

    def top(self):
        return self.list('top')
