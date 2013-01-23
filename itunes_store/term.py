import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

import datetime
import hashlib

from basesqlalchemy import Base
from sqlalchemy import (
        desc,
        Table,
        Column,
        ForeignKey,
        Integer,
        BigInteger,
        Float,
        String,
        Text,
        DateTime,
        Date,
    )
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from util import Util


class TaxonomyRelationship(Base):

    TERM_ORDER = 0

    __tablename__ = 'pts_term_relationships'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    object_id = Column(BigInteger, ForeignKey('pts_posts.ID'),
                       primary_key=True, autoincrement=False)
    term_taxonomy_id = Column(BigInteger,
                              ForeignKey('pts_term_taxonomy.term_taxonomy_id'),
                              primary_key=True, autoincrement=False)
    term_order = Column(Integer)

    def __init__(self, object_id=None, term_taxonomy_id=None, term_order=None):
        self.object_id = object_id
        self.term_taxonomy_id = term_taxonomy_id
        self.term_order = term_order or self.TERM_ORDER

class Term(Base):

    TERM_GROUP = 0

    __tablename__ = 'pts_terms'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    term_id = Column(BigInteger, primary_key=True)
    name = Column(String(200))
    slug = Column(String(200))
    term_group = Column(BigInteger)

    def __init__(self, term_id=None, name=None, slug=None, term_group=None):
        self.term_id = term_id
        self.name = name
        self.slug = slug
        self.term_group = term_group or self.TERM_GROUP

    def set_slug(self, slug=None):
        if not slug:
            slug = Util.make_seo_name(self.name)
        self.slug = slug
        return self

class TermTaxonomy(Base):

    PARENT = 0
    COUNT = 0

    __tablename__ = 'pts_term_taxonomy'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    term_taxonomy_id = Column(BigInteger, primary_key=True)
    term_id = Column(BigInteger, ForeignKey('pts_terms.term_id'))
    taxonomy = Column(String(32))
    description = Column(Text)
    parent = Column(BigInteger)
    count = Column(BigInteger)
    _term = relationship('Term', backref='_taxonomies')
    _posts = relationship('Post', secondary=TaxonomyRelationship.__table__,
                          backref=backref('_taxonomies',
                          order_by=TaxonomyRelationship.term_order))

    def __init__(self, term_taxonomy_id=None, term_id=None, taxonomy=None,
                 description=None, parent=None, count=None, _term_order=None):
        self.term_taxonomy_id = term_taxonomy_id
        self.term_id = term_id
        self.taxonomy = taxonomy or ''
        self.description = description or ''
        self.parent = parent or self.PARENT
        self.count = count or self.COUNT
        self._term_order = _term_order
