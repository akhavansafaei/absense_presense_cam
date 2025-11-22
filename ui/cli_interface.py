from database import DatabaseManager
from face_module import FaceRegistrar, FaceRecognizer
from utils import AttendanceReporter
from datetime import datetime, date, timedelta
import os


class CLIInterface:
    """Command-line interface for the attendance system."""

    def __init__(self):
        """Initialize CLI interface."""
        self.db = DatabaseManager()
        self.face_registrar = FaceRegistrar()
        self.reporter = AttendanceReporter(self.db)

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        """Print application header."""
        print("\n" + "="*70)
        print(" "*15 + "WEBCAM ATTENDANCE SYSTEM")
        print("="*70)

    def print_menu(self):
        """Print main menu."""
        stats = self.reporter.get_statistics()

        print(f"\nSystem Statistics:")
        print(f"  Total People: {stats['total_people']}")
        print(f"  Present Today: {stats['present_today']}")
        print(f"  Absent Today: {stats['absent_today']}")

        print("\n" + "-"*70)
        print("MAIN MENU:")
        print("-"*70)
        print("1. Start Attendance Monitoring (Webcam)")
        print("2. Add New Person")
        print("3. Remove Person")
        print("4. View All People")
        print("5. View Today's Attendance")
        print("6. View Person Attendance History")
        print("7. View Attendance Summary Report")
        print("8. Export Today's Attendance to CSV")
        print("9. Manual Attendance Entry")
        print("0. Exit")
        print("-"*70)

    def add_person_menu(self):
        """Handle adding a new person."""
        print("\n" + "="*70)
        print("ADD NEW PERSON")
        print("="*70)

        name = input("\nEnter person's name: ").strip()
        if not name:
            print("Error: Name cannot be empty!")
            return

        # Check if person already exists
        existing = self.db.get_person_by_name(name)
        if existing:
            print(f"Error: Person '{name}' already exists in the database!")
            return

        print("\nSelect role:")
        print("1. Student")
        print("2. Employee")
        print("3. Teacher")
        print("4. Other")

        role_choice = input("\nEnter choice (1-4): ").strip()
        role_map = {
            '1': 'Student',
            '2': 'Employee',
            '3': 'Teacher',
            '4': input("Enter custom role: ").strip()
        }

        role = role_map.get(role_choice, 'Other')

        print("\nSelect registration method:")
        print("1. Capture from webcam")
        print("2. Load from image file")

        method = input("\nEnter choice (1-2): ").strip()

        face_encoding = None
        image_path = None

        if method == '1':
            # Capture from webcam
            face_encoding, image_path = self.face_registrar.capture_face_from_webcam(name)
        elif method == '2':
            # Load from file
            file_path = input("Enter image file path: ").strip()
            face_encoding = self.face_registrar.load_face_from_image(file_path)
            image_path = file_path
        else:
            print("Invalid choice!")
            return

        if face_encoding is None:
            print("Failed to register face!")
            return

        # Add to database
        if self.db.add_person(name, role, face_encoding, image_path):
            print(f"\n✓ Successfully added {name} ({role}) to the database!")
        else:
            print(f"\n✗ Failed to add {name} to the database!")

    def remove_person_menu(self):
        """Handle removing a person."""
        print("\n" + "="*70)
        print("REMOVE PERSON")
        print("="*70)

        # Show all people
        people = self.db.get_all_people()

        if not people:
            print("\nNo people in the database!")
            return

        print("\nCurrent people in database:")
        for idx, person in enumerate(people, 1):
            print(f"{idx}. {person[1]} ({person[2]})")

        choice = input("\nEnter person name to remove (or 'cancel' to go back): ").strip()

        if choice.lower() == 'cancel':
            return

        # Confirm deletion
        confirm = input(f"\nAre you sure you want to remove '{choice}'? (yes/no): ").strip().lower()

        if confirm == 'yes':
            if self.db.remove_person(choice):
                print(f"\n✓ Successfully removed {choice} from the database!")
            else:
                print(f"\n✗ Failed to remove {choice}!")
        else:
            print("Removal cancelled.")

    def view_all_people_menu(self):
        """Display all people in the database."""
        print("\n" + "="*70)
        print("ALL PEOPLE IN DATABASE")
        print("="*70)

        people = self.db.get_all_people()

        if not people:
            print("\nNo people in the database!")
            return

        print(f"\n{'ID':<5} {'Name':<25} {'Role':<15} {'Added On':<20}")
        print("-"*70)

        for person in people:
            person_id, name, role, created_at = person
            created_date = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M')
            print(f"{person_id:<5} {name:<25} {role:<15} {created_date:<20}")

        print(f"\nTotal: {len(people)} people")

    def start_monitoring_menu(self):
        """Start webcam attendance monitoring."""
        print("\n" + "="*70)
        print("STARTING ATTENDANCE MONITORING")
        print("="*70)

        # Load all known faces
        known_faces = self.db.get_all_face_encodings()

        if not known_faces:
            print("\nNo people in the database! Please add people first.")
            return

        print(f"\nLoaded {len(known_faces)} known faces.")

        # Define recognition callback
        def on_person_recognized(person_id: int, name: str):
            """Called when a person is recognized."""
            self.db.mark_attendance(person_id)

        # Start recognition
        recognizer = FaceRecognizer(known_faces)
        recognizer.recognize_faces_from_webcam(on_recognition=on_person_recognized)

    def view_today_attendance_menu(self):
        """View today's attendance."""
        self.reporter.print_daily_report()
        input("\nPress Enter to continue...")

    def view_person_history_menu(self):
        """View person attendance history."""
        print("\n" + "="*70)
        print("PERSON ATTENDANCE HISTORY")
        print("="*70)

        name = input("\nEnter person's name: ").strip()
        if not name:
            print("Error: Name cannot be empty!")
            return

        days = input("Enter number of days to look back (default 30): ").strip()
        days = int(days) if days.isdigit() else 30

        self.reporter.print_person_history(name, days)
        input("\nPress Enter to continue...")

    def view_summary_report_menu(self):
        """View attendance summary report."""
        print("\n" + "="*70)
        print("ATTENDANCE SUMMARY REPORT")
        print("="*70)

        print("\nSelect date range:")
        print("1. Last 7 days")
        print("2. Last 30 days")
        print("3. This month")
        print("4. Custom range")

        choice = input("\nEnter choice (1-4): ").strip()

        today = date.today()

        if choice == '1':
            start_date = today - timedelta(days=7)
            end_date = today
        elif choice == '2':
            start_date = today - timedelta(days=30)
            end_date = today
        elif choice == '3':
            start_date = today.replace(day=1)
            end_date = today
        elif choice == '4':
            start_str = input("Enter start date (YYYY-MM-DD): ").strip()
            end_str = input("Enter end date (YYYY-MM-DD): ").strip()
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                print("Invalid date format!")
                return
        else:
            print("Invalid choice!")
            return

        self.reporter.print_summary_report(start_date, end_date)
        input("\nPress Enter to continue...")

    def export_csv_menu(self):
        """Export today's attendance to CSV."""
        print("\n" + "="*70)
        print("EXPORT ATTENDANCE TO CSV")
        print("="*70)

        target_date = date.today()
        print(f"\nExporting attendance for {target_date.strftime('%Y-%m-%d')}...")

        if self.reporter.export_to_csv(target_date):
            print("✓ Export successful!")
        else:
            print("✗ Export failed!")

        input("\nPress Enter to continue...")

    def manual_attendance_menu(self):
        """Manual attendance entry."""
        print("\n" + "="*70)
        print("MANUAL ATTENDANCE ENTRY")
        print("="*70)

        # Show all people
        people = self.db.get_all_people()

        if not people:
            print("\nNo people in the database!")
            return

        print("\nSelect person:")
        for idx, person in enumerate(people, 1):
            print(f"{idx}. {person[1]} ({person[2]})")

        choice = input("\nEnter person number: ").strip()

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(people):
            print("Invalid choice!")
            return

        person = people[int(choice) - 1]
        person_id = person[0]
        name = person[1]

        if self.db.mark_attendance(person_id):
            print(f"\n✓ Attendance marked for {name}!")
        else:
            print(f"\n✗ Failed to mark attendance for {name}!")

        input("\nPress Enter to continue...")

    def run(self):
        """Run the main application loop."""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            choice = input("\nEnter your choice (0-9): ").strip()

            if choice == '0':
                print("\nThank you for using Webcam Attendance System!")
                self.db.close()
                break
            elif choice == '1':
                self.start_monitoring_menu()
            elif choice == '2':
                self.add_person_menu()
                input("\nPress Enter to continue...")
            elif choice == '3':
                self.remove_person_menu()
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.view_all_people_menu()
                input("\nPress Enter to continue...")
            elif choice == '5':
                self.view_today_attendance_menu()
            elif choice == '6':
                self.view_person_history_menu()
            elif choice == '7':
                self.view_summary_report_menu()
            elif choice == '8':
                self.export_csv_menu()
            elif choice == '9':
                self.manual_attendance_menu()
            else:
                print("\nInvalid choice! Please try again.")
                input("\nPress Enter to continue...")
