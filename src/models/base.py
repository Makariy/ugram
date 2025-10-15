from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Base):
            return False 
        if type(self) is not type(value):
            return False 

        return all(
            getattr(self, col.key) == getattr(value, col.key)
            for col in self.__table__.columns
        )

    def __hash__(self) -> int:
        return sum(
            (hash(getattr(self, col.key)) for col in self.__table__.columns)
        )

