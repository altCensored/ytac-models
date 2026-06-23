from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Index,
    Integer,
    Interval,
    ForeignKey,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


content_table = Table(
    'content', Base.metadata,
    Column('source_id', Integer, ForeignKey('source.id', ondelete='CASCADE'), nullable=False),
    Column('video_id', Integer, ForeignKey('video.id', ondelete='CASCADE'), nullable=False),
    PrimaryKeyConstraint('source_id', 'video_id'),
    Index('ix_content_video_source', 'video_id', 'source_id'),
)


class Video(Base):
    __tablename__ = 'video'

    id = Column(Integer, primary_key=True)
    extractor_key = Column(String, nullable=False)
    extractor_data = Column(String, nullable=False)

    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_ytdlp = Column(String, nullable=True)
    thumbnail_ac = Column(String, nullable=True)

    tags = Column(JSONB, nullable=True)
    category = Column(String, nullable=True)
    view_count = Column(Integer, nullable=True)
    published = Column(Date, nullable=True)
    duration = Column(Integer, nullable=True)
    view_count_ac = Column(Integer, nullable=True)
    filesize_approx = Column(BigInteger, nullable=True)

    deleted_date = Column(Date, nullable=True)
    deleted_reason = Column(Text, nullable=True)

    live_status = Column(String, nullable=True)

    maint_yt_last = Column(Date, nullable=True)
    maint_ia_last = Column(Date, nullable=True)
    maint_ac_last = Column(Date, nullable=True)
    archive_date = Column(Date, nullable=True)

    videofile = Column(Text, nullable=True)

    added_date = Column(Date, nullable=True)

    allow = Column(Boolean, nullable=False, default=True)
    limited = Column(Boolean, nullable=False, default=False)
    deleted = Column(Boolean, nullable=False, default=False)
    ac_exists = Column(Boolean, nullable=False, default=False)
    ac_exists_mkv = Column(Boolean, nullable=False, default=False)

    ia_exists = Column(Boolean, nullable=False, default=False)
    ia_novideo = Column(Boolean, nullable=False, default=False)

    ia_restricted = Column(Boolean, nullable=False, default=False)
    ia_loggedin = Column(Boolean, nullable=False, default=False)
    ia_uploadother = Column(Boolean, nullable=False, default=False)
    ia_dark = Column(Boolean, nullable=False, default=False)
    found = Column(Boolean, nullable=False, default=False)

    sources = relationship('Source', secondary=content_table, back_populates='videos')

    __table_args__ = (
        UniqueConstraint('extractor_key', 'extractor_data', name='uq_video_extractor'),
        Index('ix_video_extractor', 'extractor_key', 'extractor_data'),
        Index('ix_video_published', 'published'),
        Index('ix_video_tags_gin', 'tags', postgresql_using='gin'),
    )


class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True)
    extractor_key = Column(String, nullable=False)
    extractor_data = Column(String, nullable=False)
    extractor_match = Column(String, nullable=False)
    url = Column(String, nullable=False)

    sync_next = Column(DateTime(timezone=True), nullable=True)
    delta = Column(Interval, nullable=False)

    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_ytdlp = Column(String, nullable=True)
    thumbnail_ytapi = Column(String, nullable=True)
    tags = Column(JSONB, nullable=True)
    added_date = Column(Date, nullable=True)
    uploader_id = Column(String, nullable=True)
    channel_follower_count = Column(Integer, nullable=True)

    published_at = Column(Date, nullable=True)
    view_count = Column(BigInteger, nullable=True)
    video_count = Column(Integer, nullable=True)

    allow = Column(Boolean, nullable=False, default=True)
    deleted = Column(Boolean, nullable=False, default=False)
    archive_full = Column(Boolean, nullable=False, default=False)
    archive_part = Column(Boolean, nullable=False, default=False)
    archive_latest = Column(Boolean, nullable=False, default=False)
    archive_full_was = Column(Boolean, nullable=False, default=False)
    archive_part_was = Column(Boolean, nullable=False, default=False)

    deleted_date = Column(Date, nullable=True)
    deleted_reason = Column(Text, nullable=True)
    check_live_last = Column(Date, nullable=True)
    maint_yt_last = Column(Date, nullable=True)
    maint_ia_last = Column(Date, nullable=True)
    maint_ac_last = Column(Date, nullable=True)

    videos = relationship('Video', secondary=content_table, back_populates='sources')

    __table_args__ = (
        UniqueConstraint('extractor_key', 'extractor_data', name='uq_source_extractor'),
        Index('ix_source_extractor', 'extractor_key', 'extractor_data'),
        Index('ix_source_extractor_match', 'extractor_key', 'extractor_match'),
        Index('ix_source_sync_next_allow', 'sync_next', 'allow'),
    )

    @property
    def videos_missing(self):
        return len([v for v in self.videos if not v.ia_exists and not v.ac_exists])

    @property
    def videos_saved(self):
        return len([v for v in self.videos if v.ia_exists or v.ac_exists])

    @property
    def videos_total(self):
        return len(self.videos)

    @property
    def videos_deleted(self):
        return len([v for v in self.videos if v.deleted])

    @property
    def videos_live(self):
        return len([v for v in self.videos if v.live_status in ('is_live', 'is_upcoming', 'post_live')])

    @property
    def video_newest(self):
        dates = [v.published for v in self.videos if v.published]
        return max(dates) if dates else None


class Config(Base):
    __tablename__ = 'config'
    id = Column(String, primary_key=True)
    value = Column(String)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False, unique=True)
    icon = Column(String, nullable=False)


class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=False)
    flag = Column(String, nullable=False)
    flag_icon = Column(String, nullable=False)
    tag_filter = Column(Text, nullable=True)


class Translation(Base):
    __tablename__ = 'translation'
    varname = Column(String, primary_key=True)
    en = Column(String, nullable=False)
    de = Column(String, nullable=True)
    es = Column(String, nullable=True)
    fr = Column(String, nullable=True)
    pt = Column(String, nullable=True)
    nl = Column(String, nullable=True)
    it = Column(String, nullable=True)
    se = Column(String, nullable=True)


class Counter(Base):
    __tablename__ = 'counter'
    hash = Column(BigInteger, primary_key=True)


class AltcenUser(Base):
    __tablename__ = 'altcen_user'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    email_subscribed = Column(Boolean, nullable=False, default=True)
    email_action = Column(String, nullable=True)
    password = Column(String, nullable=True)
    watched = Column(ARRAY(String), nullable=True)
    watchlater = Column(ARRAY(String), nullable=True)
    created_date = Column(DateTime(timezone=True), nullable=True)
    email_verified_date = Column(DateTime(timezone=True), nullable=True)
    email_lastsent_date = Column(DateTime(timezone=True), nullable=True)
    updated = Column(DateTime(timezone=True), nullable=True)
    navtabs = Column(ARRAY(String), nullable=True)
    navtabs_index = Column(ARRAY(String), nullable=True)
    username = Column(String, nullable=True)
    description = Column(String, nullable=True)
    public = Column(Boolean, nullable=False, default=False)
    view_counter = Column(Integer, nullable=True)
    contributor = Column(Boolean, nullable=False, default=False)
    settings = Column(JSONB, nullable=True)
    featured_playlist = Column(JSONB, nullable=True)
    playlists = relationship('Playlist', back_populates='user')


class Playlist(Base):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True)
    hashid = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    videos = Column(ARRAY(String), nullable=True)
    video_count = Column(Integer, nullable=True)
    created = Column(DateTime(timezone=True), nullable=True)
    updated = Column(DateTime(timezone=True), nullable=True)
    public = Column(Boolean, nullable=False, default=True)
    view_counter = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('altcen_user.id'), nullable=False)
    featured_video = Column(JSONB, nullable=True)
    featured_video_id = Column(String, nullable=True)
    user = relationship('AltcenUser', back_populates='playlists')


class EmailList(Base):
    __tablename__ = 'email_list'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=True)
    source = Column(String, nullable=False)
    subscribed = Column(Boolean, nullable=False, default=True)
    action = Column(String, nullable=True)
    created = Column(DateTime(timezone=True), nullable=True)
    last_sent = Column(DateTime(timezone=True), nullable=True)
    updated = Column(DateTime(timezone=True), nullable=True)


class Findtext(Base):
    __tablename__ = 'find_text'
    term = Column(String, primary_key=True, nullable=False)


class Crypto(Base):
    __tablename__ = 'crypto'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    address = Column(String, nullable=False)
