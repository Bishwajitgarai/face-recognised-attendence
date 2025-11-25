# Face Recognized Attendance System

A Flask-based web application that leverages face recognition technology to automate attendance tracking for employees.

## Features

- **Admin Dashboard**: Secure login for administrators to manage the system.
- **Employee Management**: Add, edit, and delete employee records, including photo uploads for face recognition training.
- **Real-time Attendance**: Capture attendance for entry and exit using a webcam.
- **Face Recognition**: Uses `face_recognition` and OpenCV to identify registered employees.
- **Attendance Reports**: Download attendance records as Excel files.
- **Visual Feedback**: Displays bounding boxes and names on the live video feed.

## Prerequisites

- Python 3.x
- CMake (required for `dlib` installation, which is a dependency of `face_recognition`)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd face-recognised-attendence
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    # OR if using Pipenv
    pipenv install
    ```
    *Note: Ensure you have the necessary build tools installed for `dlib`.*

3.  **Initialize the database:**
    The application will automatically create `faceattendence.db` on the first run if it doesn't exist.

## Usage

1.  **Run the application:**
    ```bash
    python run.py
    ```

2.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

3.  **Admin Login:**
    -   Default Admin Credentials (created on first run if not exists):
        -   Username: `admin`
        -   Password: `1234`

4.  **Workflow:**
    -   **Add Employee**: Go to the dashboard and add a new employee with their photo.
    -   **Mark Attendance**: Use the "Entry" or "Exit" pages to start the camera and mark attendance.
    -   **Download Reports**: Go to the employee list and download attendance logs.

## Project Structure

-   `app.py`: Core logic for face recognition and processing.
-   `run.py`: Main Flask application entry point and route definitions.
-   `templates/`: HTML templates for the web interface.
-   `faces/`: Directory to store employee images (ignored by git).
-   `excels/`: Directory to store generated excel reports (ignored by git).
-   `data/`: Contains Haar Cascade XML for face detection.

## License

[MIT License](LICENSE)
