import asyncio
import logging
import re
import os
import tempfile
import ujson
import aiohttp
from telethon import TelegramClient
from telethon.tl import types
from telethon.helpers import add_surrogate, del_surrogate
from lib.config import config
from lib.errors import VKException

FWD_NONE, FWD_ATTACH, FWD_APPEND = range(3)

_VK_BASE = 'https://api.vk.com/method/'
_ZERO_CHARS = re.compile('^[\u200b\u200c\u200d]+$')

def _type_in_list(lst, tps):
    for el in lst:
        if isinstance(el, tps):
            return el
    return None

class Logger:
    logger: logging.Logger = None

    def __init__(self):
        self.logger = logging.getLogger(
            '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        )

class Uploadable(Logger):
    default_params = {}
    session: aiohttp.ClientSession = None
    group_id: int = None
    owner_id: int = None
    media_id: int = None
    endpoint = None

    def __init__(self, session, params, group_id):
        super().__init__()
        self.session = session
        self.default_params = params
        self.group_id = group_id

    def __str__(self):
        if not self.media_id:
            return ''

        return self.__class__.__name__.lower() + \
            str(self.owner_id or -self.group_id) + '_' + str(self.media_id)

    def _build_postdata(self):
        postdata = self.default_params.copy()
        postdata['owner_id'] = str(-self.group_id)
        return postdata

    def _get_id(self, response):
        return response.get('response', {}).get('id')

    async def upload(self):
        self.logger.debug('Uploading %r', self)

        postdata = self._build_postdata()
        self.logger.debug('POST %s %s', self.endpoint, postdata)
        async with self.session.post(self.endpoint, data=postdata) as resp:
            resp = await resp.json(loads=ujson.loads)
            self.logger.log(logging.DEBUG - 5, 'POST %s response: %s', self.endpoint, resp)

            if resp.get('error'):
                raise VKException(resp)

            self.media_id = self._get_id(resp)
        return self.media_id

class Doc(Uploadable):
    original_filename: str = None
    client: TelegramClient = None
    entity = None
    mimetype: str = None
    endpoint = _VK_BASE + 'docs.getWallUploadServer'
    endpoint1 = _VK_BASE + 'docs.save'
    _field_name = 'file'

    def __init__(self, session, params, group_id, client, entity, mimetype, original_filename=None):
        super().__init__(session, params, group_id)
        self.client = client
        self.entity = entity
        self.mimetype = mimetype
        self.original_filename = original_filename

    def _build_postdata(self):
        postdata = self.default_params.copy()
        postdata['group_id'] = str(self.group_id)
        return postdata

    def _build_postdata1(self, extra):
        postdata = self.default_params.copy()
        postdata.update(extra)
        return postdata

    def _get_id(self, response):
        # self.logger.debug('el: %s', response.get('response'))
        return response.get('response', {}).get('doc', {}).get('id')

    def _download_media(self):
        return self.client.download_media(
            self.entity,
            os.path.join(
                config.get('paths', 'temp', fallback=tempfile.gettempdir()),
                str(self.entity.id)
            )
        )

    async def upload(self):
        if not self.session:
            raise Exception('Connection not established')

        self.logger.debug('Uploading %r', self)

        try:
            filename = await self._download_media()
        except ConnectionError as e:
            self.logger.warning('Got connection error on download_media: "%s", retrying...', e)
            try:
                filename = await self._download_media()
            except ConnectionError:
                self.logger.exception('Failed to download_media')
                return None

        postdata = self._build_postdata()
        self.logger.debug('POST %s %s', self.endpoint, postdata)
        async with self.session.post(self.endpoint, data=postdata) as resp:
            resp = await resp.json(loads=ujson.loads)
            self.logger.log(logging.DEBUG - 5, 'POST %s response: %s', self.endpoint, resp)

            if resp.get('error'):
                raise VKException(resp)

            upload_url = resp.get('response', {}).get('upload_url')

        with open(filename, 'rb') as f:
            formdata = aiohttp.FormData()
            formdata.add_field(
                self._field_name, f,
                filename=self.original_filename or os.path.basename(filename),
                content_type=self.mimetype)
            self.logger.debug('POST %s %s', upload_url, formdata)
            async with self.session.post(upload_url, data=formdata) as resp:
                try:
                    resp = await resp.json(content_type=None, loads=ujson.loads)
                    self.logger.log(logging.DEBUG - 5, 'POST %s response: %s', upload_url, resp)
                except aiohttp.client_exceptions.ContentTypeError:
                    self.logger.error('Invalid response: %s', await resp.text())
                    return None

                if resp.get('error'):
                    raise VKException(resp)

                save_ticket = self._build_postdata1(resp)

        try:
            os.unlink(filename)
        except OSError:
            pass

        self.logger.debug('POST %s %s', self.endpoint1, save_ticket)
        async with self.session.post(self.endpoint1, data=save_ticket) as resp:
            resp = await resp.json(loads=ujson.loads)
            self.logger.log(logging.DEBUG - 5, 'POST %s response: %s', self.endpoint1, resp)

            if resp.get('error'):
                raise VKException(resp)

            self.media_id = self._get_id(resp)

        return self.media_id

class Photo(Doc):
    endpoint = _VK_BASE + 'photos.getWallUploadServer'
    endpoint1 = _VK_BASE + 'photos.saveWallPhoto'
    _field_name = 'photo'

    def _get_id(self, response):
        self.logger.log(logging.DEBUG - 5, 'Photo upload response: %s', response)
        el = next(iter(response.get('response', [])))
        self.owner_id = el.get('owner_id')
        return el.get('id') if el else None

    def _build_postdata1(self, extra):
        postdata = self._build_postdata()
        postdata.update(extra)
        return postdata

    def __init__(self, session, params, group_id, client, entity, _=None, original_filename=None):
        super().__init__(session, params, group_id, client, entity, 'image/jpeg', original_filename)

class Video(Doc):
    endpoint = _VK_BASE + 'video.save'
    _field_name = 'video_file'

    async def upload(self):
        filename = await self._download_media()

        self.logger.debug('Uploading %r', self)

        postdata = self._build_postdata()
        self.logger.debug('POST %s %s', self.endpoint, postdata)
        async with self.session.post(self.endpoint, data=postdata) as resp:
            resp = await resp.json(loads=ujson.loads)
            self.logger.log(logging.DEBUG - 5, 'POST %s response: %s', self.endpoint, resp)

            if resp.get('error'):
                raise VKException(resp)

            upload_url = resp.get('response', {}).get('upload_url')

        with open(filename, 'rb') as f:
            formdata = aiohttp.FormData()
            formdata.add_field(
                self._field_name, f,
                filename=self.original_filename or os.path.basename(filename),
                content_type=self.mimetype)

            self.logger.debug('POST %s %s', upload_url, formdata)
            async with self.session.post(upload_url, data=formdata) as resp:
                try:
                    resp = await resp.json(content_type=None, loads=ujson.loads)
                    self.logger.log(logging.DEBUG - 5, 'POST %s response: %s', upload_url, resp)
                except aiohttp.client_exceptions.ContentTypeError:
                    self.logger.error('Invalid response: %s', await resp.text())
                    return None

                if resp.get('error'):
                    raise VKException(resp)

                self.media_id = resp.get('video_id')

        try:
            os.unlink(filename)
        except OSError:
            pass

        return self.media_id

class Audio(Doc):
    pass

class Page(Uploadable):
    title: str = None
    text: str = None
    attachments: list = None
    endpoint = _VK_BASE + 'pages.save'

    def __init__(self, session, params, group_id, title, text, attachments=None):
        super().__init__(session, params, group_id)
        self.title = title
        self.text = text
        self.attachments = attachments

    def _build_postdata(self):
        attachments = [
            '[[' + str(a) + ']]' for a in self.attachments \
                if a is not self and not isinstance(a, (Url, Poll, Geo))
        ]
        postdata = self.default_params.copy()
        postdata.update({
            'group_id': str(self.group_id),
            'title': self.title,
            'text': self.text + (('\n' + '\n'.join(attachments)) if attachments else '')
        })
        return postdata

    def _get_id(self, response):
        return response.get('response')

class Poll(Uploadable):
    question: str = None
    answers: list = None
    endpoint = _VK_BASE + 'polls.create'

    def __init__(self, session, params, group_id, question, answers):
        super().__init__(session, params, group_id)
        self.question = question
        self.answers = answers

    def _build_postdata(self):
        data = super()._build_postdata()
        data.update({
            'question': self.question,
            'add_answers': ujson.dumps(self.answers)
        })
        return data

class Url:
    url = None
    title = None

    def __init__(self, url, title=None):
        if url.startswith('http'):
            self.url = url
        else:
            self.url = 'http://' + url
        self.title = title

    def __str__(self):
        return self.url

class Fwd(Url, Uploadable):
    client = None
    post_id = None

    def __init__(self, session, params, group_id, post_id, client):
        Uploadable.__init__(self, session, params, group_id)
        self.client = client
        self.post_id = post_id
        self.url = ''

    async def upload(self):
        try:
            # HACK self.group_id is Peer or Forward
            if isinstance(self.group_id, types.PeerChannel):
                entity = await self.client.get_entity(self.group_id)
            else:
                entity = await self.group_id.get_chat()
            if entity.username:
                self.url = 'https://t.me/{}/{}'.format(entity.username, self.post_id)
        except ValueError:
            self.logger.info('Couldn\'t get entity for %d', self.group_id)

        return self.url

class Geo:
    lat = None
    long = None

    def __init__(self, lat, long):
        self.lat = lat
        self.long = long

    def __str__(self):
        return ''

class WallPost(Uploadable):
    fwd: int = None
    source: types.Message = None
    attachments: list = None
    endpoint = _VK_BASE + 'wall.post'

    def __init__(self, access_token, vk_group_id: int, message: types.Message,
                 *, fwd_from=FWD_ATTACH):
        super().__init__(
            aiohttp.ClientSession(raise_for_status=True, json_serialize=ujson.dumps),
            {'v': '5.92', 'access_token': access_token},
            vk_group_id
        )

        self.fwd = fwd_from
        self.source = message
        self.attachments = []

        # extract message attachment
        extractors = (self._process_unsupported, self._process_geo, self._process_photo,
                      self._process_webpage, self._process_poll, self._process_document,
                      self._process_rich_text)
        for extractor in extractors:
            if extractor():
                break

        # extract urls to attachments
        for e, inner_text in self.source.get_entities_text():
            if isinstance(e, types.MessageEntityTextUrl):
                self.attachments.append(Url(e.url, inner_text))
            elif isinstance(e, types.MessageEntityUrl):
                self.attachments.append(Url(inner_text))

        # NOTE last attachment is more significant, so telegram link will be ignored
        # if any other present
        fwd = self.source.forward
        if fwd and fwd.channel_id:
            self._add_fwd_from(fwd, fwd.channel_post)
        # or add link to message itself
        elif self.source.to_id:
            self._add_fwd_from(self.source.to_id, self.source.id)

    def __del__(self):
        asyncio.ensure_future(self.session.close())


    def _add_fwd_from(self, channel, channel_post):
        if self.fwd == FWD_NONE:
            return

        self.attachments.insert(
            0, Fwd(
                self.session, self.default_params, channel, channel_post, self.source.client
            )
        )

    def _process_rich_text(self):
        min_length = config.getint('xpost', 'rich_text_min_length', fallback=256)
        is_rich = bool(self.source.entities) and \
            bool(_type_in_list(self.source.entities, (
                types.MessageEntityBold, types.MessageEntityItalic,
                types.MessageEntityPre, types.MessageEntityCode
                ))) and \
            len(self.source.raw_text) >= min_length

        if not is_rich:
            return False

        min_title_length = 16
        max_title_length = min_length // 4
        pos = min(p for p in (
            self.source.raw_text.find('\n', min_title_length, max_title_length),
            self.source.raw_text.find('. ', min_title_length, max_title_length),
            self.source.raw_text.find(', ', min_title_length, max_title_length),
            max_title_length - 3
        ) if p != -1)

        title = self.source.raw_text[0:pos] + '...'

        fmt_list = {
            types.MessageEntityBold: '<b>{0}</b>',
            types.MessageEntityItalic: '<i>{0}</i>',
            types.MessageEntityPre: '<pre>{0}</pre>',
            types.MessageEntityCode: '<code>{0}</code>',
            types.MessageEntityMention: '[https://t.me/{1}|{0}]',
            types.MessageEntityMentionName: '[https://t.me/{1}|{0}]',
            types.MessageEntityUrl: '[{0}]',
            types.MessageEntityTextUrl: '[{1}|{0}]'
        }

        # add_surrogate/del_surrogate are used by Telethon internally in
        # get_entities_text -> get_inner_text to get correct offsets in unicode
        raw_text = add_surrogate(self.source.raw_text)
        text = []
        prev = 0
        for e, et in self.source.get_entities_text():
            text.append(del_surrogate(raw_text[prev:e.offset]))
            ev = None
            # NOTE no MessageEntityMentionName usage examples/documentation available
            # so assume it is same as MessageEntityMention
            if isinstance(e, (types.MessageEntityMention, types.MessageEntityMentionName)):
                ev = et[1:]
            elif isinstance(e, types.MessageEntityTextUrl):
                ev = e.url
            fmt = fmt_list.get(type(e), '{0}')
            text.append(del_surrogate(fmt.format(et, ev)))
            prev = e.offset + e.length
        text.append(del_surrogate(raw_text[prev:]))
        del raw_text

        self.attachments.append(Page(
            self.session, self.default_params, self.group_id,
            title,
            ''.join(text),
            self.attachments
        ))
        return True

    def _process_text(self, params):
        if not self.source.text:
            return False

        append_from = self.fwd == FWD_APPEND
        fwd = None
        for att in reversed(self.attachments):
            if append_from and isinstance(att, Fwd):
                fwd = _type_in_list(reversed(self.attachments), Fwd)

                # Fwd.url is already resolved here
                self.source.entities.append(
                    types.MessageEntityUrl(len(self.source.raw_text) + 2, len(fwd.url) - 2)
                )
                self.source.text += '\n\n' + fwd.url
                append_from = False
                continue

            if not isinstance(att, Url):
                continue

            if self.source.text == str(att.url):
                if att.title:
                    params['message'] = att.title
                return True

        if fwd:
            self.attachments.remove(fwd)

        text_urls = []
        for e, inner_text in self.source.get_entities_text():
            # NOTE no MessageEntityMentionName usage examples/documentation available
            # so assume it is same as MessageEntityMention
            if isinstance(e, (types.MessageEntityMention, types.MessageEntityMentionName)):
                text_urls.append(types.MessageEntityTextUrl(
                    e.offset, e.length, 'https://t.me/' + inner_text[1:]
                ))
                continue
            if isinstance(e, types.MessageEntityTextUrl):
                text_urls.append(e)


        geo = _type_in_list(self.attachments, Geo)
        if geo:
            self.attachments.remove(geo)
            params['lat'] = geo.lat
            params['long'] = geo.long

        # if this is a rich text
        rich_page = _type_in_list(self.attachments, Page)
        if rich_page:
            params['message'] = rich_page.title
            return False

        if text_urls:
            # add_surrogate/del_surrogate are used by Telethon internally in
            # get_entities_text -> get_inner_text to get correct offsets in unicode
            raw_text = add_surrogate(self.source.raw_text)

            msg = []
            prev = 0
            for tu in text_urls:
                title = del_surrogate(raw_text[prev:(tu.offset + tu.length)])
                # link titles to telegraph photos look like \u200b\u200b
                if _ZERO_CHARS.match(title):
                    continue
                msg.append(title)
                msg.append(' (' + tu.url + ') ')
                prev = tu.offset + tu.length
            msg.append(del_surrogate(raw_text[prev:]))
            del raw_text

            params['message'] = ''.join(msg)
        else:
            params['message'] = self.source.raw_text

        return True

    def _process_unsupported(self):
        if isinstance(self.source.media, (
                types.MessageMediaEmpty, types.MessageMediaGame, types.MessageMediaInvoice,
                types.MessageMediaUnsupported, types.MessageMediaContact
        )):
            self.logger.warning('Unsupported media %s', self.source.media)
            return True

        return False

    def _process_geo(self):
        if isinstance(self.source.media, (types.MessageMediaGeo, types.MessageMediaGeoLive,
                                          types.MessageMediaVenue)):
            if isinstance(self.source.media, types.MessageMediaVenue):
                self.logger.info(
                    'MessageMediaVenue is not completely supported %s', self.source.media
                )

            if isinstance(self.source.media.geo, types.GeoPoint):
                self.attachments.append(Geo(self.source.media.geo.lat, self.source.media.geo.long))

            return True

        return False

    def _process_webpage(self):
        if isinstance(self.source.media, types.MessageMediaWebPage):
            if isinstance(self.source.media.webpage, (
                    types.WebPageEmpty, types.WebPageNotModified, types.WebPagePending
            )):
                return True

            # photo attached as a webpage
            if self.source.media.webpage.photo:
                entity = _type_in_list(self.source.entities, types.MessageEntityTextUrl)

                # photo link present in message
                if entity and entity.url == self.source.media.webpage.url:
                    self.source.entities.remove(entity)

                self.attachments.append(Photo(
                    self.session, self.default_params, self.group_id,
                    self.source.client, self.source.media.webpage.photo
                ))
            else:
                self.attachments.append(
                    Url(self.source.media.webpage.url, self.source.media.webpage.title)
                )

            return True

        return False

    def _process_poll(self):
        if isinstance(self.source.media, types.MessageMediaPoll):
            self.attachments.append(Poll(
                self.session, self.default_params, self.group_id,
                self.source.media.poll.question,
                [a.text for a in self.source.media.poll.answers]
            ))
            return True

        return False

    def _process_photo(self):
        if isinstance(self.source.media, types.MessageMediaPhoto):
            if not isinstance(self.source.media.photo, types.PhotoEmpty):
                self.attachments.append(Photo(
                    self.session, self.default_params, self.group_id,
                    self.source.client, self.source.media.photo
                ))
            return True

        return False

    def _process_document(self):
        if isinstance(self.source.media, types.MessageMediaDocument):
            doc = self.source.media.document
            if not isinstance(doc, types.DocumentEmpty):
                cls = Doc
                fn_attr = _type_in_list(doc.attributes, types.DocumentAttributeFilename)
                if _type_in_list(doc.attributes, types.DocumentAttributeSticker) or\
                    doc.mime_type.startswith('image/'):
                    # in some cases images might be attached as document
                    cls = Photo
                if _type_in_list(doc.attributes, types.DocumentAttributeAudio):
                    cls = Audio
                if _type_in_list(doc.attributes, types.DocumentAttributeVideo):
                    cls = Video

                self.attachments.append(cls(
                    self.session, self.default_params, self.group_id,
                    self.source.client, doc, doc.mime_type, fn_attr.file_name if fn_attr else None
                ))
            return True

        return False

    def _build_postdata(self):
        postdata = super()._build_postdata()

        self._process_text(postdata)

        # remove links from attachments if media present
        if _type_in_list(self.attachments, (Doc, Video, Audio, Photo)):
            url = _type_in_list(self.attachments, Url)
            # self.logger.debug('Media present, removing url attachments')
            while url:
                self.logger.info('Media present, removing url attachment: %s', url)
                self.attachments.remove(url)
                url = _type_in_list(self.attachments, Url)

        if self.attachments:
            postdata['attachments'] = [str(a) for a in self.attachments if str(a)]

        return postdata

    def _get_id(self, response):
        return response.get('response', {}).get('post_id')

    async def upload(self):
        self.logger.debug('Crossposting post %d/%d -> %d',
                          self.source.to_id.channel_id, self.source.id, self.group_id)

        failed = []
        for a in self.attachments:
            # self.logger.debug('Processing attachment %r', a)
            if isinstance(a, Uploadable):
                self.logger.debug('Uploading attachment %r', a)
                if not await a.upload():
                    self.logger.warning('Upload failed for %r', a)
                    failed.append(a)

        # remove failed:
        for a in failed:
            self.attachments.remove(a)

        # remove all urls but last
        have_one = False
        remove = []
        for att in reversed(self.attachments):
            if not isinstance(att, Url):
                continue
            if have_one:
                remove.append(att)
            else:
                have_one = True

        for a in remove:
            self.attachments.remove(a)

        del remove, failed

        await super().upload()
        await self.session.close()

        self.logger.info('Crossposting done %d/%d -> https://vk.com/wall-%d_%d',
                         self.source.to_id.channel_id, self.source.id, self.group_id, self.media_id)
        return self.media_id
