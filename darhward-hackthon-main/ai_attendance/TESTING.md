# 🧪 Testing Guide - AI Attendance System

## Quick Start Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On Windows, if dlib installation fails, you may need to install Visual Studio Build Tools or use a pre-built wheel.

### 2. Initialize Database

```bash
python database.py
```

Expected output:
```
✅ Database initialized successfully
```

### 3. Test Camera

```bash
python camera.py
```

This opens a test window. Press 'Q' to quit.

### 4. Start Flask Server

```bash
python app.py
```

Expected output:
```
==================================================
🎓 AI Attendance System Starting...
==================================================

✅ Loaded 0 registered faces

📍 Server running at: http://127.0.0.1:5000
Press CTRL+C to stop
```

## Detailed Testing Procedures

### Test 1: Student Registration

**Objective**: Verify face capture and encoding storage

**Steps**:
1. Open browser: `http://127.0.0.1:5000`
2. Click "Register Student"
3. Enter:
   - Name: Test Student 1
   - Roll Number: TEST001
4. Click "Start Face Capture"
5. Camera window opens
6. Face the camera, move head slightly
7. Wait for 25 images to be captured
8. Window closes automatically

**Expected Result**:
- ✅ Success message: "Student Test Student 1 registered successfully!"
- ✅ Redirected to dashboard
- ✅ Student appears in "Registered Students" table

**Troubleshooting**:
- If "No face detected": Improve lighting, face camera directly
- If "Multiple faces detected": Ensure only one person in frame
- If "Face too small": Move closer to camera

### Test 2: Face Recognition

**Objective**: Verify AI recognition and attendance marking

**Steps**:
1. From home page, click "Start Attendance"
2. Camera window opens with live feed
3. Face the camera
4. Green bounding box appears with name and confidence %
5. After 3 consecutive recognitions, window closes

**Expected Result**:
- ✅ Face detected with green box
- ✅ Name displayed: "Test Student 1 (XX.X%)"
- ✅ Success message: "Attendance marked for Test Student 1"
- ✅ Window auto-closes

**Troubleshooting**:
- If "Unknown" appears: Re-register with better images
- If low confidence (<60%): Improve lighting, face directly
- If no detection: Move closer, ensure face is visible

### Test 3: Duplicate Prevention

**Objective**: Verify attendance can't be marked twice

**Steps**:
1. Immediately after Test 2, click "Start Attendance" again
2. Face camera and get recognized

**Expected Result**:
- ✅ Recognition works
- ✅ Message: "Recognized Test Student 1 but attendance already marked today"

### Test 4: Dashboard Functionality

**Objective**: Verify dashboard displays correct data

**Steps**:
1. Navigate to Dashboard
2. Check statistics cards
3. Verify student list
4. Verify attendance records

**Expected Result**:
- ✅ Total Students: 1
- ✅ Total Attendance Records: 1
- ✅ Today's Attendance: 1
- ✅ Student table shows "Test Student 1"
- ✅ Attendance table shows today's record

### Test 5: Date Filtering

**Objective**: Verify date filter works

**Steps**:
1. In dashboard, select today's date from date picker
2. Table updates
3. Clear date (reload page)
4. All records shown

**Expected Result**:
- ✅ Filtering shows only today's records
- ✅ Clearing shows all records

### Test 6: CSV Export

**Objective**: Verify CSV export functionality

**Steps**:
1. In dashboard, click "Export CSV"
2. File downloads
3. Open CSV file

**Expected Result**:
- ✅ File downloads: `attendance_YYYYMMDD_HHMMSS.csv`
- ✅ Contains headers: ID, Name, Timestamp, Status
- ✅ Contains attendance record

### Test 7: Multiple Students

**Objective**: Verify system handles multiple students

**Steps**:
1. Register 3 more students (TEST002, TEST003, TEST004)
2. Mark attendance for each
3. Verify dashboard shows all

**Expected Result**:
- ✅ All 4 students registered
- ✅ All 4 attendance records
- ✅ Dashboard shows correct counts

### Test 8: API Endpoints

**Objective**: Verify API endpoints work

**Test GET /api/students**:
```bash
curl http://127.0.0.1:5000/api/students
```

Expected:
```json
{
  "success": true,
  "students": [...]
}
```

**Test GET /api/attendance**:
```bash
curl http://127.0.0.1:5000/api/attendance
```

Expected:
```json
{
  "success": true,
  "records": [...]
}
```

**Test with date filter**:
```bash
curl "http://127.0.0.1:5000/api/attendance?date=2024-11-28"
```

### Test 9: Error Handling

**Test Empty Registration**:
1. Try to register without name/roll number
2. Expected: Error message

**Test Duplicate Registration**:
1. Try to register same student twice
2. Expected: "Student already exists" error

**Test Recognition with No Students**:
1. Delete database
2. Initialize new database
3. Try to start attendance
4. Expected: "No students registered yet" error

## Performance Testing

### Recognition Speed Test

**Objective**: Measure FPS during recognition

**Method**:
1. Add FPS counter to camera.py
2. Run recognition
3. Measure average FPS

**Expected**: 25-30 FPS on modern CPU

### Database Stress Test

**Objective**: Test with many students

**Method**:
1. Create script to register 100 students
2. Test recognition speed
3. Test dashboard load time

**Expected**: No significant slowdown

## Security Testing

### Test 1: Photo Attack

**Objective**: Check if system can be fooled by photo

**Steps**:
1. Take a photo of registered person
2. Show photo to camera during attendance
3. Check if recognized

**Current Result**: May be recognized (no liveness detection)
**Future**: Add blink detection

### Test 2: Database Integrity

**Objective**: Verify face images are secure

**Steps**:
1. Open database: `models/students.db`
2. Check `face_images` table
3. Verify `image` column contains BLOB data

**Expected**: Images stored as binary BLOBs used for training

## Automated Testing Script

Create `test_all.py`:

```python
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_home():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    print("✅ Home page loads")

def test_api_students():
    response = requests.get(f"{BASE_URL}/api/students")
    data = response.json()
    assert data['success'] == True
    print(f"✅ API returns {len(data['students'])} students")

def test_api_attendance():
    response = requests.get(f"{BASE_URL}/api/attendance")
    data = response.json()
    assert data['success'] == True
    print(f"✅ API returns {len(data['records'])} records")

if __name__ == "__main__":
    print("Running automated tests...\n")
    test_home()
    test_api_students()
    test_api_attendance()
    print("\n✅ All tests passed!")
```

Run with:
```bash
python test_all.py
```

## Checklist for Demo

Before presenting:

- [ ] Database initialized
- [ ] At least 2 students registered
- [ ] At least 1 attendance record
- [ ] Camera working
- [ ] Server running
- [ ] Browser tested
- [ ] CSV export tested
- [ ] Demo script reviewed

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Camera not opening | Close other apps using camera |
| Face not detected | Improve lighting, face camera |
| Low recognition confidence | Re-register with more images |
| dlib installation fails | Install Visual Studio Build Tools |
| Database locked | Close all connections, restart server |
| Port 5000 in use | Change port in app.py |

## Test Results Template

```
Test Date: ___________
Tester: ___________

Registration Test: ☐ Pass ☐ Fail
Recognition Test: ☐ Pass ☐ Fail
Dashboard Test: ☐ Pass ☐ Fail
Export Test: ☐ Pass ☐ Fail
API Test: ☐ Pass ☐ Fail

Notes:
_________________________________
_________________________________
_________________________________
```

---

**Happy Testing! 🧪**
