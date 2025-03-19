from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    # Relación entre tablas:
    posts = relationship("Post", back_populates = "user", cascade = "all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

    def serialize_is_active(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }

    def serialize_posts(self):
        return {
            "id": self.id,
            "email": self.email,
            "posts": [post.serialize_all() for post in self.posts]
        }

class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable = False)
    content: Mapped[str] = mapped_column(String(500), nullable = False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable = False)

    # Relación
    user = relationship("User", back_populates="posts")

    def serialize_all(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content
        }

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id
        }
