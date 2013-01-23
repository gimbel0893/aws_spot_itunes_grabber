import re
import random

class Util(object):

    REPLACE_ENTITY = re.compile('&.+?;')
    REPLACE_NONALPHA = re.compile('[^a-zA-Z0-9]')
    REPLACE_MULTIDASH = re.compile('-+')
    MATCH_ONLYDASH = re.compile('^-+$')

    @classmethod
    def make_seo_name(cls, name, in_case=None):
        name = cls.REPLACE_ENTITY.sub('-', name)
        name = cls.REPLACE_NONALPHA.sub('-', name)
        name = cls.REPLACE_MULTIDASH.sub('-', name)
        if cls.MATCH_ONLYDASH.search(name):
            if in_case:
                name = in_case
            else:
                name = random.randint(100000000, 999999999)
        return str(name).lower()
