import sqlite3
import time

db_path = 'db.sqlite3'

def insert_doctor_persistent():
    print("Starting persistent insertion attempt...")
    start_time = time.time()
    # Try for up to 60 seconds manually in a loop to be sure
    while time.time() - start_time < 60:
        try:
            conn = sqlite3.connect(db_path, timeout=5) # 5 seconds per attempt
            cursor = conn.cursor()
            query = """
            INSERT INTO clinicadmin_tbl_doctor 
            (name, age, gender, email, phone_number, address, specialization, qualification, medical_registration_number, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            data = (
                'Dr. John Smith', 45, 'Male', 'johnsmith@example.com', 
                '+1234567890', '123 Medical Plaza, City', 'Dermatology', 
                'MBBS, MD', 'REG123456', 'password123'
            )
            cursor.execute(query, data)
            conn.commit()
            print("Doctor inserted successfully!")
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("Database still locked, retrying...")
                time.sleep(1)
            else:
                print(f"Operational Error: {e}")
                return False
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return False
    print("Failed to insert after 60 seconds.")
    return False

if __name__ == "__main__":
    insert_doctor_persistent()
