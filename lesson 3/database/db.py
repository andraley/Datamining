from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def _get_or_create(self, session, model, uniq_field, uniq_value, **data):
        db_data = session.query(model).filter(uniq_field == uniq_value).first()
        if not db_data:
            db_data = model(**data)
            session.add(db_data)
            try:
                session.commit()
            except Exception as exc:
                print(exc)
                session.rollback()
        return db_data

    def create_comment(self, session, data):
        result = []
        for comment in data:
            comment_author = self._get_or_create(
                session,
                models.Writer,
                models.Writer.url,
                comment["url"],
                name=comment["name"],
                url=comment["url"],
            )
            db_comment = self._get_or_create(
                session,
                models.Comment,
                models.Comment.id,
                comment["id"],
                **comment,
                author=comment_author,
            )
            result.append(db_comment)

        return result

    def create_post(self, data):
        session = self.maker()
        author = self._get_or_create(
            session,
            models.Writer,
            models.Writer.url,
            data["author"]["url"],
            **data["author"],
        )
        tags = map(
            lambda tag_data: self._get_or_create(
                session, models.Tag, models.Tag.url, tag_data["url"], **tag_data
            ),
            data["tags"],
        )
        post = self._get_or_create(
            session,
            models.Post,
            models.Post.id,
            data["post"]["url"],
            **data["post"],
            author=author,
        )
        if data["comments"]:
            comments = self.create_comment(session, data["comments"])
            post.comments.extend(comments)

        post.tags.extend(tags)
        session.add(post)

        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()

