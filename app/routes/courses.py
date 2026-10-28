from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select


from app.database import SessionDep
from app.routes.authorize import get_current_active_user, check_if_admin
from app.models import Course, User, CourseCreate

router_course = APIRouter()

@router_course.get('/courses')
def get_all_courses(session:SessionDep, offset: Annotated[int, Query(ge= 0)] = 0, limit : Annotated[int, Query(le = 100)] = 100):   #le means lesser than or equal to. basically the value put in by the client nneeds to below the certain threshold
    statement = select(Course).limit(limit).offset(offset)
    courses = session.exec(statement).all()

    return courses


@router_course.get('/courses/{id}')
def get_course_by_id(id: int, session: SessionDep):
    course = session.get(Course, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course

@router_course.post('/courses')
def add_course(course: CourseCreate, session: SessionDep, if_admin: Annotated[User, Depends(check_if_admin)]):

    new_course = Course(
        course_name= course.course_name,
        code= course.code,
        duration_years= course.duration_years,
        description= course.description
    )

    session.add(new_course)
    session.commit()
    session.refresh(new_course)
    return new_course

@router_course.put('/courses/{id}')
def update_course_by_id(id: int, course: CourseCreate, session: SessionDep, if_admin : Annotated[User, Depends(check_if_admin)]):
    old_course = session.get(Course, id)
    if not old_course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_to_be_updated = course.model_dump()

    old_course.sqlmodel_update(course_to_be_updated)

    session.add(old_course)
    session.commit()
    session.refresh(old_course)

    return old_course

@router_course.delete('/courses/{id}')
def delete_course_by_id(id:int, session: SessionDep, if_admin: Annotated[User, Depends(check_if_admin)]):
    course = session.get(Course, id)
    if not course:
        raise HTTPException(status_code= 404, detail="Course not found")

    session.delete(course)
    session.commit()
    return "Ok"

