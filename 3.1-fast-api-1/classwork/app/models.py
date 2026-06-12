# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    important = Column(Boolean, server_default="false", default=False)
    done = Column(Boolean, server_default="false", default=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    finish_time = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        """Вспомогательный метод для преобразования ORM-объекта в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "important": self.important,
            "done": self.done,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "finish_time": self.finish_time.isoformat() if self.finish_time else None,
        }
