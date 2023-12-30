from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BLOB, Text
from sqlalchemy.orm import relationship
# import sqlalchemy


# print(dir(sqlalchemy))
# ['ARRAY', 'BIGINT', 'BINARY', 'BLANK_SCHEMA', 'BLOB', 'BOOLEAN', 'BigInteger', 'Boolean', 'CHAR', 'CLOB', 'CheckConstraint', 'Column', 'ColumnDefault', 'Computed', 'Constraint', 'DATE', 'DATETIME', 'DDL', 'DECIMAL', 'Date', 'DateTime', 'DefaultClause', 'Enum', 'FLOAT', 'FetchedValue', 'Float', 'ForeignKey', 'ForeignKeyConstraint', 'INT', 'INTEGER', 'Identity', 'Index', 'Integer', 'Interval', 'JSON', 'LABEL_STYLE_DEFAULT', 'LABEL_STYLE_DISAMBIGUATE_ONLY', 'LABEL_STYLE_NONE', 'LABEL_STYLE_TABLENAME_PLUS_COL', 'LargeBinary', 'MetaData', 'NCHAR', 'NUMERIC', 'NVARCHAR', 'Numeric', 'PickleType', 'PrimaryKeyConstraint', 'REAL', 'SMALLINT', 'Sequence', 'SmallInteger', 'String', 'TEXT', 'TIME', 'TIMESTAMP', 'Table', 'Text', 'ThreadLocalMetaData', 'Time', 'TypeDecorator', 'Unicode', 'UnicodeText', 'UniqueConstraint', 'VARBINARY', 'VARCHAR', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__go', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_util', 'alias', 'all_', 'and_', 'any_', 'asc', 'between', 'bindparam', 'case', 'cast', 'cimmutabledict', 'collate', 'column', 'cprocessors', 'create_engine', 'create_mock_engine', 'cresultproxy', 'delete', 'desc', 'dialects', 'distinct', 'engine', 'engine_from_config', 'event', 'events', 'exc', 'except_', 'except_all', 'exists', 'ext', 'extract', 'false', 'func', 'funcfilter', 'future', 'insert', 'inspect', 'inspection', 'intersect', 'intersect_all', 'join', 'lambda_stmt', 'lateral', 'literal', 'literal_column', 'log', 'modifier', 'not_', 'null', 'nulls_first', 'nulls_last', 'nullsfirst', 'nullslast', 'or_', 'orm', 'outerjoin', 'outparam', 'over', 'pool', 'processors', 'schema', 'select', 'sql', 'subquery', 'table', 'tablesample', 'text', 'true', 'tuple_', 'type_coerce', 'types', 'union', 'union_all', 'update', 'util', 'values', 'within_group']

from database import Base #For this to work, add __init__.py and delete the "." (meaning it's in the same folder)



#If the user is in this database at all, then they are in the weeklong
class hvzPlayer(Base):
    __tablename__ = "hvzPlayers" #The table within the dbfile

    #['Name', 'Team', 'Status', 'Tagged By', 'Tags']
    id = Column(Integer, primary_key=True, autoincrement=True)#index=True) #primary_key=True auto incrments appended items with a unique id
    name = Column(String) #Not unique, but we can sort by names
    profileImg = Column(String) # Upload a string pfp, encode utf8
    team = Column(String) #Human, zombie
    customTeam = Column(String) # Any team they want
    taggedBy = Column(String) 
    tags = Column(Integer)
    ifMod = Column(Boolean)
    daysAliveCount = Column(Integer)
    announcement = Column(String) #One singular announcement located at ACTUAL id = 1 (not readjusting)
    announcementId = Column(Integer)
    readjustingId = Column(Integer)
    hiddenOZ = Column(Boolean) #Hidden original zombie (Will be on Zombie team), will be shown as human ON THE TABLE, will be real visible zombie when EITHER time passes or tags (Tags will be HIDDEN on table for OZs)
    
class userPass(Base):
    __tablename__ = "userPass" #The table within the dbfile
    #['Name', 'Team', 'Status', 'Tagged By', 'Tags']
    username = Column(String, primary_key=True, unique=True, index=True, nullable=False) #primary_key=True auto incrments appended items with a unique id
    password = Column(String, nullable=False) #Not unique, but we can sort by names
    passwordReenter = Column(String)
    profilePic = Column(String) #I believe profile pics are blobs (binary text)
    isAdmin = Column(Boolean) #It's fine if this is null honestly. Will just check if it's None or False
    presidentOrVP = Column(Boolean) #Able to de-mod people
    secretKey = Column(String)#An 8 spaced thing
    signedUp = Column(Boolean) #False = no, True = Yes
    # We'll have to keep a boolean for all these badges. The second they're true, dont' set em false ever ;)
    ##########################
    daysAliveBadge = Column(Boolean) #days >= 3
    playerTagsBadge = Column(Boolean) #Tags >= 3
    hiddenOzBadge = Column(Boolean) #If ever gotten hidden oz
    ##########################

class missions(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True)
    dateAndTime = Column(String)
    description = Column(String)
    isCompleted = Column(String)
    readjustingId = Column(Integer) #This is needed to remark the count of how many players are on the table, and to assign an ID that just goes from 1:N smoothly


