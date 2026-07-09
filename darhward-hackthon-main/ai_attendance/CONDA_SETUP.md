# Conda Installation Steps for AI Attendance System

## Step-by-Step Guide

### Step 1: Create Conda Environment (In Progress)
```bash
conda create -n attendance python=3.9
```
**Status**: Running...

### Step 2: Activate Environment
```bash
conda activate attendance
```

### Step 3: Install dlib via Conda
```bash
conda install -c conda-forge dlib
```

### Step 4: Install Python Packages
```bash
pip install face-recognition Flask opencv-python numpy Pillow
```

### Step 5: Initialize Database
```bash
python database.py
```

### Step 6: Run Application
```bash
python app.py
```

### Step 7: Open Browser
Navigate to: **http://127.0.0.1:5000**

---

## Important Notes

- ✅ Always activate the environment before running: `conda activate attendance`
- ✅ The environment is isolated - packages won't conflict with your system Python
- ✅ To deactivate: `conda deactivate`
- ✅ To remove environment later: `conda env remove -n attendance`

---

## Quick Reference

**Activate environment**:
```bash
conda activate attendance
```

**Run the app**:
```bash
cd "c:\Users\91984\Desktop\ai attendence"
python app.py
```

**Deactivate when done**:
```bash
conda deactivate
```
