"""项目与用户业务逻辑。"""
from sqlalchemy.orm import Session

from app.models.project import Project, User
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_user(db: Session, email: str, hashed_password: str, nickname: str | None = None) -> User:
    user = User(email=email, hashed_password=hashed_password, nickname=nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_project(db: Session, obj: ProjectCreate, owner_id: int) -> Project:
    project = Project(name=obj.name, description=obj.description, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def list_projects(db: Session, owner_id: int) -> list[Project]:
    return db.query(Project).filter(Project.owner_id == owner_id).all()


def update_project(db: Session, project: Project, obj: ProjectUpdate) -> Project:
    if obj.name is not None:
        project.name = obj.name
    if obj.description is not None:
        project.description = obj.description
    db.commit()
    db.refresh(project)
    return project
