from metadata import *
from rhapsody import exceptions


class Detail(object):
    def __init__(self, data):
        self.url = data['url']
        self.bitrate = data['bitrate']
        self.format = data['format']


class Streams(MetadataDetail):
    url_base = 'play'
    detail_class = Detail
    cache_timeout = 600

    def detail(self, obj_id, **kwargs):
        if not self._api.is_authenticated():
            raise exceptions.StreamingRightsError
        if not self._api.account.can_stream_on_home_device:
            raise exceptions.StreamingRightsError
        if not self._api.account.can_stream_on_mobile:
            raise exceptions.StreamingRightsError
        if not self._api.account.can_stream_on_pc:
            raise exceptions.StreamingRightsError
        if not self._api.account.can_stream_on_web:
            raise exceptions.StreamingRightsError

        if self._api.ENABLE_RTMP:
            if not self._api.validate_session():
                raise exceptions.StreamingRightsError
            else:
                return super(Streams, self).detail(obj_id + '?web=True&context=ON_DEMAND&sessionId={0:s}'.format(
                    self._api.session.id
                ))
        else:
            return super(Streams, self).detail(obj_id)
