"""SQLAlchemy 엔진 + 세션 팩토리"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from steam_rag.config.settings import settings

# pool_pre_ping=True: DB 연결이 살아있는지 먼저 확인
# future=True: SQLAlchemy 2.x 스타일로 동작하게 하는 옵션
engine = create_engine(settings.db.url, pool_pre_ping=True, future=True)

# class_=Session: sessionmaker가 어떤 Session 클래스를 만들지 지정
# expire_on_commit=False: commit() 후에도 객체를 만료시키지 않고 메모리의 값을 그대로 사용, 기본 True 는 commit 후에는 객체의 값 만료됨
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
