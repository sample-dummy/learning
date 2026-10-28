from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated
from app.database import SessionDep
from sqlmodel import select, and_
from app.models import Student, StudentPublic, StudentCreate, User, StudentUpdate, Course, StudentUpdateOptional

from app.routes.authorize import get_current_active_user, check_if_admin

router = APIRouter()



#StudentPublic is my response model
@router.post('/students',status_code=201)
def post_student(student: StudentCreate, session:SessionDep, admin: Annotated[User, Depends(check_if_admin)]):
    
    account_buffer = select(User).where(student.email == User.email)
    account = session.exec(account_buffer).first()

    course_buffer = select(Course).where(student.course == Course.code)
    course = session.exec(course_buffer).first()

    if account is None:
         raise HTTPException(status_code= 404, detail="Register the user before creating the student")

    if course is None:
         raise HTTPException(status_code= 404, detail="Not a valid course")
    
#parse each of the field in student table with data from either client's payload (studentCreate) or the user record
    new_student = Student (
         name = student.name,
         age= student.age,
         course_id = course.id ,
         users_id= account.id
    )

    session.add(new_student)
    session.commit()
    session.refresh(new_student)
    return new_student

@router.get('/students', response_model = list[StudentPublic])
def get_students(session: SessionDep, query_course_id : int | None = None,  query_name: Annotated[str | None, Query(max_length=50)] = None,
                 offset: Annotated[int, Query(ge= 0)] = 0, limit : Annotated[int, Query(le = 200)] = 100):

    statement = select(Student)                 
    #the below is filtering being performed
    if query_name is not None:
        statement = select(Student).where(Student.name.ilike(f"%{query_name}%"))

    if query_course_id is not None:
        if session.get(Course, query_course_id) is None:
            raise HTTPException(status_code=404, detail = "The student doesn't have a course or the course doesn't exist")
        statement = select(Student).where(Student.course_id == query_course_id)

    if query_name and query_course_id is not None:
        if session.get(Course, query_course_id) is None:
            raise HTTPException(status_code=404, detail = "The student doesn't have a course or the course doesn't exist")

        statement = select(Student).where(and_(
             Student.name.ilike(f"%{query_name}%"), Student.course_id == query_course_id
        ))

    
    results = session.exec(statement.offset(offset).limit(limit)).all()
    return results



@router.get('/students/{id}', response_model=StudentPublic)
def get_student_by_id(id: int, session: SessionDep):
    student=session.get(Student, id)                                            #use this for single record
    if not student:
            raise HTTPException(status_code=404, detail="Student not found")
    return student


    
@router.put('/students/{id}')
def update_student_by_id(id:int,student:StudentUpdate, session:SessionDep, admin: Annotated[User, Depends(check_if_admin)]):
    student_from_db=session.get(Student, id)
    if not student_from_db:
         raise HTTPException(status_code=404, detail="Student not found")

    student_to_be_updated = student.model_dump()

    student_from_db.sqlmodel_update(student_to_be_updated)
    session.add(student_from_db)                       #basically the student_from_db is replaced with the new data, so use the same variable(And it's not appropriately named)
    session.commit()
    session.refresh(student_from_db)
    return student_from_db



@router.delete('/students/{id}')
def delete_by_id(id:int, session: SessionDep, admin: Annotated[User, Depends(check_if_admin)]):
    student=session.get(Student, id)
    if not student:
          raise HTTPException(status_code=404, detail="Student not found")
    session.delete(student)
    session.commit()
    return "Ok"


@router.patch('studemts/{id}', response_model=StudentPublic)
def patch_by_id(id: int, session : SessionDep, student: StudentUpdateOptional, admin: Annotated[User, Depends(check_if_admin)]):
    student_to_be_updated = session.get(Student, id)
    if student_to_be_updated is None:
         raise HTTPException(status_code=404, detail= "Student not found")

    student_data = student.model_dump(exclude_unset=True)
    student_to_be_updated.sqlmodel_update(student_data)
    session.add(student_to_be_updated)
    session.commit()
    session.refresh(student_to_be_updated)
    return student_to_be_updated

@router.get("/users/me/")
def read_own_items(  #👇👇👇any route has this below shit is basically a protected endpoint👇👇👇
    current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep):

    statement = select(Student).where(Student.users_id == current_user.id)
    student = session.exec(statement).first()

    return student