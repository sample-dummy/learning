from sqlmodel import Session, select

from app.database import engine
from app.models import User, UserRole
from app.routes.authorize import get_password_hash
from app.config import settings

def seed_admin():
    email = "admin123@gmail.com"

    with Session(engine) as session:
        existing_admin = session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_admin:
            print(f"User with {email} already exists")
            return

        admin = User(
            email=email,
            hashed_password=get_password_hash(settings.admin_password),
            role=UserRole.ADMIN,
        )
        session.add(admin)
        session.commit()
        print(f"User with {email} added with role {admin.role}")


if __name__ == "__main__":
    seed_admin()
