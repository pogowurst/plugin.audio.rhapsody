from metadata import *
from rhapsody import exceptions


class Detail(object):
    def __init__(self, data):
        self.streams = [Stream(x) for x in data['streams']]


class Stream(object):
    def __init__(self, data):
        self.format = Format(data['format'])
        self.url = data['url']


class Format(object):
    def __init__(self, data):
        self.name = data['name']
        self.bitrate = data['bitrate']
        self.sample_bits = data['sampleBits']
        self.sample_rate = data['sampleRate']


class Streams(MetadataDetail):
    FORMAT_AAC = 'AAC'
    FORMAT_AAC_PLUS = 'AAC PLUS'
    BITRATE_64 = 64
    BITRATE_192 = 192
    BITRATE_320 = 320
    QUALITIES = (
        (FORMAT_AAC_PLUS, BITRATE_64),
        (FORMAT_AAC, BITRATE_192),
        (FORMAT_AAC, BITRATE_320),
    )

    url_base = 'streams'
    detail_class = Detail
    cache_timeout = 600
    version = 'v2.2'

    def detail(self, obj_id, qualtity=QUALITIES[0], **kwargs):
        if not self._api.is_authenticated():
            raise exceptions.StreamingRightsError

        params = kwargs.get('params', dict())
        params.update({
            'track': obj_id,
            'format': qualtity[0],
            'bitrate': qualtity[1]
        })
        return super(Streams, self).detail(None, params=params)
