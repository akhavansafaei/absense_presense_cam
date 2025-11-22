from datetime import date, datetime, timedelta
from typing import List, Dict
from database import DatabaseManager
import csv
import os


class AttendanceReporter:
    """Generates attendance reports and statistics."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize attendance reporter.

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def print_daily_report(self, target_date: date = None):
        """
        Print attendance report for a specific date.

        Args:
            target_date: Date to report (defaults to today)
        """
        if target_date is None:
            target_date = date.today()

        print(f"\n{'='*70}")
        print(f"ATTENDANCE REPORT - {target_date.strftime('%A, %B %d, %Y')}")
        print(f"{'='*70}")

        attendance_records = self.db.get_attendance_by_date(target_date)

        if not attendance_records:
            print("No attendance records found for this date.")
            return

        # Header
        print(f"\n{'Name':<25} {'Role':<15} {'Time In':<20} {'Status':<10}")
        print("-" * 70)

        # Records
        for record in attendance_records:
            time_in = record['time_in']
            if time_in:
                time_in_str = datetime.fromisoformat(time_in).strftime('%I:%M:%S %p')
            else:
                time_in_str = "N/A"

            print(f"{record['name']:<25} {record['role']:<15} {time_in_str:<20} {record['status']:<10}")

        print("-" * 70)
        print(f"Total Present: {len(attendance_records)}")
        print()

    def print_person_history(self, name: str, days: int = 30):
        """
        Print attendance history for a specific person.

        Args:
            name: Person's name
            days: Number of days to look back
        """
        print(f"\n{'='*70}")
        print(f"ATTENDANCE HISTORY - {name} (Last {days} days)")
        print(f"{'='*70}")

        history = self.db.get_person_attendance_history(name, days)

        if not history:
            print(f"No attendance records found for {name}.")
            return

        # Header
        print(f"\n{'Date':<15} {'Time In':<20} {'Time Out':<20} {'Status':<10}")
        print("-" * 70)

        # Records
        present_days = 0
        for record in history:
            record_date = datetime.strptime(record['date'], '%Y-%m-%d').strftime('%Y-%m-%d')

            time_in = record['time_in']
            time_in_str = datetime.fromisoformat(time_in).strftime('%I:%M:%S %p') if time_in else "N/A"

            time_out = record['time_out']
            time_out_str = datetime.fromisoformat(time_out).strftime('%I:%M:%S %p') if time_out else "N/A"

            print(f"{record_date:<15} {time_in_str:<20} {time_out_str:<20} {record['status']:<10}")

            if record['status'] == 'present':
                present_days += 1

        print("-" * 70)
        print(f"Total Days Present: {present_days}/{len(history)}")
        print(f"Attendance Rate: {(present_days/len(history)*100):.1f}%")
        print()

    def print_summary_report(self, start_date: date, end_date: date):
        """
        Print summary attendance report for a date range.

        Args:
            start_date: Start date
            end_date: End date
        """
        print(f"\n{'='*70}")
        print(f"ATTENDANCE SUMMARY REPORT")
        print(f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")
        print(f"{'='*70}")

        all_people = self.db.get_all_people()
        attendance_records = self.db.get_attendance_report(start_date, end_date)

        # Group by person
        person_stats = {}
        for person in all_people:
            person_id, name, role, _ = person
            person_stats[name] = {
                'role': role,
                'days_present': 0,
                'total_days': (end_date - start_date).days + 1
            }

        for record in attendance_records:
            name = record['name']
            if name in person_stats and record['status'] == 'present':
                person_stats[name]['days_present'] += 1

        # Print summary
        print(f"\n{'Name':<25} {'Role':<15} {'Days Present':<15} {'Rate':<10}")
        print("-" * 70)

        for name, stats in sorted(person_stats.items()):
            days_present = stats['days_present']
            total_days = stats['total_days']
            rate = (days_present / total_days * 100) if total_days > 0 else 0

            print(f"{name:<25} {stats['role']:<15} {days_present}/{total_days:<10} {rate:>6.1f}%")

        print()

    def export_to_csv(self, target_date: date, output_path: str = None):
        """
        Export attendance report to CSV file.

        Args:
            target_date: Date to export
            output_path: Output file path (auto-generated if not provided)
        """
        if output_path is None:
            os.makedirs("reports", exist_ok=True)
            output_path = f"reports/attendance_{target_date.strftime('%Y%m%d')}.csv"

        attendance_records = self.db.get_attendance_by_date(target_date)

        try:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = ['Name', 'Role', 'Date', 'Time In', 'Time Out', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for record in attendance_records:
                    writer.writerow({
                        'Name': record['name'],
                        'Role': record['role'],
                        'Date': target_date.strftime('%Y-%m-%d'),
                        'Time In': record['time_in'] or '',
                        'Time Out': record['time_out'] or '',
                        'Status': record['status']
                    })

            print(f"Report exported to: {output_path}")
            return True

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        Get overall system statistics.

        Returns:
            Dictionary with system statistics
        """
        all_people = self.db.get_all_people()
        today_attendance = self.db.get_attendance_by_date(date.today())

        return {
            'total_people': len(all_people),
            'present_today': len(today_attendance),
            'absent_today': len(all_people) - len(today_attendance)
        }
