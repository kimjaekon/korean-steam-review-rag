"""SQLAlchemy ORM 매핑"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # DeclarativeBase : 이 클래스는 DB 테이블과 매핑되는 ORM 클래스다 선언


class Base(DeclarativeBase):
    """모든 ORM 모델의 베이스"""


class ReviewORM(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    recommendation_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    appid: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    author_steamid: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    voted_up: Mapped[bool] = mapped_column(nullable=False)
    playtime_at_review_min: Mapped[int] = mapped_column(Integer, nullable=False)
    votes_helpful: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
