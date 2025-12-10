import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="CampusMind", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .title {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        letter-spacing: -1px;
        animation: fadeInDown 0.6s ease-out;
    }
    
    .small {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 30px;
        animation: fadeIn 0.8s ease-out;
    }
    
    .dashboard-title {
        font-size: 36px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .dashboard-title::before {
        content: '';
        width: 4px;
        height: 36px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    .user-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }
    
    .user-card:hover {
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        transform: translateY(-2px);
    }
    
    .info-item {
        padding: 12px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .info-value {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .badge-high {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .badge-medium {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    .badge-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .badge-open {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    .badge-forwarded {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .badge-closed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .badge-assigned {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 4px solid;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .stat-card.total {
        border-left-color: #667eea;
    }
    
    .stat-card.active {
        border-left-color: #3b82f6;
    }
    
    .stat-card.resolved {
        border-left-color: #10b981;
    }
    
    .login-container {
        max-width: 450px;
        margin: 100px auto;
        background: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid;
        border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
    }
    
    .issue-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .issue-card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
        border-left-color: #667eea;
    }
    
    .action-buttons {
        display: flex;
        gap: 12px;
        margin-top: 20px;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #64748b;
    }
    
    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    .sidebar .sidebar-content h1, .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
        color: white;
    }
    
    .metric-container {
        display: flex;
        gap: 20px;
        margin: 20px 0;
    }
    
    [data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stAlert {
        border-radius: 8px;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 30px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def safe_get(url, params=None, timeout=6):
    try:
        return requests.get(url, params=params, timeout=timeout)
    except Exception:
        return None

def safe_post(url, params=None, json=None, timeout=8):
    try:
        return requests.post(url, params=params, json=json, timeout=timeout)
    except Exception:
        return None

def api_login(email, password):
    r = safe_post(f"{API}/auth/login", params={"email": email, "password": password})
    return r.json() if r and r.status_code == 200 else None

def api_get_users():
    r = safe_get(f"{API}/users")
    return r.json() if r and r.status_code == 200 else []

def api_issues_for_user(uid, show_resolved=False):
    r = safe_get(f"{API}/issues/for_user/{uid}", params={"show_resolved": show_resolved})
    return r.json() if r and r.status_code == 200 else []

def api_create_issue(student_id, title, desc):
    return safe_post(f"{API}/issues", json={"student_id": student_id, "title": title, "description": desc})

def api_forward(issue_id, by_user_id):
    return safe_post(f"{API}/issues/{issue_id}/forward", params={"by_user_id": by_user_id})

def api_verify(issue_id, verifier_id, resolved=True):
    return safe_post(f"{API}/issues/{issue_id}/verify", params={"verifier_id": verifier_id, "resolved": resolved})

def api_reclassify(issue_id):
    return safe_post(f"{API}/issues/{issue_id}/classify")

def api_admin_stats():
    r = safe_get(f"{API}/admin/stats")
    return r.json() if r and r.status_code == 200 else {}

def api_admin_all_issues():
    r = safe_get(f"{API}/admin/issues")
    return r.json() if r and r.status_code == 200 else []

def api_get_department(dept_id):
    r = safe_get(f"{API}/departments/{dept_id}")
    return r.json() if r and r.status_code == 200 else None

def api_get_section(section_id):
    r = safe_get(f"{API}/sections/{section_id}")
    return r.json() if r and r.status_code == 200 else None

if "user" not in st.session_state:
    st.session_state.user = None
if "users_cache" not in st.session_state:
    st.session_state.users_cache = None

def load_users_cache():
    st.session_state.users_cache = api_get_users()

def get_user_by_id(uid):
    if st.session_state.users_cache is None:
        load_users_cache()
    for u in st.session_state.users_cache or []:
        if u["id"] == uid:
            return u
    return None

def user_meta_block(user):
    dept_id = user.get("department_id")
    if dept_id:
        dept_info = api_get_department(dept_id)
        dept_display = dept_info.get("name", f"ID:{dept_id}") if dept_info else f"ID:{dept_id}"
    else:
        dept_display = "-"
    
    sect_id = user.get("section_id")
    if sect_id:
        sect_info = api_get_section(sect_id)
        sect_display = sect_info.get("name", f"ID:{sect_id}") if sect_info else f"ID:{sect_id}"
    else:
        sect_display = "-"
    
    role_display = user.get('role', '').upper()
    
    st.markdown(
        f"""
        <div class="user-card">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                <div class="info-item">
                    <div class="info-label">Name</div>
                    <div class="info-value">{user.get('name', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Role</div>
                    <div class="info-value">{role_display}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Department</div>
                    <div class="info-value">{dept_display}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Section</div>
                    <div class="info-value">{sect_display}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def login_ui():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div class="login-container">
                <div style="text-align: center; margin-bottom: 30px;">
                    <div class="title">CampusMind</div>
                    <div class="small">Issue Management System</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.form("login"):
            st.markdown("### Login")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                user = api_login(email, password)
                if user:
                    st.session_state.user = user
                    load_users_cache()
                    st.rerun()
                else:
                    st.error("Invalid credentials or backend unreachable.")

def get_priority_badge(priority):
    if not priority:
        return '<span class="badge badge-low">N/A</span>'
    priority_lower = priority.lower()
    if priority_lower == "critical":
        return '<span class="badge badge-critical">Critical</span>'
    elif priority_lower == "high":
        return '<span class="badge badge-high">High</span>'
    elif priority_lower == "medium":
        return '<span class="badge badge-medium">Medium</span>'
    else:
        return '<span class="badge badge-low">Low</span>'

def get_status_badge(status):
    if not status:
        return '<span class="badge badge-open">Open</span>'
    status_lower = status.lower()
    if status_lower == "closed":
        return '<span class="badge badge-closed">Closed</span>'
    elif status_lower == "forwarded":
        return '<span class="badge badge-forwarded">Escalated</span>'
    elif status_lower == "assigned":
        return '<span class="badge badge-assigned">Assigned</span>'
    else:
        return '<span class="badge badge-open">Open</span>'

def student_dashboard(user):
    st.markdown("<div class='dashboard-title'>Student Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Manage your complaints and track their status</div>", unsafe_allow_html=True)
    user_meta_block(user)
    proctor = get_user_by_id(user.get("reports_to")) if user.get("reports_to") else None
    if proctor:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 16px; border-radius: 12px; margin: 20px 0;">
                <strong>Proctor:</strong> {proctor['name']}
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("---")

    st.markdown("<div class='section-header'>Raise a Complaint</div>", unsafe_allow_html=True)
    with st.form("raise"):
        title = st.text_input("Title", placeholder="Brief title of your complaint")
        desc = st.text_area("Description", placeholder="Describe your complaint in detail...", height=120)
        submit = st.form_submit_button("Submit Complaint", use_container_width=True)
        if submit:
            if not title or not desc:
                st.error("Title and description are required.")
            else:
                r = api_create_issue(user["id"], title, desc)
                if r and r.status_code == 201:
                    st.success("✅ Complaint submitted successfully!")
                    st.session_state.users_cache = None
                    st.rerun()
                else:
                    st.error("Failed to submit complaint.")

    st.markdown("---")
    st.markdown("<div class='section-header'>Your Complaints</div>", unsafe_allow_html=True)
    active = api_issues_for_user(user["id"], show_resolved=False)
    resolved = api_issues_for_user(user["id"], show_resolved=True)
    resolved_only = [i for i in (resolved or []) if i.get("status") == "closed"]

    # Build table safely: handle missing student_id by using current user id
    if active:
        rows = []
        for it in active:
            sid = it.get("student_id", user["id"])  # fallback to current student
            raised_by = (get_user_by_id(sid)["name"] if get_user_by_id(sid) else f"id:{sid}")
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Category": it.get("category") or "N/A",
                "Priority": it.get("priority") or "N/A",
                "Status": it.get("status") or "open",
                "Raised By": raised_by,
                "Assigned To": get_user_by_id(it.get("assigned_to"))["name"] if it.get("assigned_to") and get_user_by_id(it.get("assigned_to")) else "Unassigned",
                "Created At": it.get("created_at")
            })
        df = pd.DataFrame(rows)
        if "Created At" in df.columns:
            df["Created At"] = pd.to_datetime(df["Created At"])
            df = df.sort_values("Created At", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <h3>No Active Complaints</h3>
                <p>You don't have any active complaints at the moment.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.expander("📊 Show Resolved Complaints", expanded=False):
        if resolved_only:
            rows = []
            for it in resolved_only:
                sid = it.get("student_id", user["id"])
                raised_by = (get_user_by_id(sid)["name"] if get_user_by_id(sid) else f"id:{sid}")
                vid = it.get("verified_by")
                verified_by = (get_user_by_id(vid)["name"] if vid and get_user_by_id(vid) else (f"id:{vid}" if vid else "-"))
                rows.append({
                    "ID": it.get("id"),
                    "Title": it.get("title"),
                    "Category": it.get("category") or "N/A",
                    "Priority": it.get("priority") or "N/A",
                    "Status": it.get("status") or "closed",
                    "Raised By": raised_by,
                    "Verified By": verified_by,
                    "Verified At": it.get("verified_at")
                })
            df2 = pd.DataFrame(rows)
            if "Verified At" in df2.columns:
                df2["Verified At"] = pd.to_datetime(df2["Verified At"])
                df2 = df2.sort_values("Verified At", ascending=False)
            st.dataframe(df2, use_container_width=True, hide_index=True)
        else:
            st.info("No resolved complaints.")

def proctor_dashboard(user):
    st.markdown("<div class='dashboard-title'>Proctor Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Manage student complaints and escalate when needed</div>", unsafe_allow_html=True)
    user_meta_block(user)
    students = [u for u in (st.session_state.users_cache or api_get_users()) if u.get("reports_to")==user["id"] and u.get("role")=="student"]
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 16px; border-radius: 12px; margin: 20px 0;">
            <strong>Students under you:</strong> <span style="font-size: 20px; font-weight: 700; color: #667eea;">{len(students)}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    issues = api_issues_for_user(user["id"], show_resolved=False)
    
    active_issues = [i for i in (issues or []) if i.get("status") != "closed" and i.get("forwarded_by") != user["id"]]
    escalated_issues = [i for i in (issues or []) if i.get("forwarded_by") == user["id"]]
    
    st.markdown("<div class='section-header'>Active Complaints</div>", unsafe_allow_html=True)
    if active_issues:
        rows=[]
        for it in active_issues:
            sid = it.get("student_id")
            raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Category": it.get("category") or "N/A",
                "Priority": it.get("priority") or "N/A",
                "Status": it.get("status") or "open",
                "Raised By": raised_by,
                "Assigned To": get_user_by_id(it.get("assigned_to"))["name"] if it.get("assigned_to") and get_user_by_id(it.get("assigned_to")) else "Unassigned",
                "Created At": it.get("created_at")
            })
        df = pd.DataFrame(rows)
        if "Created At" in df.columns:
            df["Created At"] = pd.to_datetime(df["Created At"])
            df = df.sort_values("Created At", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        active_ids = [it.get("id") for it in active_issues if it.get("id")]
        if active_ids:
            st.markdown("### Actions")
            sel = st.selectbox("Select Issue ID", options=active_ids, key="proctor_sel")
            c1,c2,c3 = st.columns(3)
            if c1.button("✅ Resolve", key="proctor_resolve", use_container_width=True):
                r = api_verify(sel, user["id"], True)
                if r and r.status_code==200:
                    st.success("✅ Resolved successfully!"); st.rerun()
                else: st.error("Failed to resolve.")
            if c2.button("⬆️ Escalate", key="proctor_escalate", use_container_width=True):
                r = api_forward(sel, user["id"])
                if r and r.status_code==200:
                    st.success("⬆️ Escalated successfully!"); st.rerun()
                else: st.error("Failed to escalate.")
            if c3.button("🔄 Re-classify", key="proctor_reclassify", use_container_width=True):
                r = api_reclassify(sel)
                if r and r.status_code==200:
                    st.success("🔄 Re-classified successfully!"); st.rerun()
                else: st.error("Failed.")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <h3>No Active Complaints</h3>
                <p>All complaints have been resolved or escalated.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.markdown("<div class='section-header'>Escalated Complaints</div>", unsafe_allow_html=True)
    if escalated_issues:
        rows=[]
        for it in escalated_issues:
            sid = it.get("student_id")
            raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Category": it.get("category") or "N/A",
                "Priority": it.get("priority") or "N/A",
                "Status": it.get("status") or "forwarded",
                "Raised By": raised_by,
                "Forwarded To": get_user_by_id(it.get("assigned_to"))["name"] if it.get("assigned_to") and get_user_by_id(it.get("assigned_to")) else "Unassigned",
                "Created At": it.get("created_at")
            })
        df_esc = pd.DataFrame(rows)
        if "Created At" in df_esc.columns:
            df_esc["Created At"] = pd.to_datetime(df_esc["Created At"])
            df_esc = df_esc.sort_values("Created At", ascending=False)
        st.dataframe(df_esc, use_container_width=True, hide_index=True)
    else:
        st.info("No escalated complaints.")
    
    with st.expander("📊 Show Resolved Complaints", expanded=False):
        all_with_resolved = api_issues_for_user(user["id"], show_resolved=True)
        resolved_items = [i for i in (all_with_resolved or []) if i.get("status")=="closed"]
        if resolved_items:
            rows=[]
            for it in resolved_items:
                sid = it.get("student_id")
                raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
                vid = it.get("verified_by")
                verified_by = (get_user_by_id(vid)["name"] if vid and get_user_by_id(vid) else (f"id:{vid}" if vid else "-"))
                rows.append({
                    "ID": it.get("id"),
                    "Title": it.get("title"),
                    "Category": it.get("category") or "N/A",
                    "Priority": it.get("priority") or "N/A",
                    "Verified By": verified_by,
                    "Verified At": it.get("verified_at"),
                    "Raised By": raised_by
                })
            df2=pd.DataFrame(rows)
            if "Verified At" in df2.columns:
                df2["Verified At"]=pd.to_datetime(df2["Verified At"])
                df2 = df2.sort_values("Verified At", ascending=False)
            st.dataframe(df2, use_container_width=True, hide_index=True)
        else:
            st.info("No resolved complaints.")

def hod_dashboard(user):
    st.markdown("<div class='dashboard-title'>HOD Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Oversee department-wide complaints and manage escalations</div>", unsafe_allow_html=True)
    user_meta_block(user)
    st.markdown("---")
    issues = api_issues_for_user(user["id"], show_resolved=False)
    
    active_issues = [i for i in (issues or []) if i.get("status") != "closed" and i.get("forwarded_by") != user["id"]]
    escalated_issues = [i for i in (issues or []) if i.get("forwarded_by") == user["id"]]
    
    st.markdown("<div class='section-header'>Active Complaints</div>", unsafe_allow_html=True)
    if active_issues:
        rows=[]
        for it in active_issues:
            sid = it.get("student_id")
            raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Category": it.get("category") or "N/A",
                "Priority": it.get("priority") or "N/A",
                "Status": it.get("status") or "open",
                "Raised By": raised_by,
                "Assigned To": get_user_by_id(it.get("assigned_to"))["name"] if it.get("assigned_to") and get_user_by_id(it.get("assigned_to")) else "Unassigned",
                "Created At": it.get("created_at")
            })
        df=pd.DataFrame(rows)
        if "Created At" in df.columns:
            df["Created At"]=pd.to_datetime(df["Created At"])
            df = df.sort_values("Created At", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        active_ids = [it.get("id") for it in active_issues if it.get("id")]
        if active_ids:
            st.markdown("### Actions")
            sel = st.selectbox("Select Issue ID", options=active_ids, key="hod_sel")
            c1,c2,c3 = st.columns(3)
            if c1.button("✅ Resolve", key="hod_resolve", use_container_width=True):
                r = api_verify(sel, user["id"], True)
                if r and r.status_code==200:
                    st.success("✅ Resolved successfully!"); st.rerun()
                else: st.error("Failed to resolve.")
            if c2.button("⬆️ Escalate", key="hod_escalate", use_container_width=True):
                r = api_forward(sel, user["id"])
                if r and r.status_code==200:
                    st.success("⬆️ Escalated successfully!"); st.rerun()
                else: st.error("Failed to escalate.")
            if c3.button("🔄 Re-classify", key="hod_reclassify", use_container_width=True):
                r = api_reclassify(sel)
                if r and r.status_code==200:
                    st.success("🔄 Re-classified successfully!"); st.rerun()
                else: st.error("Failed.")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <h3>No Active Complaints</h3>
                <p>All complaints have been resolved or escalated.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.markdown("<div class='section-header'>Escalated Complaints</div>", unsafe_allow_html=True)
    if escalated_issues:
        rows=[]
        for it in escalated_issues:
            sid = it.get("student_id")
            raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Category": it.get("category") or "N/A",
                "Priority": it.get("priority") or "N/A",
                "Status": it.get("status") or "forwarded",
                "Raised By": raised_by,
                "Forwarded To": get_user_by_id(it.get("assigned_to"))["name"] if it.get("assigned_to") and get_user_by_id(it.get("assigned_to")) else "Unassigned",
                "Created At": it.get("created_at")
            })
        df_esc=pd.DataFrame(rows)
        if "Created At" in df_esc.columns:
            df_esc["Created At"]=pd.to_datetime(df_esc["Created At"])
            df_esc = df_esc.sort_values("Created At", ascending=False)
        st.dataframe(df_esc, use_container_width=True, hide_index=True)
    else:
        st.info("No escalated complaints.")
    
    with st.expander("📊 Show Resolved Complaints", expanded=False):
        all_with_resolved = api_issues_for_user(user["id"], show_resolved=True)
        resolved_items = [i for i in (all_with_resolved or []) if i.get("status")=="closed"]
        if resolved_items:
            rows=[]
            for it in resolved_items:
                sid = it.get("student_id")
                raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
                vid = it.get("verified_by")
                verified_by = (get_user_by_id(vid)["name"] if vid and get_user_by_id(vid) else (f"id:{vid}" if vid else "-"))
                rows.append({
                    "ID": it.get("id"),
                    "Title": it.get("title"),
                    "Raised By": raised_by,
                    "Verified By": verified_by,
                    "Verified At": it.get("verified_at")
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No resolved items.")

def vc_dashboard(user):
    st.markdown("<div class='dashboard-title'>VC Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Review and resolve escalated complaints</div>", unsafe_allow_html=True)
    user_meta_block(user)
    st.markdown("---")
    issues = api_issues_for_user(user["id"], show_resolved=False)
    if issues:
        rows=[]
        for it in issues:
            sid = it.get("student_id")
            raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Category": it.get("category") or "N/A",
                "Priority": it.get("priority") or "N/A",
                "Raised By": raised_by,
                "Created At": it.get("created_at")
            })
        df=pd.DataFrame(rows)
        if "Created At" in df.columns:
            df["Created At"]=pd.to_datetime(df["Created At"])
            df = df.sort_values("Created At", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        issue_ids = [it.get("id") for it in issues if it.get("id")]
        if issue_ids:
            sel = st.selectbox("Select Issue ID", options=issue_ids, key="vc_sel")
            if st.button("✅ Resolve (Close)", key="vc_resolve", use_container_width=True):
                r = api_verify(sel, user["id"], True)
                if r and r.status_code==200:
                    st.success("✅ Resolved successfully!"); st.rerun()
                else:
                    st.error("Failed.")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <h3>No Escalated Complaints</h3>
                <p>No complaints have been escalated to your level.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with st.expander("📊 Show Resolved Complaints", expanded=False):
        all_with_resolved = api_issues_for_user(user["id"], show_resolved=True)
        resolved_items = [i for i in (all_with_resolved or []) if i.get("status")=="closed"]
        if resolved_items:
            rows = []
            for it in resolved_items:
                sid = it.get("student_id")
                raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
                vid = it.get("verified_by")
                verified_by = (get_user_by_id(vid)["name"] if vid and get_user_by_id(vid) else (f"id:{vid}" if vid else "-"))
                rows.append({
                    "ID": it.get("id"),
                    "Title": it.get("title"),
                    "Raised By": raised_by,
                    "Verified By": verified_by,
                    "Verified At": it.get("verified_at")
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No resolved items.")

def admin_dashboard(user):
    st.markdown("<div class='dashboard-title'>Admin Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>System-wide analytics and issue management</div>", unsafe_allow_html=True)
    stats = api_admin_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Issues", stats.get("total",0))
    with col2:
        st.metric("Active Issues", stats.get("active",0))
    with col3:
        st.metric("Resolved Issues", stats.get("resolved",0))
    
    st.markdown("---")
    st.markdown("<div class='section-header'>All Issues</div>", unsafe_allow_html=True)
    issues = api_admin_all_issues()
    if issues:
        rows=[]
        for it in issues:
            sid = it.get("student_id")
            raised_by = (get_user_by_id(sid)["name"] if sid and get_user_by_id(sid) else (f"id:{sid}" if sid else "Unknown"))
            rows.append({
                "ID": it.get("id"),
                "Title": it.get("title"),
                "Status": it.get("status") or "open",
                "Raised By": raised_by,
                "Created At": it.get("created_at")
            })
        df=pd.DataFrame(rows)
        if "Created At" in df.columns:
            df["Created At"]=pd.to_datetime(df["Created At"])
            df = df.sort_values("Created At", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h3>No Issues</h3>
                <p>No issues found in the system.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

if st.session_state.user is None:
    login_ui()
else:
    user = st.session_state.user
    if st.session_state.users_cache is None:
        load_users_cache()
    st.sidebar.markdown(f"**{user['name']}**  \n{user['role']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    role = user.get("role","").lower()
    if role=="student":
        student_dashboard(user)
    elif role=="proctor":
        proctor_dashboard(user)
    elif role=="hod":
        hod_dashboard(user)
    elif role=="vc":
        vc_dashboard(user)
    elif role=="admin":
        admin_dashboard(user)
    else:
        st.error("Unknown role. Use seeded accounts.")