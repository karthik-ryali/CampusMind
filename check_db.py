import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Issue, Department, Section

DB_PATH = "sqlite:///data/issue_manager.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)
session = Session()

def print_table(title, query_obj, columns):
    print(f"\n{'='*20} {title} {'='*20}")
    df = pd.read_sql(session.query(query_obj).statement, session.bind)
    
    if df.empty:
        print("Table is empty.")
    else:
        try:
            print(df[columns].to_string(index=False))
        except KeyError:
            print(df.to_string(index=False))

try:
    print_table("DEPARTMENTS", Department, ["id", "name"])
    print_table("SECTIONS", Section, ["id", "name", "department_id"])

    print(f"\n{'='*20} STAFF & ADMIN USERS {'='*20}")
    staff_users = session.query(User).filter(User.role.in_(["vc", "hod", "proctor"])).all()
    
    if not staff_users:
        print("No staff users found.")
    else:
        data = []
        for u in staff_users:
            data.append({
                "ID": u.id,
                "Name": u.name,
                "Email": u.email,
                "Pass": u.password,
                "Role": u.role,
                "Dept ID": u.department_id,
                "Reports To": u.reports_to
            })
        print(pd.DataFrame(data).to_string(index=False))

    print(f"\n{'='*20} STUDENTS {'='*20}")
    students = session.query(User).all()
    data = []
    for s in students:
        data.append({
            "ID": s.id,
            "Name": s.name,
            "Email": s.email,
            "Pass": s.password,
            "Section ID": s.section_id,
            "Proctor ID": s.reports_to
        })
    print(pd.DataFrame(data[:300]).to_string(index=False))

    print_table("ISSUES", Issue, ["id", "title", "status", "assigned_to", "forwarded_by", "student_id"])

finally:
    session.close()
    print("\nVerification Complete.")