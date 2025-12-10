import os

DB_DIR = "data"
DB_FILE = "issue_manager.db"
DB_PATH = os.path.join(DB_DIR, DB_FILE)

def delete_database():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"Sucessfully deleted database file: {DB_PATH}")
            print(f"Run 'seed_db.py' to recreate schema and data")
        except PermissionError:
            print(f"Error: Permission denied")
            print("Close any application using database")
        except Exception as e:
            print(f"Error occured: {e}")
    else:
        print(f"Database file not found at : {DB_PATH}")
        print("Nothing to delete")

if __name__ == "__main__":
    delete_database()