class Metadata(object):
    url_base = ''
    cache_timeout = 60 * 60 * 2

    def __init__(self, api):
        self._api = api


class MetadataList(Metadata):
    class List(object):
        def __init__(self, data):
            self._data = data

    list_class = List

    def list(self, name=None, model=None, limit=None, offset=None):
        if name is not None:
            url = self.url_base + '/' + name
        else:
            url = self.url_base
        if model is None:
            model = self.list_class
        return self._api.get_list(model, url, limit=limit, offset=offset, cache_timeout=self.cache_timeout)


class MetadataDetail(Metadata):
    class Detail(object):
        def __init__(self, data):
            self._data = data

    url_base = ''
    detail_class = Detail

    def detail(self, obj_id, model=None):
        if model is None:
            model = self.detail_class
        return self._api.get_detail(model, self.url_base, obj_id, cache_timeout=self.cache_timeout)
