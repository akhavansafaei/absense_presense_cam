"# Webcam Attendance System

A simple yet powerful face recognition-based attendance monitoring system that uses a webcam to automatically track the presence and absence of students or employees.

## Features

- **Face Recognition**: Automatic face detection and recognition using webcam
- **Database Management**: Add and remove people from the system database
- **Real-time Monitoring**: Live attendance tracking with visual feedback
- **Attendance Reports**: Daily, historical, and summary reports
- **CSV Export**: Export attendance data for external use
- **Manual Entry**: Option to manually mark attendance when needed
- **Multiple Roles**: Support for students, employees, teachers, and custom roles

## System Requirements

- Python 3.7 or higher
- Webcam
- Linux/macOS/Windows

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd absense_presense_cam
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The `face_recognition` library requires `dlib` which may need additional system dependencies:

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

**On macOS:**
```bash
brew install cmake
```

**On Windows:**
- Install Visual Studio Build Tools
- Or use pre-built wheels from [here](https://github.com/ageitgey/face_recognition/issues)

## Project Structure

```
absense_presense_cam/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── database/              # Database management module
│   ├── __init__.py
│   └── database_manager.py
├── face_module/           # Face recognition module
│   ├── __init__.py
│   ├── face_registrar.py
│   └── face_recognizer.py
├── ui/                    # User interface
│   ├── __init__.py
│   └── cli_interface.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── attendance_reporter.py
├── data/                  # Data storage
│   ├── database/         # SQLite database files
│   └── face_images/      # Stored face images
└── reports/              # Generated attendance reports
```

## Usage

### Starting the Application

```bash
python main.py
```

### Main Menu Options

The application provides an interactive command-line interface with the following options:

#### 1. Start Attendance Monitoring (Webcam)
- Starts real-time face recognition using your webcam
- Automatically marks attendance when faces are recognized
- Shows recognized faces with green boxes
- Unknown faces are shown with red boxes
- Press 'q' or ESC to stop monitoring

#### 2. Add New Person
- Register a new person in the system
- Choose to capture face from webcam or load from image file
- Supports multiple roles (Student, Employee, Teacher, etc.)
- Face encoding is automatically generated and stored

#### 3. Remove Person
- Remove a person from the database
- Deletes all associated attendance records
- Requires confirmation before deletion

#### 4. View All People
- Lists all registered people
- Shows ID, name, role, and registration date

#### 5. View Today's Attendance
- Displays attendance records for the current day
- Shows name, role, time in, and status
- Provides total count of present people

#### 6. View Person Attendance History
- Shows attendance history for a specific person
- Configurable date range (default: last 30 days)
- Displays attendance rate percentage

#### 7. View Attendance Summary Report
- Generate summary reports for date ranges
- Options: Last 7 days, Last 30 days, This month, Custom range
- Shows attendance rate for each person

#### 8. Export Today's Attendance to CSV
- Export attendance data to CSV format
- Saved in the `reports/` directory
- Easy to import into Excel or other tools

#### 9. Manual Attendance Entry
- Manually mark attendance for a person
- Useful when automatic recognition fails
- Records attendance with current timestamp

## Quick Start Guide

### Step 1: Add People to the Database

1. Run the application: `python main.py`
2. Select option `2` (Add New Person)
3. Enter the person's name and role
4. Choose registration method:
   - **Webcam capture**: Position yourself in front of the camera and press SPACE
   - **Image file**: Provide path to an image file containing the person's face
5. Repeat for all people you want to track

### Step 2: Start Monitoring

1. Select option `1` (Start Attendance Monitoring)
2. The webcam will activate and start recognizing faces
3. When a registered person is detected, their attendance is automatically marked
4. Press 'q' or ESC to stop monitoring

### Step 3: View Reports

1. Select option `5` to view today's attendance
2. Select option `7` for summary reports
3. Select option `8` to export data to CSV

## Database Schema

### People Table
- `id`: Primary key
- `name`: Person's name (unique)
- `role`: Role (student/employee/etc.)
- `face_encoding`: Serialized face encoding
- `image_path`: Path to stored image
- `created_at`: Registration timestamp

### Attendance Table
- `id`: Primary key
- `person_id`: Foreign key to people table
- `date`: Attendance date
- `time_in`: Check-in time
- `time_out`: Check-out time
- `status`: Attendance status (present/absent)

## Troubleshooting

### Webcam not detected
- Ensure your webcam is properly connected
- Check if other applications are using the webcam
- Try running with different camera indices if you have multiple cameras

### Face not recognized
- Ensure good lighting conditions
- Look directly at the camera
- Make sure your face is clearly visible
- Adjust the recognition tolerance in the code if needed

### Installation issues with face_recognition
- Ensure all system dependencies are installed (see Installation section)
- Try installing dlib separately: `pip install dlib`
- On Windows, consider using pre-built wheels

### Database locked errors
- Ensure no other instance of the application is running
- Check file permissions in the `data/database/` directory

## Tips for Best Results

1. **Good Lighting**: Ensure the area is well-lit when registering and recognizing faces
2. **Clear Images**: Use high-quality, front-facing images when registering from files
3. **Single Person**: Only one person should be in frame during registration
4. **Consistent Appearance**: Major changes in appearance (glasses, facial hair, etc.) may affect recognition
5. **Camera Position**: Position the camera at face level for best results

## Security Considerations

- Face encodings are stored in the database, not the actual images
- Keep the database file secure and backed up regularly
- Limit access to the application and data directories
- Consider encrypting sensitive data in production environments

## Future Enhancements

Potential improvements for the system:
- Web-based interface
- Multiple camera support
- Email/SMS notifications
- Integration with HR/school management systems
- Advanced reporting with charts and graphs
- Cloud storage for face data
- Mobile app support

## License

This project is open source and available for educational and commercial use.

## Support

For issues, questions, or contributions, please open an issue in the repository.

## Credits

Built using:
- [OpenCV](https://opencv.org/) - Computer vision library
- [face_recognition](https://github.com/ageitgey/face_recognition) - Face recognition library
- [SQLite](https://www.sqlite.org/) - Database engine" 
