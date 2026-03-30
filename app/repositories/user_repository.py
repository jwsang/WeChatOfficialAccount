from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_account import UserAccount


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> UserAccount | None:
        return self.db.get(UserAccount, user_id)

    def get_by_username(self, username: str) -> UserAccount | None:
        statement = select(UserAccount).where(UserAccount.username == username)
        return self.db.scalar(statement)

    def create(self, payload: dict) -> UserAccount:
        user = UserAccount(**payload)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: UserAccount) -> UserAccount:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
