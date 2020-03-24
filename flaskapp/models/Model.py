from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from flaskapp import db

#
# class UserFile(db.Model):
#
#     __tablename__ = 'files'
#
#     # id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     id = db.Column(db.String, primary_key=True, default=generate_uuid_str)
#     file_name = db.Column(db.String, nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     # user_id = db.Column(db.Integer,
#     #                     db.ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"),
#     #                     nullable=False
#     #                 )
#     # user = db.relationship('User', backref='files', lazy=True)
#     # , user_id = {self.user_id}
#     def __repr__(self):
#         return f'File<file_name={self.file_name}, created_at={self.created_at}>'


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def __repr__(self):
        return f'User<email={self.email}>'