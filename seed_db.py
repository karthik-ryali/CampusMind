from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Department, Section, User
from faker import Faker
import os

DB_DIR = "data"
DB_FILE = "issue_manager.db"
DB_PATH = f"sqlite:///{os.path.join(os.getcwd(), DB_DIR, DB_FILE)}"

engine = create_engine(DB_PATH, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

fake = Faker()

def create_schema():
    Base.metadata.create_all(bind=engine)
    print("Created DB Schema")

def seed():
    session = SessionLocal()
    try:
        depts = ["CSE", "AI-ML", "DS", "ECE", "EEE", "MECH", "CIVIL"]
        for d in depts:
            dept = Department(name=d)
            session.add(dept)
            session.flush()
            
            s1 = Section(name=f"{d}-A", department_id=dept.id)
            s2 = Section(name=f"{d}-B", department_id=dept.id)
            session.add_all([s1, s2])

        session.commit()

        vc = User(name="VC Office", email="vc@univ.edu", role="vc", password="12345")
        session.add(vc)
        session.commit()
        session.refresh(vc)

        all_depts = session.query(Department).all()
        
        for dept in all_depts:
            hod = User(
                name = f"HOD {dept.name}",
                email = f"hod_{dept.name.lower()}@univ.edu",
                password = "123456",
                role = "hod",
                department_id = dept.id,
                reports_to = vc.id
            )
            session.add(hod)
            session.commit()
            session.refresh(hod)

            sections = session.query(Section).filter(Section.department_id==dept.id).all()
            proctors = []

            for sec in sections:
                proctor = User(
                    name = f"Proctor {dept.name} {sec.name}",
                    email = f"proctor_{dept.name.lower()}_{sec.name.lower()}@univ.edu",
                    password = "1234567",
                    role = "proctor",
                    department_id = dept.id,
                    section_id = sec.id,
                    reports_to = hod.id
                )
                session.add(proctor)
                session.commit()
                session.refresh(proctor)
                proctors.append(proctor)
            
            for idx, sec in enumerate(sections):
                current_proctor_id = proctors[idx].id
                
                students_batch = []
                for i in range(50):
                    student = User(
                        name = f"{dept.name}_Student_{idx*50+i+1}",
                        email = f"{dept.name.lower()}_stu_{idx*50+i+1}@univ.edu",
                        password = f"{idx*50+i+1}", # Password matches ID number
                        role = "student",
                        department_id = dept.id,
                        section_id = sec.id,
                        reports_to = current_proctor_id
                    )
                    students_batch.append(student)
                
                session.add_all(students_batch)
                session.commit()
                
        print("✅ Seeding complete!")
    
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    create_schema()
    seed()