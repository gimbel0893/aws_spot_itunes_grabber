import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

import datetime

from basesqlalchemy import Base, DBSession as db
from sqlalchemy import (
        and_,
        Column,
        ForeignKey,
        Integer,
        BigInteger,
        String,
        Text,
        DateTime,
    )
from sqlalchemy.orm import relationship, backref

from php import PHPArray
from log import GrabberLog
from util import Util
from term import Term, TermTaxonomy


class GrabberGame(Base):

    GUID_BASE = 'http://localhost/?post_type=games&#038;p='
    TAXONOMY = 'games_category'

    __tablename__ = 'grabber_games'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    game_id = Column(Integer, primary_key=True, autoincrement=False)
    log_id = Column(Integer, ForeignKey('grabber_logs.id'))
    created = Column(DateTime)
    modified = Column(DateTime)
    log = relationship('GrabberLog', backref='_games')

    def __init__(self, game_id=None, log_id=None, created=None, modified=None,
                 log=None):
        self.game_id = game_id
        self.log_id = log_id
        self.created = created
        self.modified = modified
        self.game = None
        self.log = log

    def init(self, game):
        if not self.game_id:
            self.created = datetime.datetime.utcnow()
        self.game_id = game.get_id()
        self.modified = datetime.datetime.utcnow()
        self.game = game
        return self

    def save_wp_post(self):
        log.info('in save_wp_post(), ' \
                 + 'about to query for existing wp game post')
        post = db.query(Post).join(Post.meta).filter(
                PostMeta.meta_key == 'games_appleid',
                PostMeta.meta_value == str(self.game.get_id())).first()
        # if the game exists clear out old meta info, we'll re-add with newest
        if post:
            log.info('FOUND existing wp game post')
            log.info('about to delete old postmeta')
            #db.delete(post.meta)
            db.query(PostMeta).filter_by(post_id=post.ID) \
                              .filter(PostMeta.meta_key!='games_association') \
                              .delete()
            log.info('deleted old postmeta')
            #db.flush()
        # or make a new game
        else:
            log.info('DID NOT FIND existing wp game post')
            post_name = Util.make_seo_name(self.game.get_title())
            post = Post(post_title=self.game.get_title(), post_name=post_name)

        log.info('about to start adding postmeta')
        post.meta.append(PostMeta(meta_key='games_appleid',
                         meta_value=self.game.get_id()))
        post.meta.append(PostMeta(meta_key='games_description',
                         meta_value=self.game.get_description()))
        post.meta.append(PostMeta(meta_key='games_developer',
                         meta_value=self.game.get_developer()))
        post.meta.append(PostMeta(meta_key='games_display_date',
                         meta_value=datetime.datetime.utcnow()))
        post.meta.append(PostMeta(meta_key='games_post_id',
                         meta_value=post.ID))
        post.meta.append(PostMeta(meta_key='games_price',
                         meta_value=self.game.get_price()))
        post.meta.append(PostMeta(meta_key='games_publisher',
                         meta_value=self.game.get_publisher()))
        post.meta.append(PostMeta(meta_key='games_releasedate',
                         meta_value=self.game.get_release_date()))
        post.meta.append(PostMeta(meta_key='games_version',
                         meta_value=self.game.get_version()))
        php_array = PHPArray(self.game.get_screenshots())
        post.meta.append(PostMeta(meta_key='games_screenshots',
                         meta_value=str(php_array)))
        post.meta.append(PostMeta(meta_key='games_icon',
                         meta_value=self.game.get_icon()))
        post.meta.append(PostMeta(meta_key='games_medium_icon',
                         meta_value=self.game.get_medium_icon()))
        post.meta.append(PostMeta(meta_key='games_large_icon',
                         meta_value=self.game.get_large_icon()))
        log.info('done building up postmeta, about to add to db session')

        db.add(post)
        log.info('added wp post to db session')
        db.flush()
        log.info('flushed wp post')
        post.guid = self.GUID_BASE + str(post.ID)

        log.info('about to add genres')
        self.set_genres(post)
        log.info('added genres')
        db.add(post)
        log.info('added wp post again with guid')

        return self

    def set_genres(self, post):
        if self.game.get_genres():
            for genre in self.game.get_genres():
                taxonomy = db.query(TermTaxonomy).join(TermTaxonomy._term) \
                            .filter(and_(TermTaxonomy.taxonomy==self.TAXONOMY,
                                         Term.name==genre)).first()
                # increment the count of posts using this term set
                if taxonomy:
                    taxonomy.count += 1
                    log.info('not new taxonomy')
                # if this term set doesn't exist, create a new one
                else:
                    taxonomy = TermTaxonomy(taxonomy=self.TAXONOMY)
                    taxonomy._term = Term(name=genre).set_slug()
                    log.info('new taxonomy')
                # associate the new/existing genre with this post
                post._taxonomies.append(taxonomy)
        return self

class Post(Base):

    POST_AUTHOR = 0
    POST_PARENT = 0
    POST_TYPE = 'games'
    POST_STATUS = 'publish'
    COMMENT_STATUS = 'open'
    PING_STATUS = 'open'

    __tablename__ = 'pts_posts'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    meta = relationship('PostMeta', backref='post')
    ID = Column(BigInteger, primary_key=True)
    post_author = Column(BigInteger)
    post_date = Column(DateTime)
    post_date_gmt = Column(DateTime)
    post_content = Column(Text)
    post_title = Column(Text)
    post_excerpt = Column(Text)
    post_status = Column(String(20))
    comment_status = Column(String(20))
    ping_status = Column(String(20))
    post_password = Column(String(20))
    post_name = Column(String(200))
    to_ping = Column(Text)
    pinged = Column(Text)
    post_modified = Column(DateTime)
    post_modified_gmt = Column(DateTime)
    post_content_filtered = Column(Text)
    post_parent = Column(Integer)
    guid = Column(String(255))
    menu_order = Column(Integer)
    post_type = Column(String(20))
    post_mime_type = Column(String(100))
    comment_count = Column(BigInteger)

    def __init__(self, ID=None, post_author=None, post_date=None,
                 post_date_gmt=None, post_content=None, post_title=None,
                 post_excerpt=None, post_status=None, comment_status=None,
                 ping_status=None, post_password=None, post_name=None,
                 to_ping=None, pinged=None, post_modified=None,
                 post_modified_gmt=None, post_content_filtered=None,
                 post_parent=None, guid=None, menu_order=None, post_type=None,
                 post_mime_type=None, comment_count=None):
        self.ID = ID
        self.post_author = post_author or self.POST_AUTHOR
        self.post_date = post_date or datetime.datetime.now()
        self.post_date_gmt = post_date_gmt or datetime.datetime.utcnow()
        self.post_content = post_content or ''
        self.post_title = post_title or ''
        self.post_excerpt = post_excerpt or ''
        self.post_status = post_status or self.POST_STATUS
        self.comment_status = comment_status or self.COMMENT_STATUS
        self.ping_status = ping_status or self.PING_STATUS
        self.post_password = post_password or ''
        self.post_name = post_name or ''
        self.to_ping = to_ping or ''
        self.pinged = pinged or ''
        self.post_modified = post_modified or datetime.datetime.now()
        self.post_modified_gmt = post_modified_gmt or datetime.datetime.utcnow()
        self.post_content_filtered = post_content_filtered or ''
        self.post_parent = post_parent or self.POST_PARENT
        self.guid = guid or ''
        self.menu_order = menu_order or 0
        self.post_type = post_type or self.POST_TYPE
        self.post_mime_type = post_mime_type or ''
        self.comment_count = comment_count or 0

class PostMeta(Base):

    __tablename__ = 'pts_postmeta'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    meta_id =  Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey('pts_posts.ID'))
    meta_key = Column(String(255))
    meta_value = Column(Text)

    def __init__(self, meta_id=None, post_id=None, meta_key=None,
                 meta_value=None):
        self.meta_id = meta_id
        self.post_id = post_id
        self.meta_key = meta_key
        self.meta_value = meta_value
