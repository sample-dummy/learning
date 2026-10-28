from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from enum import Enum


class Course(SQLModel, table = True):
    id : int | None = Field(default = None, primary_key = True)
    course_name: str
    code : str
    duration_years: int
    description : str |None
    active: bool = Field(default=True)

    students : list["Student"] = Relationship(back_populates="course_prop")


class Student(SQLModel, table=True):
    id:int | None = Field(default=None, primary_key=True)
    name:str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    course: str = Field(index=True)

    #this is not a db column. this is just a property
    course_prop : Course | None = Relationship(back_populates="students")
    course_id :int = Field(default= None, foreign_key="course.id")
    users_id : int | None = Field(default=None, foreign_key="user.id", unique=True)
    #or you could replace the whole thing with a Relationship and back_populates routes. your wish

class StudentPublic(SQLModel):  #this is the response model
     id:int
     name: str 
     age: int | None  
     course:str

class StudentCreate(SQLModel):
    name:str
    age:int
    course:str
    email:str

#creating a new class as the update endpoints don't need the email data
class StudentUpdate(SQLModel):
    name:str
    age:int
    course:str

class StudentUpdateOptional(SQLModel):
    name:str | None
    age:int | None
    course:str | None


class UserRole(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'


class User(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str 
    role: UserRole = Field(default=UserRole.STUDENT)
    disabled: bool = Field(default=False)

class UserCreate(SQLModel):
    email:str
#this field sent by the client needs to be hashed. 
#Thus named just password
    password:str         

class UserPublic(SQLModel):
    id:int
    email: str

class Token(BaseModel):
    access_token: str
    token_type : str

class TokenData(BaseModel):
    email: str




class CourseCreate(SQLModel):
    course_name: str
    code: str
    duration_years: int
    description: str | None