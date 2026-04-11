import sqlite3
import os

db_path = 'db.sqlite3'

def insert_doctor_raw():
    try:
        conn = sqlite3.connect(db_path, timeout=60) # 60 seconds timeout
        cursor = conn.cursor()
        
        # doctor table name is clinicadmin_tbl_doctor
        # columns: name, age, gender, email, phone_number, address, specialization, qualification, medical_registration_number, password
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
        print("Doctor inserted successfully via raw SQL")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_doctor_raw()
