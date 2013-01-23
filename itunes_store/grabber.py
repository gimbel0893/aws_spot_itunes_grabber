import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

import sys
import string
import datetime
import transaction
from sqlalchemy.exc import IntegrityError

import itunes
from basesqlalchemy import DBSession, Base
from game import GrabberGame as Game, PostMeta
from history import Version, Price
from exception import GrabberException
from log import GrabberLog as Log


class GameGrabber(object):

    MEDIA = 'software'
    LIMIT = 200
    ACCEPTED_GENRE = 'Games'

    def __init__(self):
        super(GameGrabber, self).__init__()
        self.search_term = None
        self.offset = None
        self.stat = None
        self.log = None
        self.db = DBSession()

    def init(self, search_term=None):
        self.search_term = search_term
        self.offset = 0
        self.stat = GrabberStat()
        self.start_log()
        return self

    def grab(self, search_term=''):
        self.init(search_term)
        last_page = False
        while not last_page:
            try:
                games = self._grab()
                self.add_games(games)
            except Exception as e:
                self.handle_exception(e)
            if len(games) < self.LIMIT:
                last_page = True
            else:
                self.offset += self.LIMIT
        return self

    def _grab(self):
        try:
            results = itunes.search(query=self.search_term, media=self.MEDIA,
                                    limit=self.LIMIT, offset=self.offset)
        except (itunes.ServiceException, Exception) as e:
            raise
        return results

    def add_games(self, games=[]):
        log.info('start add_games() term={}, offset={}.' \
                  .format(self.search_term, self.offset))
        log.info(self.stat)
        self.stat.increment(len(games))
        for game in games:
            self.stat.increment_iteration()
            log.info('on add_games() loop iteration={}, term={}, offset={}.' \
                .format(self.stat.iteration, self.search_term, self.offset))
            if game.get_genre() == self.ACCEPTED_GENRE:
                if game.get_id() not in self.stat.ids:
                    log.info('about to call add_game() for apple_id={}.' \
                              .format(game.get_id()))
                    self.add_game(game)
                    log.info('called add_game()')
                    self.stat.add_id(game.get_id())
                else:
                    log.info('didnt call add_game(), already have apple_id={} ' \
                             + 'in this run'.format(game.get_id()))
            else:
                log.info('didnt call add_game(), bad genre={}.' \
                          .format(game.get_genre()))
        transaction.commit()
        return self

    def add_game(self, game):
        log.info('in add_game(), about to get savepoint')
        savepoint = transaction.savepoint()
        log.info('got savepoint, about to check for game existance')
        # try to load the game first so that we can update
        # otherwise create a new game
        g = self.db.query(Game).filter_by(game_id=game.get_id()).first() \
                or Game(log=self.log)
        log.info('{} that game, about to init()' \
                  .format('FOUND' if g.game_id else 'DID NOT FIND'))
        is_existing_game = True if g.game_id else False;
        g.init(game)
        log.info('done with game init()')
        try:
            # make sure to add history before updating wp_post
            log.info('about to add_history()')
            if is_existing_game:
                self.add_history(g)
            log.info('done with add_history()')
            log.info('about to add basic game')
            self.db.add(g)
            log.info('added basic game')
            # need flush so that our savepoint will fail here if it needs to
            self.db.flush()
            log.info('flushed')
            g.save_wp_post()
            log.info('saved wp_post')
            if not is_existing_game:
                self.stat.increment_db()
        except Exception as e:
            log.info('exception, about to roll back savepoint')
            savepoint.rollback()
            log.info('rolled back savepoint')
            raise
        return self

    def add_history(self, game):
        version_meta = self.db.query(PostMeta).filter_by(post_id=game.game_id,
                        meta_key='games_version').first()
        version = version_meta.meta_value if version_meta else None
        if version is None or version < game.game.get_version():
            history = Version(version=game.game.get_version())
            history.log = self.log
            game._history.append(history)
        price_meta = self.db.query(PostMeta).filter_by(post_id=game.game_id,
                        meta_key='games_price').first()
        price = price_meta.meta_value if price_meta else None
        if price is None or price < game.game.get_price():
            history = Price(price=game.game.get_price())
            history.log = self.log
            game._history.append(history)
        return self

    def handle_exception(self, exception):
        e = GrabberException(type=type(exception), message=str(exception),
                             search_term=self.search_term, limit=self.LIMIT,
                             offset=self.offset, iteration=self.stat.iteration,
                             log=self.log)
        try:
            self.db.add(e)
            transaction.commit()
        except Exception as e:
            transaction.abort()
            raise
        self.stat.increment_exception()
        return self

    def start_log(self):
        self.log = Log()
        self.db.add(self.log)
        transaction.commit()
        return self

    def end_log(self):
        self.log.init(self.stat)
        self.db.add(self.log)
        transaction.commit()
        return self

class GrabberStat(object):

    def __init__(self):
        super(GrabberStat, self).__init__()
        self.total_results = 0
        self.total_queries = 0
        self.ids = set()
        self.total_db_adds = 0
        self.total_exceptions = 0
        self.iteration = 0

    def increment(self, num_results=0):
        self.total_results += num_results
        self.total_queries += 1
        self.iteration = 0
        return self

    def add_id(self, id):
        self.ids.add(id)
        return self

    def increment_db(self):
        self.total_db_adds += 1
        return self

    def increment_exception(self):
        self.total_exceptions += 1
        return self

    def increment_iteration(self):
        self.iteration += 1
        return self

    def __str__(self):
        return ('{} - queries: {}, results: {}, unique_ids: {}, db_adds: {}, ' \
                + 'exceptions: {}, iteration: {}.').format(
                datetime.datetime.now().strftime('%H%M%S'), self.total_queries,
                self.total_results, len(self.ids), self.total_db_adds,
                self.total_exceptions, self.iteration)

class GamesGrabber(GameGrabber):

    SEARCH_SEQ = string.lowercase

    def __init__(self, search_seq=None):
        super(GamesGrabber, self).__init__()
        self.search_seq = search_seq or GamesGrabber.SEARCH_SEQ
        self.stat = GrabberStat()

    def init(self, search_term=None):
        self.search_term = search_term
        self.offset = 0
        return self

    def grab_all(self):
        self.start_log()
        for search_term in self.search_seq:
            self.grab(search_term)
            log.info(self.stat)
        return self


if __name__ == '__main__':
    if len(sys.argv) == 2:
        g = GameGrabber().grab(sys.argv[1]).end_log()
    else:
        g = GamesGrabber().grab_all().end_log()
    log.info(g.stat)
