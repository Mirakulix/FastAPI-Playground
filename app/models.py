from sqlalchemy import Column, Integer, String, Text
from .database import Base

class CourseMatch(Base):
    __tablename__ = "course_matches"

    id = Column(Integer, primary_key=True, index=True)
    university_1 = Column(String, index=True)
    university_2 = Column(String, index=True)
    match_result = Column(Text)