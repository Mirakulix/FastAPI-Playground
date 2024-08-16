from . import models

def test_create_course_match(db):
    course_match = models.CourseMatch(
        university_1="WU Wien",
        university_2="Harvard",
        match_result="90%"
    )
    db.add(course_match)
    db.commit()
    db.refresh(course_match)
    assert course_match.id is not None

def test_read_course_match(db):
    course_match = db.query(models.CourseMatch).filter_by(university_1="WU Wien").first()
    assert course_match is not None
    assert course_match.university_2 == "Harvard"

def test_update_course_match(db):
    course_match = db.query(models.CourseMatch).filter_by(university_1="WU Wien").first()
    course_match.match_result = "95%"
    db.commit()
    db.refresh(course_match)
    assert course_match.match_result == "95%"

def test_delete_course_match(db):
    course_match = db.query(models.CourseMatch).filter_by(university_1="WU Wien").first()
    db.delete(course_match)
    db.commit()
    course_match = db.query(models.CourseMatch).filter_by(university_1="WU Wien").first()
    assert course_match is None