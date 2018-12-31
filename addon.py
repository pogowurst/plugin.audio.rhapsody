import os
import sys
import traceback
from cStringIO import StringIO

from xbmcswift2 import Plugin

plugin = Plugin()


@plugin.route('/')
def index():
    return [
        {'label': _(30200), 'path': plugin.url_for('library')},
        {'label': _(30201), 'path': plugin.url_for('search')},
        {'label': _(30202), 'path': plugin.url_for('discover')},
        {'label': _(30203), 'path': plugin.url_for('recent')},
    ]


@plugin.route('/library')
def library():
    return [
        {'label': _(30210), 'path': plugin.url_for('artists_library')},
        {'label': _(30211), 'path': plugin.url_for('albums_library')},
        {'label': _(30212), 'path': plugin.url_for('tracks_library')},
        {'label': _(30213), 'path': plugin.url_for('favorites_library')},
        {'label': _(30214), 'path': plugin.url_for('playlists_library')},
    ]


@plugin.route('/discover')
def discover():
    return [
        {'label': _(30260), 'path': plugin.url_for('popular')},
        {'label': _(30261), 'path': plugin.url_for('genres')},
        {'label': _(30262), 'path': plugin.url_for('albums_new')},
        {'label': _(30263), 'path': plugin.url_for('albums_picks')},
        {'label': _(30264), 'path': plugin.url_for('playlists_featured')},
        {'label': _(30266), 'path': plugin.url_for('stations_top')},
    ]


@plugin.route('/discover/popular')
def popular():
    return [
        {'label': _(30220), 'path': plugin.url_for('artists_top')},
        {'label': _(30221), 'path': plugin.url_for('albums_top')},
        {'label': _(30222), 'path': plugin.url_for('tracks_top')},
    ]


@plugin.route('/genres')
def genres():
    parent_genre_id = plugin.request.args.get('parent_genre_id', [None])[0]
    items = []
    if parent_genre_id is None:
        genres_list = rhapsody.genres.list()
    else:
        genres_list = rhapsody.genres.find(parent_genre_id).subgenres
    for genre in genres_list:
        items.append(helpers.get_genre_item(genre))
    return items


@plugin.route('/genres/<genre_id>/detail')
def genres_detail(genre_id):
    return [
        {'label': _(30220), 'path': plugin.url_for('genres_artists_top', genre_id=genre_id)},
        {'label': _(30221), 'path': plugin.url_for('genres_albums_top', genre_id=genre_id)},
        {'label': _(30222), 'path': plugin.url_for('genres_tracks_top', genre_id=genre_id)},
        {'label': _(30262), 'path': plugin.url_for('genres_albums_new', genre_id=genre_id)},
        {'label': _(30266), 'path': plugin.url_for('genres_stations', genre_id=genre_id)},
        {'label': _(30265), 'path': plugin.url_for('genres', parent_genre_id=genre_id)},
    ]


@plugin.route('/genres/<genre_id>/artists/top')
def genres_artists_top(genre_id):
    items = []
    for artist in rhapsody.genres.top_artists(genre_id):
        items.append(helpers.get_artist_item(artist))
    return items


@plugin.route('/genres/<genre_id>/albums/top')
def genres_albums_top(genre_id):
    items = []
    for album in rhapsody.genres.top_albums(genre_id):
        items.append(helpers.get_album_item(album))
    return items


@plugin.route('/genres/<genre_id>/tracks/top')
def genres_tracks_top(genre_id):
    items = helpers.get_track_items(rhapsody.genres.top_tracks(genre_id))
    return items


@plugin.route('/genres/<genre_id>/albums/new')
def genres_albums_new(genre_id):
    items = []
    for album in rhapsody.genres.new_albums(genre_id):
        items.append(helpers.get_album_item(album))
    return items


@plugin.route('/genres/<genre_id>/stations')
def genres_stations(genre_id):
    return helpers.get_station_items(rhapsody.genres.stations(genre_id))


@plugin.route('/search')
def search():
    query = plugin.keyboard(cache.get('last_search', ''), _(30240))
    if query is not None and len(query) > 0:
        cache['last_search'] = query
        items = []
        for result in rhapsody.search.fulltext(query):
            if result.type == 'artist':
                artist = result.data
                artist_item = helpers.get_artist_item(artist)
                artist_item['label'] = _(30241) + ': ' + artist_item['label']
                items.append(artist_item)
            if result.type == 'album':
                album = result.data
                album_item = helpers.get_album_item(album)
                album_item['label'] = _(30242) + ': ' + album_item['label']
                items.append(album_item)
            if result.type == 'track':
                track = result.data
                track_item = helpers.get_track_item(track)
                track_item['label'] = _(30243) + ': ' + track_item['label']
                items.append(track_item)
        if len(items) > 0:
            return items
        else:
            plugin.notify(_(30101).encode('utf-8'))


@plugin.route('/recent')
def recent():
    return [
        {'label': _(30230), 'path': plugin.url_for('artists_recent')},
        {'label': _(30231), 'path': plugin.url_for('tracks_recent')},
        {'label': _(30232), 'path': plugin.url_for('artists_most_played')},
        {'label': _(30233), 'path': plugin.url_for('albums_most_played')},
        {'label': _(30234), 'path': plugin.url_for('tracks_most_played')},
    ]


@plugin.route('/artists/top')
def artists_top():
    items = []
    for artist in rhapsody.artists.top():
        items.append(helpers.get_artist_item(artist))
    return items


@plugin.route('/artists/recent')
def artists_recent():
    items = []
    for artist in rhapsody.library.recent_artists():
        items.append(helpers.get_artist_item(artist))
    return items


@plugin.route('/artists/charts')
def artists_most_played():
    range_choice = plugin.request.args.get('range_choice', [None])[0]
    if range_choice is not None:
        items = []
        for most_played in rhapsody.library.most_played_artists(range_choice):
            try:
                artist = rhapsody.artists.detail(most_played.id)
                items.append(helpers.get_artist_item(artist))
            except exceptions.ResourceNotFoundError:
                pass
    else:
        items = [
            {
                'label': _(30235),
                'path': plugin.url_for('artists_most_played', range_choice=rhapsody.library.MOST_PLAYED_WEEK)
            },
            {
                'label': _(30236),
                'path': plugin.url_for('artists_most_played', range_choice=rhapsody.library.MOST_PLAYED_MONTH)
            },
            {
                'label': _(30237),
                'path': plugin.url_for('artists_most_played', range_choice=rhapsody.library.MOST_PLAYED_YEAR)
            },
            {
                'label': _(30238),
                'path': plugin.url_for('artists_most_played', range_choice=rhapsody.library.MOST_PLAYED_LIFE)
            },
        ]
    return items


@plugin.route('/artists/library')
def artists_library():
    items = []
    for artist in rhapsody.library.artists():
        items.append(helpers.get_artist_item(artist, in_library=True))
    return items


@plugin.route('/artists/library/<artist_id>/albums')
def artists_library_albums(artist_id):
    items = []

    try:
        album_type = int(plugin.request.args['album_type'][0])
    except (KeyError, ValueError):
        items.append({
            'label': u'[B]{0:s}[/B]'.format(_(30255)),
            'path': plugin.url_for('artists_detail', artist_id=artist_id)
        })

        album_type = rhapsody.albums.TYPE_MAIN_RELEASE
        items.append({
            'label': u'[B]{0:s}[/B]'.format(_(30245)),
            'path': plugin.url_for(
                'artists_library_albums',
                artist_id=artist_id,
                album_type=rhapsody.albums.TYPE_SINGLE_EP
            )
        })
        items.append({
            'label': u'[B]{0:s}[/B]'.format(_(30246)),
            'path': plugin.url_for(
                'artists_library_albums',
                artist_id=artist_id,
                album_type=rhapsody.albums.TYPE_COMPILATION
            )
        })

    for album in filter(lambda x: x.type.id == album_type, rhapsody.library.artist_albums(artist_id)):
        items.append(helpers.get_album_item(album, show_artist=False, in_library=True, library_artist_id=artist_id))

    return items


@plugin.route('/artists/library/<artist_id>/albums/<album_id>/remove')
def artists_library_albums_remove(artist_id, album_id):
    rhapsody.library.remove_album(album_id)
    return plugin.finish(artists_library_albums(artist_id), update_listing=True)


@plugin.route('/artists/library/<artist_id>/add')
def artists_library_add(artist_id):
    rhapsody.library.add_artist(artist_id)
    plugin.notify(_(30102))


@plugin.route('/artists/library/<artist_id>/remove')
def artists_library_remove(artist_id):
    rhapsody.library.remove_artist(artist_id)
    return plugin.finish(artists_library(), update_listing=True)


@plugin.route('/artists/<artist_id>/albums')
def artists_detail(artist_id):
    items = []

    try:
        album_type = int(plugin.request.args['album_type'][0])
    except (KeyError, ValueError):
        station = rhapsody.stations.detail(rhapsody.artists.get_station_id(artist_id))
        items.append(helpers.get_station_item(station, label=u'[B]{0:s}[/B]'.format(_(30244))))
        items.append({
            'label': u'[B]{0:s}[/B]'.format(_(30256)),
            'path': plugin.url_for('artists_similar', artist_id=artist_id)
        })

        album_type = rhapsody.albums.TYPE_MAIN_RELEASE
        items.append({
            'label': u'[B]{0:s}[/B]'.format(_(30245)),
            'path': plugin.url_for('artists_detail', artist_id=artist_id, album_type=rhapsody.albums.TYPE_SINGLE_EP)
        })
        items.append({
            'label': u'[B]{0:s}[/B]'.format(_(30246)),
            'path': plugin.url_for('artists_detail', artist_id=artist_id, album_type=rhapsody.albums.TYPE_COMPILATION)
        })

    for album in filter(lambda x: x.type.id == album_type, rhapsody.artists.albums(artist_id)):
        items.append(helpers.get_album_item(album, show_artist=False))

    return items


@plugin.route('/artists/<artist_id>/similar')
def artists_similar(artist_id):
    items = []
    similar = rhapsody.artists.similar(artist_id)
    for artist in similar.contemporaries + similar.followers + similar.influencers + similar.related:
        items.append(helpers.get_artist_item(artist))
    return items


@plugin.route('/favorites/<track_id>/add')
def favorites_add(track_id):
    rhapsody.library.add_favorite(track_id)
    plugin.notify(_(30102))


@plugin.route('/favorites/<track_id>/remove')
def favorites_remove(track_id):
    rhapsody.library.remove_favorite(track_id)
    return plugin.finish(favorites_library(), update_listing=True)


@plugin.route('/favorites')
def favorites_library():
    items = helpers.get_track_items(rhapsody.library.favorites(), in_favorites=True)
    return items


@plugin.route('/playlists/featured')
def playlists_featured():
    items = []
    for playlist in rhapsody.playlists.featured():
        items.append(helpers.get_playlist_item(playlist, in_library=False))
    return items


@plugin.route('/playlists/library')
def playlists_library():
    items = [{'label': _(30250), 'path': plugin.url_for('playlists_library_add')}]
    for playlist in rhapsody.library.playlists():
        items.append(helpers.get_playlist_item(playlist, in_library=True))
    return items


@plugin.route('/playlists/library/add')
def playlists_library_add():
    name = plugin.keyboard('')
    if name is not None and len(name) > 0:
        rhapsody.library.add_playlist(name)
    return plugin.finish(playlists_library(), update_listing=True)


@plugin.route('/playlists/library/<playlist_id>/rename')
def playlists_library_rename(playlist_id):
    name = plugin.keyboard('')
    if name is not None and len(name) > 0:
        rhapsody.library.rename_playlist(playlist_id, name)
    return plugin.finish(playlists_library(), update_listing=True)


@plugin.route('/playlists/library/<playlist_id>/remove')
def playlists_library_remove(playlist_id):
    rhapsody.library.remove_playlist(playlist_id)
    return plugin.finish(playlists_library(), update_listing=True)


@plugin.route('/playlists/library/<playlist_id>/detail')
def playlists_library_detail(playlist_id):
    playlist = rhapsody.library.playlist(playlist_id)
    items = helpers.get_track_items(playlist.tracks, in_playlists=True, playlist_id=playlist_id)
    return items


@plugin.route('/playlists/library/select/<track_id>')
def playlists_library_select(track_id):
    from xbmcswift2 import xbmcgui

    playlists = rhapsody.library.playlists()
    idx = xbmcgui.Dialog().select(_(30214), [x.name for x in playlists])
    if idx >= 0:
        playlist = playlists[idx]
        plugin.redirect(plugin.url_for('playlists_library_add_track', track_id=track_id, playlist_id=playlist.id))


@plugin.route('/playlists/library/<playlist_id>/add/<track_id>')
def playlists_library_add_track(playlist_id, track_id):
    rhapsody.library.add_track_to_playlist(track_id, playlist_id)
    plugin.notify(_(30102))


@plugin.route('/playlists/library/<playlist_id>/remove/<track_id>')
def playlists_library_remove_track(playlist_id, track_id):
    rhapsody.library.remove_track_from_playlist(track_id, playlist_id)
    return plugin.finish(playlists_library_detail(playlist_id), update_listing=True)


@plugin.route('/playlists/<playlist_id>')
def playlists_detail(playlist_id):
    items = helpers.get_track_items(rhapsody.playlists.detail(playlist_id).tracks)
    return items


@plugin.route('/stations/top')
def stations_top():
    items = [
        {'label': _(30267), 'path': plugin.url_for('stations_decade')}
    ] + list(helpers.get_station_items(rhapsody.stations.top()))
    return items


@plugin.route('/stations/decade')
def stations_decade():
    return helpers.get_station_items(rhapsody.stations.decade())


@plugin.route('/stations/<station_id>/detail')
def stations_detail(station_id):
    station = rhapsody.stations.detail(station_id)
    items = [{
        'label': _(30268).format(station.name),
        'is_playable': True,
        'path': plugin.url_for('stations_play', station_id=station_id)
    }]
    return items


@plugin.route('/stations/<station_id>/play')
def stations_play(station_id):
    import xbmc

    current_track_id = plugin.request.args.get('current_track_id', [None])[0]
    if current_track_id is None:
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        current_track_id = rhapsody.stations.tracks(station_id).tracks[0].id
        current_track = rhapsody.tracks.detail(current_track_id)
        current_item = helpers.get_track_item(current_track)
        plugin.add_to_playlist([current_item], playlist='music')

    return play(track_id=current_track_id, station_id=station_id)


@plugin.route('/albums/top')
def albums_top():
    items = []
    for album in rhapsody.albums.top():
        items.append(helpers.get_album_item(album))
    return items


@plugin.route('/albums/new')
def albums_new():
    items = []
    for album in rhapsody.albums.new():
        items.append(helpers.get_album_item(album))
    return items


@plugin.route('/albums/picks')
def albums_picks():
    items = []
    for album in rhapsody.albums.picks():
        items.append(helpers.get_album_item(album))
    return items


@plugin.route('/albums/charts')
def albums_most_played():
    range_choice = plugin.request.args.get('range_choice', [None])[0]
    if range_choice is not None:
        items = []
        for most_played in rhapsody.library.most_played_albums(range_choice):
            try:
                album = rhapsody.albums.detail(most_played.id)
                items.append(helpers.get_album_item(album))
            except exceptions.ResourceNotFoundError:
                pass
    else:
        items = [
            {
                'label': _(30235),
                'path': plugin.url_for('albums_most_played', range_choice=rhapsody.library.MOST_PLAYED_WEEK)
            },
            {
                'label': _(30236),
                'path': plugin.url_for('albums_most_played', range_choice=rhapsody.library.MOST_PLAYED_MONTH)
            },
            {
                'label': _(30237),
                'path': plugin.url_for('albums_most_played', range_choice=rhapsody.library.MOST_PLAYED_YEAR)
            },
            {
                'label': _(30238),
                'path': plugin.url_for('albums_most_played', range_choice=rhapsody.library.MOST_PLAYED_LIFE)
            },
        ]
    return items


@plugin.route('/albums/library')
def albums_library():
    items = []
    for album in rhapsody.library.albums():
        items.append(helpers.get_album_item(album, in_library=True))
    return items


@plugin.route('/albums/library/<album_id>/tracks')
def albums_library_tracks(album_id):
    items = helpers.get_track_items(rhapsody.library.album_tracks(album_id), show_artist=False, in_library=True)
    return items


@plugin.route('/albums/library/<album_id>/tracks/<track_id>/remove')
def albums_library_tracks_remove(album_id, track_id):
    rhapsody.library.remove_track(track_id)
    return plugin.finish(albums_library_tracks(album_id), update_listing=True)


@plugin.route('/albums/library/<album_id>/add')
def albums_library_add(album_id):
    rhapsody.library.add_album(album_id)
    plugin.notify(_(30102))


@plugin.route('/albums/library/<album_id>/remove')
def albums_library_remove(album_id):
    rhapsody.library.remove_album(album_id)
    return plugin.finish(albums_library(), update_listing=True)


@plugin.route('/albums/<album_id>')
def albums_detail(album_id):
    album = rhapsody.albums.detail(album_id)
    items = helpers.get_track_items(album.tracks, show_artist=(album.type.id == 2))
    return items


@plugin.route('/tracks/top')
def tracks_top():
    items = helpers.get_track_items(rhapsody.tracks.top())
    return items


@plugin.route('/tracks/recent')
def tracks_recent():
    items = helpers.get_track_items(rhapsody.library.recent_tracks())
    return items


@plugin.route('/tracks/charts')
def tracks_most_played():
    range_choice = plugin.request.args.get('range_choice', [None])[0]
    if range_choice is not None:
        items = []
        for most_played in rhapsody.library.most_played_tracks(range_choice, limit=1000)[:50]:
            try:
                track = rhapsody.tracks.detail(most_played.id)
                items.append(helpers.get_track_item(track))
                if len(items) >= 20:
                    break
            except exceptions.ResourceNotFoundError:
                pass
    else:
        items = [
            {
                'label': _(30235),
                'path': plugin.url_for('tracks_most_played', range_choice=rhapsody.library.MOST_PLAYED_WEEK)
            },
            {
                'label': _(30236),
                'path': plugin.url_for('tracks_most_played', range_choice=rhapsody.library.MOST_PLAYED_MONTH)
            },
            {
                'label': _(30237),
                'path': plugin.url_for('tracks_most_played', range_choice=rhapsody.library.MOST_PLAYED_YEAR)
            },
            {
                'label': _(30238),
                'path': plugin.url_for('tracks_most_played', range_choice=rhapsody.library.MOST_PLAYED_LIFE)
            },
        ]
    return items


@plugin.route('/tracks/library')
def tracks_library():
    items = helpers.get_track_items(rhapsody.library.tracks(), in_library=True)
    return items


@plugin.route('/tracks/library/<track_id>/add')
def tracks_library_add(track_id):
    rhapsody.library.add_track(track_id)
    plugin.notify(_(30102))


@plugin.route('/tracks/library/<track_id>/remove')
def tracks_library_remove(track_id):
    rhapsody.library.remove_track(track_id)
    return plugin.finish(tracks_library(), update_listing=True)


@plugin.route('/play/<track_id>')
def play(track_id, station_id=None):
    import re
    import play
    import xbmc

    track = rhapsody.tracks.detail(track_id)
    stream = rhapsody.streams.detail(track_id)

    item = helpers.get_track_item(track)
    if stream.url.startswith('rtmp://'):
        parts = [
            '/'.join(stream.url.split('/')[:5]),
            'app=' + '/'.join(stream.url.split('/')[3:5]),
            'playpath=' + 'mp3:' + '/'.join(stream.url.split('/')[5:])
        ]
        item['path'] = ' '.join(parts)
    else:
        item['path'] = stream.url

    notify = play.Notify(rhapsody, track, stream)
    player = play.Player(plugin=plugin, notify=notify)
    plugin.set_resolved_url(item)

    # add upcoming station tracks to playlist
    if station_id is not None:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        current_pos = playlist.getposition()
        playlist_target_size = current_pos + 5
        while playlist.size() <= playlist_target_size:
            next_tracks = rhapsody.stations.tracks(station_id).tracks[:5]
            if len(next_tracks) == 0:
                break
            for next_track in next_tracks:
                plugin.log.info('Preload: Adding next station track {0:d} of {1:d}'.format(
                    playlist.size(), current_pos + 5
                ))
                next_item = helpers.get_track_item(next_track)
                next_item['path'] = plugin.url_for(
                    'stations_play',
                    station_id=station_id,
                    current_track_id=next_track.id
                )
                plugin.add_to_playlist([next_item], playlist='music')

    # query the next playlist item so it'll be added to the cache for seamless playback
    prefetch_enabled = plugin.get_setting('api_prefetch', converter=bool)
    if prefetch_enabled and rhapsody.ENABLE_CACHE:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        next_pos = playlist.getposition() + 1
        if next_pos >= playlist.size():
            next_pos = 0
        next_url = playlist[next_pos].getfilename()

        next_track_id = None
        url_patterns = [
            re.escape(
                plugin.url_for('play', track_id='-track_id-')
            ).replace(
                re.escape('-track_id-'), '(?P<track_id>[^\/]+)'
            ),
            re.escape(
                plugin.url_for('stations_play', station_id='-station_id-', current_track_id='-track_id-')
            ).replace(
                re.escape('-station_id-'), '(?P<station_id>[^\/]+)'
            ).replace(
                re.escape('-track_id-'), '(?P<track_id>.+)'
            )
        ]
        for url_pattern in url_patterns:
            match = re.match(url_pattern, next_url)
            if match is not None:
                next_track_id = match.group('track_id')

        if next_track_id is not None:
            plugin.log.info('Preload: Caching next playlist position {0:d} ({1:s})'.format(next_pos, next_track_id))
            rhapsody.tracks.detail(next_track_id)
            rhapsody.streams.detail(next_track_id)

    # wait for the current item to finish before exiting
    while not xbmc.abortRequested and not player.has_stopped:
        xbmc.sleep(10)

    plugin.log.info('Player: Exited')
    return plugin.finish()


if __name__ == '__main__':
    sys.stdout = StringIO()
    sys.path.append(os.path.join(plugin.addon.getAddonInfo('path'), 'resources', 'lib'))

    _ = plugin.get_string
    cache = plugin.get_storage('data', TTL=0)

    import requests

    requests.packages.urllib3.disable_warnings()

    from helpers import Helpers

    helpers = Helpers(plugin)

    try:
        from rhapsody import exceptions

        rhapsody = helpers.get_api()
        # TODO: try to get RTMP working again
        # rhapsody.ENABLE_RTMP = plugin.get_setting('api_transport', converter=str) == 'RTMP'
        rhapsody.ENABLE_DEBUG = plugin.get_setting('api_debug', converter=bool)
        rhapsody.ENABLE_CACHE = not plugin.get_setting('api_cache_disable', converter=bool)
        if not rhapsody.ENABLE_DEBUG and not rhapsody.ENABLE_CACHE:
            rhapsody.ENABLE_CACHE = True
            plugin.set_setting('api_cache_disable', '0')

        plugin.run()
    except exceptions.AuthenticationError:
        plugin.notify(_(30100).encode('utf-8'))
        plugin.open_settings()
    except exceptions.RequestError:
        plugin.notify(_(30103).encode('utf-8'))
        plugin.log.error(sys.stdout.getvalue())
    except exceptions.ResourceNotFoundError:
        plugin.notify(_(30104).encode('utf-8'))
        plugin.log.error(sys.stdout.getvalue())
    except exceptions.ResponseError:
        plugin.notify(_(30105).encode('utf-8'))
        plugin.log.error(sys.stdout.getvalue())
    except exceptions.StreamingRightsError:
        plugin.notify(_(30106).encode('utf-8'))
        plugin.log.error(sys.stdout.getvalue())
    except Exception as e:
        plugin.log.error(sys.stdout.getvalue())
        traceback.print_exc()
        plugin.notify(e)
    finally:
        helpers.cleanup()

        stdout = sys.stdout.getvalue()
        if len(stdout):
            plugin.log.info(stdout)
