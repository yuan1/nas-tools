# coding: utf-8
from sqlalchemy import Column, Float, Index, Integer, Text, text, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
BaseMedia = declarative_base()


class CONFIGFILTERGROUP(Base):
    __tablename__ = 'CONFIG_FILTER_GROUP'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    GROUP_NAME = Column(Text)
    IS_DEFAULT = Column(Text)
    NOTE = Column(Text)


class CONFIGFILTERRULES(Base):
    __tablename__ = 'CONFIG_FILTER_RULES'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    GROUP_ID = Column(Text, index=True)
    ROLE_NAME = Column(Text)
    PRIORITY = Column(Text)
    INCLUDE = Column(Text)
    EXCLUDE = Column(Text)
    SIZE_LIMIT = Column(Text)
    NOTE = Column(Text)


class CONFIGRSSPARSER(Base):
    __tablename__ = 'CONFIG_RSS_PARSER'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    NAME = Column(Text, index=True)
    TYPE = Column(Text)
    FORMAT = Column(Text)
    PARAMS = Column(Text)
    NOTE = Column(Text)
    SYSDEF = Column(Text)



class CONFIGSYNCPATHS(Base):
    __tablename__ = 'CONFIG_SYNC_PATHS'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    SOURCE = Column(Text)
    DEST = Column(Text)
    UNKNOWN = Column(Text)
    MODE = Column(Text)
    RENAME = Column(Integer)
    ENABLED = Column(Integer)
    NOTE = Column(Text)


class CONFIGUSERS(Base):
    __tablename__ = 'CONFIG_USERS'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    NAME = Column(Text, index=True)
    PASSWORD = Column(Text)
    PRIS = Column(Text)


class CUSTOMWORDS(Base):
    __tablename__ = 'CUSTOM_WORDS'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    REPLACED = Column(Text)
    REPLACE = Column(Text)
    FRONT = Column(Text)
    BACK = Column(Text)
    OFFSET = Column(Text)
    TYPE = Column(Integer)
    GROUP_ID = Column(Integer)
    SEASON = Column(Integer)
    ENABLED = Column(Integer)
    REGEX = Column(Integer)
    HELP = Column(Text)
    NOTE = Column(Text)


class CUSTOMWORDGROUPS(Base):
    __tablename__ = 'CUSTOM_WORD_GROUPS'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    TITLE = Column(Text)
    YEAR = Column(Text)
    TYPE = Column(Integer)
    TMDBID = Column(Integer)
    SEASON_COUNT = Column(Integer)
    NOTE = Column(Text)



class MESSAGECLIENT(Base):
    __tablename__ = 'MESSAGE_CLIENT'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    NAME = Column(Text)
    TYPE = Column(Text)
    CONFIG = Column(Text)
    SWITCHS = Column(Text)
    INTERACTIVE = Column(Integer)
    ENABLED = Column(Integer)
    NOTE = Column(Text)



class SYNCHISTORY(Base):
    __tablename__ = 'SYNC_HISTORY'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    PATH = Column(Text, index=True)
    SRC = Column(Text)
    DEST = Column(Text)


class SYSTEMDICT(Base):
    __tablename__ = 'SYSTEM_DICT'
    __table_args__ = (
        Index('INDX_SYSTEM_DICT', 'TYPE', 'KEY'),
    )

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    TYPE = Column(Text)
    KEY = Column(Text)
    VALUE = Column(Text)
    NOTE = Column(Text)


class TRANSFERBLACKLIST(Base):
    __tablename__ = 'TRANSFER_BLACKLIST'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    PATH = Column(Text, index=True)


class TRANSFERHISTORY(Base):
    __tablename__ = 'TRANSFER_HISTORY'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    MODE = Column(Text)
    TYPE = Column(Text)
    CATEGORY = Column(Text)
    TMDBID = Column(Integer)
    TITLE = Column(Text, index=True)
    YEAR = Column(Text)
    SEASON_EPISODE = Column(Text)
    SOURCE = Column(Text)
    SOURCE_PATH = Column(Text, index=True)
    SOURCE_FILENAME = Column(Text, index=True)
    DEST = Column(Text)
    DEST_PATH = Column(Text)
    DEST_FILENAME = Column(Text)
    DATE = Column(Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TRANSFERUNKNOWN(Base):
    __tablename__ = 'TRANSFER_UNKNOWN'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    PATH = Column(Text, index=True)
    DEST = Column(Text)
    MODE = Column(Text)
    STATE = Column(Text, index=True)



class MEDIASYNCITEMS(BaseMedia):
    __tablename__ = 'MEDIASYNC_ITEMS'
    __table_args__ = (
        Index('INDX_MEDIASYNC_ITEMS_SL', 'SERVER', 'LIBRARY'),
    )

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    SERVER = Column(Text)
    LIBRARY = Column(Text)
    ITEM_ID = Column(Text, index=True)
    ITEM_TYPE = Column(Text)
    TITLE = Column(Text, index=True)
    ORGIN_TITLE = Column(Text, index=True)
    YEAR = Column(Text)
    TMDBID = Column(Text, index=True)
    IMDBID = Column(Text)
    PATH = Column(Text)
    NOTE = Column(Text)
    JSON = Column(Text)


class MEDIASYNCSTATISTIC(BaseMedia):
    __tablename__ = 'MEDIASYNC_STATISTICS'

    ID = Column(Integer, Sequence('ID'), primary_key=True)
    SERVER = Column(Text, index=True)
    TOTAL_COUNT = Column(Text)
    MOVIE_COUNT = Column(Text)
    TV_COUNT = Column(Text)
    UPDATE_TIME = Column(Text)
