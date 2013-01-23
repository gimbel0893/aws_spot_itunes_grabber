import logging
log = logging.getLogger(__name__)


class PHPArray(object):

    def __init__(self, array=[]):
        super(PHPArray, self).__init__()
        self.array = array
        self.string = ''

    def __str__(self):
        self._print(self.array)
        return self.string

    def _print(self, array):
        if isinstance(array, list):
            return self._print_list(array)
        elif isinstance(array, dict):
            return self._print_dict(array)
        elif isinstance(array, int):
            self.string += 'i:{};'.format(array)
        elif isinstance(array, (str, unicode)):
            self.string += 's:{}:"{}";'.format(len(array), array.encode('utf8'))
        elif isinstance(array, bool):
            self.string += 'b:{};'.format(1 if array else 0)
        else:
            raise Exception('found unexpected type: {}.'.format(type(array)))
        return self
            
    def _print_list(self, array):
        length = len(array)
        self.string += 'a:{}:{{'.format(length)
        for i in range(len(array)):
            self.string += 'i:{};'.format(i)
            self._print(array[i])
        self.string += '}'
        return self

    def _print_dict(self, array):
        length = len(array)
        self.string += 'a:{}:{{'.format(length)
        for key, value in array.iteritems():
            self._print(key)
            self._print(value)
        self.string += '}'
        return self


if __name__ == '__main__':
    print "\n\n"
    array = ['abc', 'def', 'hij', 'xyz']
    php_array = PHPArray(array)
    print str(php_array)
    print "\n\n"
    array = {'one': 1, 'array': [1, 2, 3], 'dict': {'seven': 7, 'eight': 8},
             'two': 2, 'three': 'the number 3'}
    php_array = PHPArray(array)
    print str(php_array)
    print "\n\n"
