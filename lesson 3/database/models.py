from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime


Base = declarative_base()


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class Post(Base, IdMixin, UrlMixin):
    __tablename__ = "posts"
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("writers.id"))
    author = relationship("Writer")
    tags = relationship("Tag", secondary=tag_post)
    img = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    comments = relationship("Comment")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    author_id = Column(Integer, ForeignKey("writers.id"))
    author = relationship("Writer")
    post_id = Column(Integer, ForeignKey("posts.id"))

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.text = kwargs["text"]
        self.author = kwargs["author"]


class Writer(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = "writers"
    posts = relationship("Post")


class Tag(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = "tags"
    posts = relationship("Post", secondary=tag_post)
