import sqlite3
import pickle
import os
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict


class DatabaseManager:
    """Manages the SQLite database for people and attendance records."""

    def __init__(self, db_path: str = "data/database/attendance.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables for the attendance system."""
        # People table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                face_encoding BLOB NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Attendance table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                date DATE NOT NULL,
                time_in TIMESTAMP,
                time_out TIMESTAMP,
                status TEXT DEFAULT 'present',
                FOREIGN KEY (person_id) REFERENCES people (id),
                UNIQUE(person_id, date)
            )
        ''')

        self.conn.commit()

    def add_person(self, name: str, role: str, face_encoding, image_path: str = None) -> bool:
        """
        Add a new person to the database.

        Args:
            name: Person's name
            role: Role (student/employee/etc.)
            face_encoding: Face encoding array from face_recognition
            image_path: Path to the person's image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize face encoding
            encoding_blob = pickle.dumps(face_encoding)

            self.cursor.execute('''
                INSERT INTO people (name, role, face_encoding, image_path)
                VALUES (?, ?, ?, ?)
            ''', (name, role, encoding_blob, image_path))

            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Error: Person with name '{name}' already exists!")
            return False
        except Exception as e:
            print(f"Error adding person: {e}")
            return False

    def remove_person(self, name: str) -> bool:
        """
        Remove a person from the database.

        Args:
            name: Person's name

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get person ID
            person_id = self._get_person_id(name)
            if person_id is None:
                print(f"Error: Person '{name}' not found!")
                return False

            # Delete attendance records
            self.cursor.execute('DELETE FROM attendance WHERE person_id = ?', (person_id,))

            # Delete person
            self.cursor.execute('DELETE FROM people WHERE id = ?', (person_id,))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error removing person: {e}")
            return False

    def get_all_people(self) -> List[Tuple]:
        """Get all people from the database."""
        self.cursor.execute('SELECT id, name, role, created_at FROM people ORDER BY name')
        return self.cursor.fetchall()

    def get_person_by_name(self, name: str) -> Optional[Tuple]:
        """Get person details by name."""
        self.cursor.execute('SELECT id, name, role, created_at FROM people WHERE name = ?', (name,))
        return self.cursor.fetchone()

    def get_all_face_encodings(self) -> List[Tuple]:
        """
        Get all face encodings with person information.

        Returns:
            List of tuples (person_id, name, face_encoding)
        """
        self.cursor.execute('SELECT id, name, face_encoding FROM people')
        results = []
        for row in self.cursor.fetchall():
            person_id, name, encoding_blob = row
            face_encoding = pickle.loads(encoding_blob)
            results.append((person_id, name, face_encoding))
        return results

    def _get_person_id(self, name: str) -> Optional[int]:
        """Get person ID by name."""
        self.cursor.execute('SELECT id FROM people WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def mark_attendance(self, person_id: int, time_in: datetime = None) -> bool:
        """
        Mark attendance for a person.

        Args:
            person_id: Person's ID
            time_in: Time of arrival (defaults to current time)

        Returns:
            True if successful, False otherwise
        """
        try:
            if time_in is None:
                time_in = datetime.now()

            today = date.today()

            # Check if attendance already exists for today
            self.cursor.execute('''
                SELECT id FROM attendance WHERE person_id = ? AND date = ?
            ''', (person_id, today))

            existing = self.cursor.fetchone()

            if existing:
                # Update time_in if earlier, or time_out if later
                self.cursor.execute('''
                    UPDATE attendance
                    SET time_out = ?
                    WHERE person_id = ? AND date = ?
                ''', (time_in, person_id, today))
            else:
                # Create new attendance record
                self.cursor.execute('''
                    INSERT INTO attendance (person_id, date, time_in, status)
                    VALUES (?, ?, ?, 'present')
                ''', (person_id, today, time_in))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False

    def get_attendance_by_date(self, target_date: date = None) -> List[Dict]:
        """
        Get attendance records for a specific date.

        Args:
            target_date: Date to query (defaults to today)

        Returns:
            List of attendance records with person information
        """
        if target_date is None:
            target_date = date.today()

        self.cursor.execute('''
            SELECT p.name, p.role, a.time_in, a.time_out, a.status
            FROM attendance a
            JOIN people p ON a.person_id = p.id
            WHERE a.date = ?
            ORDER BY p.name
        ''', (target_date,))

        results = []
        for row in self.cursor.fetchall():
            results.append({
                'name': row[0],
                'role': row[1],
                'time_in': row[2],
                'time_out': row[3],
                'status': row[4]
            })
        return results

    def get_attendance_report(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Get attendance report for a date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of attendance records
        """
        self.cursor.execute('''
            SELECT p.name, p.role, a.date, a.time_in, a.time_out, a.status
            FROM attendance a
            JOIN people p ON a.person_id = p.id
            WHERE a.date BETWEEN ? AND ?
            ORDER BY a.date DESC, p.name
        ''', (start_date, end_date))

        results = []
        for row in self.cursor.fetchall():
            results.append({
                'name': row[0],
                'role': row[1],
                'date': row[2],
                'time_in': row[3],
                'time_out': row[4],
                'status': row[5]
            })
        return results

    def get_person_attendance_history(self, name: str, days: int = 30) -> List[Dict]:
        """
        Get attendance history for a specific person.

        Args:
            name: Person's name
            days: Number of days to look back

        Returns:
            List of attendance records
        """
        person_id = self._get_person_id(name)
        if person_id is None:
            return []

        self.cursor.execute('''
            SELECT date, time_in, time_out, status
            FROM attendance
            WHERE person_id = ? AND date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        ''', (person_id, days))

        results = []
        for row in self.cursor.fetchall():
            results.append({
                'date': row[0],
                'time_in': row[1],
                'time_out': row[2],
                'status': row[3]
            })
        return results

    def close(self):
        """Close database connection."""
        self.conn.close()
