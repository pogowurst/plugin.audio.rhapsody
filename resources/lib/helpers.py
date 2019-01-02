from __future__ import absolute_import, division, unicode_literals

from kodiswift import actions

from rhapsody.api import API
from rhapsody.cache import Base as BaseCache
from rhapsody.models.common import Image


class Helpers:
    class Cache(BaseCache):
        def __init__(self, plugin):
            self._plugin = plugin
            self.storages = {}

        def get_storage(self, timeout):
            timeout = int(timeout / 60)
            if timeout not in self.storages:
                self.storages[timeout] = self._plugin.get_storage('rhapsody.{0:d}'.format(timeout), ttl=timeout)
            return self.storages[timeout]

        def get(self, key, timeout):
            storage = self.get_storage(timeout)
            return storage.get(key)

        def set(self, key, value, timeout):
            storage = self.get_storage(timeout)
            storage[key] = value
            storage.close()

        def cleanup(self):
            del self._plugin

    def __init__(self, plugin):
        self._plugin = plugin
        self._cache = Helpers.Cache(plugin)
        self._api = None

    def get_artist_item(self, artist, in_library=False):
        item = {
            'label': artist.name,
            'thumbnail': Image.get_url(Image.TYPE_ARTIST, artist.id, Image.SIZE_ARTIST_ORIGINAL),
            'properties': {
                'fanart_image': Image.get_url(Image.TYPE_ARTIST, artist.id, Image.SIZE_ARTIST_ORIGINAL),
            },
            'context_menu': [],
        }

        if in_library:
            item['path'] = self._plugin.url_for('artists_library_albums', artist_id=artist.id)
            item['context_menu'].append((
                self._plugin.get_string(30217),
                actions.update_view(self._plugin.url_for('artists_library_remove', artist_id=artist.id))))
        else:
            item['path'] = self._plugin.url_for('artists_detail', artist_id=artist.id)
            item['context_menu'].append((
                self._plugin.get_string(30215),
                actions.background(self._plugin.url_for('artists_library_add', artist_id=artist.id))))

        return item

    def get_album_item(self, album, show_artist=True, in_library=False, library_artist_id=None):
        label = album.name + ' (' + str(album.get_release_date().year) + ')'
        if show_artist:
            label += '[LIGHT] / ' + album.artist.name + '[/LIGHT]'
        item = {
            'label': label,
            'thumbnail': Image.get_url(Image.TYPE_ALBUM, album.id, Image.SIZE_ALBUM_ORIGINAL),
            'properties': {
                'fanart_image': Image.get_url(Image.TYPE_ARTIST, album.artist.id, Image.SIZE_ARTIST_ORIGINAL),
            },
            'context_menu': []
        }

        if in_library:
            item['path'] = self._plugin.url_for('albums_library_tracks', album_id=album.id)
            if library_artist_id is None:
                action = actions.update_view(self._plugin.url_for('albums_library_remove',
                                                                  album_id=album.id))
            else:
                action = actions.update_view(self._plugin.url_for('artists_library_albums_remove',
                                                                  artist_id=library_artist_id,
                                                                  album_id=album.id))
            item['context_menu'].append((self._plugin.get_string(30217), action))
        else:
            item['path'] = self._plugin.url_for('albums_detail', album_id=album.id)
            item['context_menu'].append((
                self._plugin.get_string(30215),
                actions.background(self._plugin.url_for('albums_library_add', album_id=album.id))))
        return item

    def get_genre_item(self, genre):
        item = {
            'label': genre.name,
            'path': self._plugin.url_for('genres_detail', genre_id=genre.id),
            'thumbnail': Image.get_url(Image.TYPE_GENRE, genre.id, Image.SIZE_GENRE_ORIGINAL),
            'properties': {
                'fanart_image': Image.get_url(Image.TYPE_GENRE, genre.id, Image.SIZE_GENRE_ORIGINAL),
            }
        }
        return item

    def get_playlist_item(self, playlist, in_library=False):
        item = {
            'label': playlist.name,
            'path': self._plugin.url_for('playlists_detail', playlist_id=playlist.id),
            'thumbnail': Image.get_url(Image.TYPE_PLAYLIST, playlist.id, Image.SIZE_PLAYLIST_ORIGINAL),
            'properties': {
                'fanart_image': Image.get_url(Image.TYPE_PLAYLIST, playlist.id, Image.SIZE_PLAYLIST_ORIGINAL),
            }
        }
        if in_library:
            item['path'] = self._plugin.url_for('playlists_library_detail', playlist_id=playlist.id)
            item['context_menu'] = [
                (
                    self._plugin.get_string(30251),
                    actions.update_view(self._plugin.url_for('playlists_library_rename', playlist_id=playlist.id))
                ),
                (
                    self._plugin.get_string(30252),
                    actions.update_view(self._plugin.url_for('playlists_library_remove', playlist_id=playlist.id))
                )
            ]
        return item

    def get_track_item(self, track, track_number=None, show_artist=True, in_library=False, in_favorites=False,
                       in_playlists=False, playlist_id=None, library_album_id=None):
        label = track.name
        if show_artist:
            label += '[LIGHT] / ' + track.artist.name + '[/LIGHT]'
        item = {
            'label': label,
            'is_playable': True,
            'info': {
                'title': track.name,
                'artist': track.artist.name,
                'album': track.album.name,
                'duration': track.duration
            },
            'thumbnail': Image.get_url(Image.TYPE_ALBUM, track.album.id, Image.SIZE_ALBUM_ORIGINAL),
            'properties': {
                'fanart_image': Image.get_url(Image.TYPE_ARTIST, track.artist.id, Image.SIZE_ARTIST_ORIGINAL),
            },
            'context_menu': []
        }
        if track_number is not None:
            item['info']['tracknumber'] = track_number
        item['context_menu'].append((
            self._plugin.get_string(30255).format(track.artist.name),
            actions.update_view(self._plugin.url_for('artists_detail', artist_id=track.artist.id))
        ))
        if in_library:
            if library_album_id is None:
                action = actions.update_view(self._plugin.url_for('tracks_library_remove',
                                                                  track_id=track.id))
            else:
                action = actions.update_view(self._plugin.url_for('albums_library_tracks_remove',
                                                                  track_id=track.id,
                                                                  album_id=library_album_id))
            item['context_menu'].append((self._plugin.get_string(30217), action))
        else:
            item['context_menu'].append((
                self._plugin.get_string(30215),
                actions.background(self._plugin.url_for('tracks_library_add', track_id=track.id))))
        if in_favorites:
            item['context_menu'].append((
                self._plugin.get_string(30218),
                actions.update_view(self._plugin.url_for('favorites_remove', track_id=track.id))))
        else:
            item['context_menu'].append((
                self._plugin.get_string(30216),
                actions.background(self._plugin.url_for('favorites_add', track_id=track.id))))
        if in_playlists:
            item['context_menu'].append((
                self._plugin.get_string(30254),
                actions.update_view(self._plugin.url_for('playlists_library_remove_track',
                                                         track_id=track.id, playlist_id=playlist_id))))
        else:
            item['context_menu'].append((
                self._plugin.get_string(30253),
                actions.background(self._plugin.url_for('playlists_library_select', track_id=track.id)))
            )

        item['path'] = self._plugin.url_for('play', track_id=track.id)
        return item

    def get_track_items(self, tracks, **kwargs):
        items = []
        for x in range(len(tracks)):
            items.append(self.get_track_item(tracks[x], track_number=(x + 1), **kwargs))
        return items

    def get_station_item(self, station, label=None):
        return {
            'label': (label or station.name),
            'thumbnail': Image.get_url(Image.TYPE_STATION, station.id, Image.SIZE_STATION_ORIGINAL),
            'properties': {
                'fanart_image': Image.get_url(Image.TYPE_STATION, station.id, Image.SIZE_STATION_ORIGINAL),
            },
            'path': self._plugin.url_for('stations_detail', station_id=station.id)
        }

    def get_station_items(self, stations, **kwargs):
        items = []
        for x in range(len(stations)):
            items.append(self.get_station_item(stations[x], **kwargs))
        return items

    def cleanup(self):
        self._cache.cleanup()

    def _get_api(self):
        api_key = self._plugin.get_setting('api_key', converter=unicode)
        api_secret = self._plugin.get_setting('api_secret', converter=unicode)
        rhapsody = API(api_key, api_secret, cache_instance=self._cache, log_callback=self._plugin.log.info)

        username = self._plugin.get_setting('username', converter=unicode)
        password = self._plugin.get_setting('password', converter=unicode)
        rhapsody.login(username, password)

        return rhapsody

    def get_api(self):
        if self._api is None:
            self._api = self._get_api()
        return self._api

    def get_stream(self, track_id):
        qualities = {
            'AAC+ 64kBit/s': 0,
            'AAC 192kBit/s': 1,
            'AAC 320kBit/s': 2,
        }
        quality = qualities.get(self._plugin.get_setting('api_quality', converter=str), qualities['AAC 320kBit/s'])
        while quality >= 0:
            try:
                q = self.get_api().streams.QUALITIES[quality]
                return self.get_api().streams.detail(track_id, qualtity=q).streams[0]
            except IndexError:
                self._plugin.log.info('Playback: No stream available. Retrying with reduced quality...')
                quality -= 1
        else:
            return
