# **CampusMind – Intelligent Campus Issue Management System**

*A Unified, ML-Powered Grievance & Workflow Platform for Modern Engineering Colleges*

Live Deployment:
🔗 [https://campusmind-sife.onrender.com/](https://campusmind-sife.onrender.com/)

---

# **1. Overview**

Engineering colleges run on daily communication between **students**, **proctors**, **HODs**, **administration**, and **support staff**.
But most institutions still rely on **WhatsApp messages**, **manual notes**, and **verbal escalations** to manage issues.

This causes:

* Important issues getting **lost** in chat groups
* Proctors unable to track 300–500 student messages
* Students not knowing **whom to approach**
* No accountability or audit trail
* No analytics for HOD/VC to understand ground reality

**CampusMind** solves this by creating a structured, centralized, AI-driven issue tracking system designed for real engineering college workflows.

---

# **2. Why Colleges Need CampusMind**

### **2.1 WhatsApp is not a Tracking System**

| Problem                   | Result                                   |
| ------------------------- | ---------------------------------------- |
| Messages buried in groups | Critical issues missed                   |
| Unlimited message formats | No structured data                       |
| No status tracking        | Students feel ignored                    |
| No escalation mechanism   | HOD/VC never see issues                  |
| No analytics              | Management cannot improve campus systems |

Engineering campuses need **traceability**, **automation**, and **visibility**.

---

# **3. What CampusMind Offers**

### ✔ **Smart Issue Submission**

Students submit issues with a simple form.
ML automatically predicts:

* **Category** (academic, infrastructure, network, hostel, etc.)
* **Priority** (urgent/high/medium/low)

### ✔ **Hierarchical Workflow**

CampusMind embeds the actual college structure:

```
VC → HOD → Proctor → Students
```

Issues automatically reach the correct authority based on student details.

### ✔ **Proctor Control Panel**

Proctors can:

* See all issues from their section
* Verify or reject issues
* Reassign categories if needed
* Assign issues to HOD or maintenance staff

### ✔ **HOD/VC Dashboard**

Department-level and campus-level visibility.

### ✔ **Real College Simulation**

Database seeding generates:

* 7 departments
* 14 sections
* 700 students
* 14 proctors
* 7 HODs
* 1 VC

Perfect for demos and testing.

---

# **4. Project Structure**

```
CampusMind/
│
├── app.py                -> Streamlit dashboard UI (optional frontend)
├── main.py               -> Primary FastAPI backend server
├── models.py             -> SQLAlchemy ORM models
├── schemas.py            -> Pydantic request/response models
├── seed_db.py            -> Auto-load realistic campus hierarchy
├── delete_db.py          -> Clear database
├── check_db.py           -> Inspect DB contents
│
├── category_pipe.pkl     -> ML model for issue categorization
│
├── data/
│   └── issue_manager.db  -> SQLite database (auto-created)
│
├── static/
│   ├── index.html        -> Final polished HTML/CSS/JS user interface
│   ├── css/
│   └── js/
│
└── requirements.txt      -> Python dependencies
```

---

# **5. How CampusMind Works (Workflow)**

### **1. Student submits an issue → backend receives it**

Example:

```
"Fan not working in CSE lab A"
```

### **2. ML model predicts**

* Category: infrastructure
* Priority: medium

### **3. Backend routes issue**

System checks:

* student’s department
* student’s section
* assigned proctor

### **4. Proctor Dashboard**

Proctor verifies / rejects / reassigns / assigns.

### **5. HOD & VC Oversight**

Full transparency with analytics scope.

---

# **6. Running the Project Locally**

## **Option A — Run the Backend (FastAPI)**

This is required for both Streamlit UI and static UI.

```bash
uvicorn main:app --reload
```

FastAPI interactive docs:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## **Option B — Run the Streamlit Interface (app.py)**

This UI is meant for **testing, prototyping, and internal demonstration** (easier dashboards, quick role switching).

```bash
streamlit run app.py
```

Features in Streamlit UI:

* Mock login (student, proctor, HOD, admin)
* Submit issues
* View issues
* Proctor verification workflow
* Assign issues
* Basic statistics dashboard

Used for:

* Developer testing
* Hackathon demos
* Internal quality checks

---

## **Option C — Use the Production HTML UI (static/index.html)**

This is the **final professional frontend** intended for real deployment.

### If using FastAPI static mount:

Direct access at:

```
http://127.0.0.1:8000/
```

Or open `static/index.html` manually during local development.

This interface:

* Provides clean and responsive student submission UI
* Integrates with backend using JS fetch API
* Suitable for real campus usage and deployment on Render/Vercel/Cloudflare Pages

---

# **7. Technology Stack**

### **Backend**

* FastAPI (core REST API)
* SQLAlchemy ORM (database)
* SQLite (simple hackathon-friendly database)
* Pydantic (data validation)
* Uvicorn (server)

### **ML Engine**

* TF-IDF Vectorizer
* Logistic Regression classifier
* Joblib serialization

### **Frontend**

* Clean HTML/CSS/JavaScript UI under `/static`
* Optional Streamlit dashboard (`app.py`)

### **Deployment**

* Render (web service)
* Auto-start with `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

# **8. Future Enhancements**

* JWT authentication for secure roles
* Push notification alerts (Firebase)
* PDF notice workflow (VC → HOD → Proctor → Students)
* Visual analytics dashboard
* SLAs & time-to-resolution metrics
* Mobile app version (Flutter)

---

# **9. Why CampusMind Makes Sense for Real Colleges**

### **For Students**

* No need to search “Which proctor should I ask?”
* Guaranteed response tracking
* Transparent workflow
* Faster issue resolution

### **For Proctors**

* No spam
* No lost messages
* Highlighted urgent issues
* Simple verify/assign flow
* Organized dashboard

### **For HOD**

* 360° visibility into department issues
* Identify repeating problems
* Improve resource allocation

### **For VC/Admin**

* Campus-wide analytics
* SLA reports
* Identify systemic failures
* Improve student satisfaction and safety

CampusMind replaces chaos with **structured communication + automation + transparency**.

---

# **10. Conclusion**

CampusMind is a complete issue-management ecosystem designed to solve a real, everyday problem in engineering colleges.

It combines:

* NLP-powered classification
* A strong backend workflow engine
* A realistic academic hierarchy
* Clean UI options
* Full cloud deployment

This makes it a powerful, practical, and scalable solution ready for real-world adoption.