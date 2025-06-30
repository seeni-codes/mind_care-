import streamlit as st
from datetime import datetime, date
from mental_health_bot import ask_mental_health_bot, generate_wellness_tips
from database import (
    register_user, get_user_by_email, verify_password, 
    save_user_profile, get_user_profile, get_db_connection
)
import sqlite3

st.set_page_config(page_title="MindCare AI", page_icon="🧠", layout="wide")

# --- Initialize database tables for mental health features
def create_mental_health_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create journal entries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT,
        content TEXT NOT NULL,
        mood_rating INTEGER,
        is_private BOOLEAN DEFAULT 1,
        entry_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Create mood tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mood_scale INTEGER NOT NULL,
        energy_level INTEGER NOT NULL,
        anxiety_level INTEGER NOT NULL,
        sleep_quality INTEGER NOT NULL,
        notes TEXT,
        entry_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    conn.close()

# Database functions for mental health features
def save_journal_entry(user_id: int, entry_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO journal_entries (user_id, title, content, mood_rating, is_private, entry_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        entry_data.get("title"),
        entry_data.get("content"),
        entry_data.get("mood_rating"),
        entry_data.get("is_private", True),
        entry_data.get("entry_date")
    ))
    conn.commit()
    conn.close()

def get_user_journals(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM journal_entries 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    """, (user_id,))
    journals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return journals

def save_mood_entry(user_id: int, mood_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO mood_entries (user_id, mood_scale, energy_level, anxiety_level, sleep_quality, notes, entry_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        mood_data.get("mood_scale"),
        mood_data.get("energy_level"),
        mood_data.get("anxiety_level"),
        mood_data.get("sleep_quality"),
        mood_data.get("notes"),
        mood_data.get("entry_date")
    ))
    conn.commit()
    conn.close()

def get_user_moods(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM mood_entries 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    """, (user_id,))
    moods = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return moods

def update_user_profile(user_id: int, profile: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if profile exists
    cursor.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
        UPDATE user_profiles SET 
        age = ?, gender = ?, activity_level = ?, medical_conditions = ?, 
        food_preferences = ?, allergies = ?, health_goal = ?
        WHERE user_id = ?
        """, (
            profile.get("age"),
            profile.get("gender"),
            profile.get("activity_level", profile.get("occupation")),  # Reuse field
            profile.get("medical_conditions", profile.get("mental_health_concerns")),
            profile.get("food_preferences", profile.get("support_preferences")),
            profile.get("allergies", profile.get("stress_level")),  # Reuse field
            profile.get("health_goal", "Mental Wellness"),
            user_id
        ))
    else:
        cursor.execute("""
        INSERT INTO user_profiles (user_id, age, gender, activity_level, medical_conditions, food_preferences, allergies, health_goal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            profile.get("age"),
            profile.get("gender"),
            profile.get("activity_level", profile.get("occupation")),
            profile.get("medical_conditions", profile.get("mental_health_concerns")),
            profile.get("food_preferences", profile.get("support_preferences")),
            profile.get("allergies", profile.get("stress_level")),
            profile.get("health_goal", "Mental Wellness")
        ))
    
    conn.commit()
    conn.close()

# Initialize mental health database tables
create_mental_health_tables()

# --- Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# --- Header UI
st.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;'>
    <h1 style='color: white; margin: 0;'>🧠 MindCare AI Assistant</h1>
    <p style='color: white; margin: 0.5rem 0 0 0; opacity: 0.9;'>Your personal mental wellness companion</p>
</div>
""", unsafe_allow_html=True)

def login_tab():
    st.markdown("### 🔐 Login to Your Safe Space")
    with st.form("login_form"):
        login_email = st.text_input("Email", key="login_email", placeholder="Enter your email")
        login_pass = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
        login_submit = st.form_submit_button("Login", use_container_width=True)
        if login_submit:
            user = get_user_by_email(login_email)
            if user and verify_password(user['password_hash'], login_pass):
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = user['email']
                st.session_state['user_name'] = user['name']
                st.session_state['user_id'] = user['id']
                st.success(f"Welcome back, {user['name']}! 🌟")
                st.rerun()
            else:
                st.error("Invalid email or password")

def register_tab():
    st.markdown("### 📝 Create Your Account")
    st.info("Join our supportive community and start your mental wellness journey today.")
    
    with st.form("register_form"):
        name = st.text_input("Full Name", key="reg_name", placeholder="Enter your full name")
        email = st.text_input("Email", key="reg_email", placeholder="Enter your email")
        phone = st.text_input("Phone (Optional)", key="reg_phone", placeholder="Enter your phone number")
        password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password", placeholder="Confirm your password")
        register_submit = st.form_submit_button("Create Account", use_container_width=True)
        
        if register_submit:
            if password != confirm_password:
                st.error("❌ Passwords do not match")
            elif not name or not email or not password:
                st.error("❌ Name, email, and password are required")
            else:
                success = register_user(name, email, phone or "", password)
                if success:
                    st.success("✅ Registration successful! Please login to continue.")
                else:
                    st.error("⚠️ User with this email already exists.")

def logout_button():
    if st.button("Logout 🚪", key="logout_button", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = None
        st.session_state['user_name'] = None
        st.session_state['user_id'] = None
        st.success("You have been logged out safely. Take care! 💙")
        st.rerun()

def profile_tab():
    st.markdown(f"### 👋 Welcome, {st.session_state['user_name']}!")
    st.markdown(f"**Email:** {st.session_state['user_email']}")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        logout_button()
    
    with st.expander("👤 Personal Profile Setup", expanded=False):
        with st.form("user_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=13, max_value=100, value=25, step=1)
                gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Non-binary", "Other"])
                occupation = st.text_input("Occupation/Student Status", placeholder="e.g., College Student, Working Professional")
                
            with col2:
                stress_level = st.selectbox("Current Stress Level", ["Low", "Moderate", "High", "Very High"])
                mental_health_concerns = st.text_area("Mental Health Concerns (Optional)", 
                                                    placeholder="e.g., anxiety, depression, stress, etc.", height=80)
                support_preferences = st.text_area("Preferred Support Style", 
                                                 placeholder="e.g., gentle guidance, practical advice, listening ear", height=80)
                
            submitted = st.form_submit_button("Save Profile 💾", use_container_width=True)
            if submitted:
                profile = {
                    "age": age,
                    "gender": gender,
                    "occupation": occupation,
                    "stress_level": stress_level,
                    "mental_health_concerns": mental_health_concerns,
                    "support_preferences": support_preferences
                }
                update_user_profile(st.session_state['user_id'], profile)
                st.success("Profile saved successfully! 🌟")

def chatbot_tab():
    st.markdown("### 💬 Chat with MindCare AI")
    st.markdown("Share your thoughts, feelings, or concerns. I'm here to listen and support you.")
    
    # Chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, (role, message, timestamp) in enumerate(st.session_state['chat_history']):
            if role == "user":
                st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; margin-left: 20%;'>
                    <p style='margin: 0; color: #1565c0;'><strong>You:</strong> {message}</p>
                    <small style='color: #666;'>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #f3e5f5; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; margin-right: 20%;'>
                    <p style='margin: 0; color: #7b1fa2;'><strong>MindCare AI:</strong> {message}</p>
                    <small style='color: #666;'>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Input for new message
    user_input = st.text_area("💭 Share what's on your mind...", height=100, 
                              placeholder="Feel free to express your thoughts, emotions, or ask for support...")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send Message 📤", use_container_width=True):
            if user_input.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Add user message to history
                st.session_state['chat_history'].append(("user", user_input, timestamp))
                
                with st.spinner("MindCare AI is thinking..."):
                    reply = ask_mental_health_bot(user_input)
                    st.session_state['chat_history'].append(("bot", reply, timestamp))
                
                st.rerun()
            else:
                st.warning("Please enter a message to continue our conversation.")
    
    with col2:
        if st.button("Clear Chat 🗑️", use_container_width=True):
            st.session_state['chat_history'] = []
            st.rerun()

def journal_tab():
    st.markdown("### 📔 Personal Journal")
    st.markdown("Write your thoughts, reflect on your day, or document your journey.")
    
    # New journal entry
    with st.expander("✍️ Write New Entry", expanded=True):
        with st.form("journal_form"):
            entry_title = st.text_input("Entry Title (Optional)", placeholder="Give your entry a title...")
            entry_content = st.text_area("Your Thoughts", height=200, 
                                       placeholder="Write about your day, feelings, experiences, or anything on your mind...")
            mood_rating = st.slider("How are you feeling today?", 1, 10, 5, 
                                  help="1 = Very Low, 10 = Excellent")
            is_private = st.checkbox("Keep this entry private", value=True)
            
            submitted = st.form_submit_button("Save Entry 💾", use_container_width=True)
            if submitted and entry_content.strip():
                entry_data = {
                    "title": entry_title or f"Journal Entry - {date.today()}",
                    "content": entry_content,
                    "mood_rating": mood_rating,
                    "is_private": is_private,
                    "entry_date": date.today().isoformat()
                }
                save_journal_entry(st.session_state['user_id'], entry_data)
                st.success("📝 Journal entry saved successfully!")
                st.rerun()
            elif submitted:
                st.warning("Please write something before saving your entry.")
    
    # Display previous entries
    st.markdown("### 📚 Your Previous Entries")
    entries = get_user_journals(st.session_state['user_id'])
    
    if entries:
        for entry in entries[-5:]:  # Show last 5 entries
            with st.expander(f"📖 {entry['title']} - {entry['entry_date']}"):
                st.write(entry['content'])
                st.markdown(f"**Mood Rating:** {entry['mood_rating']}/10")
                if entry['is_private']:
                    st.caption("🔒 Private Entry")
    else:
        st.info("No journal entries yet. Start writing to document your thoughts and feelings!")

def mood_tracker_tab():
    st.markdown("### 📊 Mood Tracker")
    st.markdown("Track your emotional well-being over time to identify patterns and progress.")
    
    # Quick mood entry
    with st.expander("📝 Log Today's Mood", expanded=True):
        with st.form("mood_form"):
            col1, col2 = st.columns(2)
            with col1:
                mood_scale = st.slider("Overall Mood", 1, 10, 5, 
                                     help="1 = Very Low/Depressed, 5 = Neutral, 10 = Excellent/Euphoric")
                energy_level = st.slider("Energy Level", 1, 10, 5)
                
            with col2:
                anxiety_level = st.slider("Anxiety Level", 1, 10, 5, 
                                        help="1 = Very Calm, 10 = Very Anxious")
                sleep_quality = st.slider("Sleep Quality (last night)", 1, 10, 5)
            
            mood_notes = st.text_area("Notes (Optional)", height=100,
                                    placeholder="What influenced your mood today? Any specific events or thoughts?")
            
            submitted = st.form_submit_button("Save Mood Entry 💾", use_container_width=True)
            if submitted:
                mood_data = {
                    "mood_scale": mood_scale,
                    "energy_level": energy_level,
                    "anxiety_level": anxiety_level,
                    "sleep_quality": sleep_quality,
                    "notes": mood_notes,
                    "entry_date": date.today().isoformat()
                }
                save_mood_entry(st.session_state['user_id'], mood_data)
                st.success("📈 Mood entry logged successfully!")
                st.rerun()
    
    # Display mood history
    st.markdown("### 📈 Your Mood Trends")
    moods = get_user_moods(st.session_state['user_id'])
    
    if moods and len(moods) > 0:
        # Simple mood visualization
        recent_moods = moods[-7:]  # Last 7 entries
        dates = [entry['entry_date'] for entry in recent_moods]
        mood_values = [entry['mood_scale'] for entry in recent_moods]
        
        if len(dates) > 1:
            st.line_chart(dict(zip(dates, mood_values)))
        
        # Recent entries
        st.markdown("### Recent Mood Entries")
        for mood in recent_moods[-3:]:
            with st.expander(f"📅 {mood['entry_date']} - Mood: {mood['mood_scale']}/10"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mood:** {mood['mood_scale']}/10")
                    st.write(f"**Energy:** {mood['energy_level']}/10")
                with col2:
                    st.write(f"**Anxiety:** {mood['anxiety_level']}/10")
                    st.write(f"**Sleep Quality:** {mood['sleep_quality']}/10")
                if mood['notes']:
                    st.write(f"**Notes:** {mood['notes']}")
    else:
        st.info("No mood entries yet. Start tracking to see your emotional patterns over time!")

# --- Main App Logic ---
if not st.session_state['logged_in']:
    tabs = st.tabs(["🏠 Welcome", "🔐 Login", "📝 Sign Up"])
    
    with tabs[0]:
        st.markdown("""
        ## Welcome to MindCare AI 🌟
        
        Your personal mental wellness companion designed to support your emotional well-being journey.
        
        ### 🌈 What We Offer:
        - **💬 AI Chatbot**: Get emotional support and guidance anytime
        - **📔 Personal Journal**: Reflect and document your thoughts privately  
        - **📊 Mood Tracking**: Monitor your emotional patterns over time
        - **🔒 Privacy First**: Your data is secure and confidential
        
        ### 🚀 Getting Started:
        1. **Sign Up** for a free account
        2. **Set up your profile** for personalized support
        3. **Start chatting** with our AI companion
        4. **Track your moods** and write in your journal
        
        *Remember: This is a supportive tool, not a replacement for professional mental health care.*
        """)
        
        st.info("💡 **Tip:** Create an account to unlock all features and start your wellness journey!")
    
    with tabs[1]:
        login_tab()
    
    with tabs[2]:
        register_tab()

else:
    # Logged in user interface
    tabs = st.tabs(["👤 Profile", "💬 Chat", "📔 Journal", "📊 Mood Tracker"])
    
    with tabs[0]:
        profile_tab()
    
    with tabs[1]:
        chatbot_tab()
    
    with tabs[2]:
        journal_tab()
    
    with tabs[3]:
        mood_tracker_tab()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🌟 MindCare AI - Supporting your mental wellness journey</p>
    <p><small>If you're experiencing a mental health emergency, please contact your local emergency services or crisis helpline.</small></p>
</div>
""", unsafe_allow_html=True)