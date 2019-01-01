from metadata import *


class Stations(MetadataList, MetadataDetail):
    class Base(object):
        def __init__(self, data):
            self.id = data['id']
            self.name = data['name']
            self.type = data['type']
            self.artists = data['artists']
            try:
                self.summary = data['summary']
            except KeyError:
                self.summary = None
            try:
                self.description = data['description']
            except KeyError:
                self.description = None
            self.images = data['images']

    class List(Base):
        def __init__(self, data):
            super(Stations.List, self).__init__(data)

    class Detail(Base):
        def __init__(self, data):
            super(Stations.Detail, self).__init__(data)

    url_base = 'stations'
    list_class = List
    detail_class = Detail

    def top(self):
        return self.list('top')

    def decade(self):
        return self.list('decade')

    def tracks(self, station_id, offset=0, count=5):
        return self._api.stations_tracks.detail(station_id, params={'offset': offset, 'count': count})


class StationsTracks(MetadataDetail):
    class StationTrack(object):
        class Parameters(object):
            def __init__(self, data):
                self.id = data['id']
                self.display_preview_limit = data['displayPreviewLimit']
                self.is_tunable = data['isTunable']
                self.skip_limit = data['skipLimit']
                self.skip_limit_duration = data['skipLimitDuration']
                self.popularity = data['popularity']
                self.variety = data['variety']

        def __init__(self, data):
            import tracks

            self.parameters = StationsTracks.StationTrack.Parameters(data['stationParameters'])
            self.tracks = [tracks.Tracks.List(x) for x in data['tracks']]

    url_base = 'stations'
    detail_class = StationTrack
    cache_timeout = None

    def detail(self, obj_id, model=None, **kwargs):
        params = kwargs.get('params', dict())
        return super(StationsTracks, self).detail(obj_id + '/tracks', params=params)
