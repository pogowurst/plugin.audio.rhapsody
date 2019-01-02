from __future__ import unicode_literals

import datetime

from kodiswift import xbmc


class Notify(object):
    track = None
    stream = None
    playback_started_time = None
    playback_stopped_time = None

    def __init__(self, rhapsody, track, stream):
        self.rhapsody = rhapsody
        self.track = track
        self.stream = stream

    def playback_started(self):
        if self.playback_started_time is None:
            self.rhapsody.events.log_playstart(self.track.id, self.stream)
            self.playback_started_time = datetime.datetime.utcnow()

    def playback_stopped(self):
        if self.playback_started_time is not None and self.playback_stopped_time is None:
            self.playback_stopped_time = datetime.datetime.utcnow()
            self.rhapsody.events.log_playstop(self.track.id, self.stream, self.playback_started_time)

    def is_playback_completed(self):
        return self.playback_started_time is not None and self.playback_stopped_time is not None


class Player(xbmc.Player):
    has_started = False
    has_stopped = False

    def __init__(self, **kwargs):
        self.plugin = kwargs.pop('plugin')
        self.notify = kwargs.pop('notify')
        super(Player, self).__init__()

    def onPlayBackStarted(self):
        if not self.has_started:
            self.has_started = True
            self.plugin.log.info('Player: onPlayBackStarted')
            self.notify.playback_started()
        else:
            self.plugin.log.info('Player: Kodi is playing a new track but didn\'t notify us the previous one has ended')
            self.onPlayBackEnded()

    def onPlayBackEnded(self):
        if not self.has_stopped:
            self.plugin.log.info('Player: onPlayBackEnded')
            self.has_stopped = True
            self.notify.playback_stopped()

    def onPlayBackStopped(self):
        self.onPlayBackEnded()
