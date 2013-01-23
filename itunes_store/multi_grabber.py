import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

from yaml import load as yload
from multiprocessing import Pool

from grabber import GamesGrabber


CONFIG = 'multi_grabber.yml'

def run(process):
    log.info('Process "{}" started'.format(process.get('name', '')))

    terms = []
    if 'term' in process:
        terms.append(process['term'])
    if 'sequence' in process:
        terms += process['sequence']
    g = GamesGrabber(terms).grab_all().end_log()

    log.info('Process "{}" stats:'.format(process.get('name', '')))
    log.info(g.stat)
    log.info('Process "{}" finished'.format(process.get('name', '')))


if __name__ == '__main__':
    log.info('Multiprocessing Start')

    with open(CONFIG, 'r') as f:
        config = yload(f)
    processes = config['processes']
    pool = Pool(processes=len(processes))
    pool.map(run, processes)

    log.info('Multiprocessing End')
