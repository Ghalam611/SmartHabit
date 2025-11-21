import streamlit as st
from smart_habit import SmartHabit
from datetime import datetime

# Initialize tracker
if "tracker" not in st.session_state:
    st.session_state.tracker = SmartHabit()

tracker = st.session_state.tracker

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Smart Habit Tracker", page_icon="⭐", layout="wide")
st.title("⭐ Smart Habit Tracker")
st.write("**Build better habits every day!**")

# ------------------ SIDEBAR MENU ------------------
st.sidebar.title("📋 Menu")
menu = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Dashboard", "➕ Add Habit", "✅ Mark Progress", "📋 My Habits", "📊 Analytics", "⚙️ Manage Habits"]
)

# Quick stats in sidebar
if tracker.habits:
    today = datetime.now().strftime("%Y-%m-%d")
    completed_today = sum(1 for h in tracker.habits 
                         if h["daily_progress"].get(today, 0) >= h["target_hours"])
    
    st.sidebar.markdown("---")
    st.sidebar.write("**Today's Summary**")
    st.sidebar.metric("Completed", f"{completed_today}/{len(tracker.habits)}")

# ------------------ DASHBOARD ------------------
if menu == "🏠 Dashboard":
    st.header("🏠 Your Dashboard")
    
    if not tracker.habits:
        st.info("🌟 Welcome! Start by adding your first habit.")
    else:
        # Score cards
        score = tracker.calculate_daily_score()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Daily Score", f"{score['daily_score']}%")
        with col2:
            st.metric("Completed", score['completed_habits'])
        with col3:
            st.metric("Total Habits", score['total_habits'])
        
        st.progress(score["daily_score"] / 100)
        
        # Today's habits
        st.subheader("📝 Today's Habits")
        for habit in tracker.habits:
            today = datetime.now().strftime("%Y-%m-%d")
            today_hours = habit["daily_progress"].get(today, 0)
            target = habit["target_hours"]
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{habit['name']}**")
            with col2:
                st.write(f"{today_hours}h / {target}h")
            with col3:
                if today_hours >= target:
                    st.success("✅ Done")
                else:
                    st.warning("🕒 In Progress")
            
            st.progress(min(today_hours / target, 1.0))
            st.markdown("---")

# ------------------ ADD HABIT ------------------
elif menu == "➕ Add Habit":
    st.header("➕ Add New Habit")
    
    with st.form("add_habit_form"):
        name = st.text_input("Habit Name")
        target_hours = st.number_input("Target Hours per Day", min_value=0.5, step=0.5, value=1.0)
        
        if st.form_submit_button("Add Habit"):
            if name.strip():
                habit = {
                    "number": tracker.next_number,
                    "name": name,
                    "target_hours": target_hours,
                    "today_hours": 0,
                    "completed": False,
                    "daily_progress": {},
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
                tracker.initialize_daily_tracking(habit)
                tracker.habits.append(habit)
                tracker.next_number += 1
                tracker.save_data()
                st.success(f"Habit '{name}' added! 🎉")
            else:
                st.error("Please enter a habit name")

# ------------------ MARK PROGRESS ------------------
elif menu == "✅ Mark Progress":
    st.header("✅ Mark Progress")
    
    if not tracker.habits:
        st.warning("No habits available. Add some habits first!")
    else:
        habit_names = {f"{h['name']}": h['number'] for h in tracker.habits}
        selected = st.selectbox("Select Habit", list(habit_names.keys()))
        habit_num = habit_names[selected]
        habit = tracker.find_habit_by_number(habit_num)
        
        st.write(f"**Target:** {habit['target_hours']} hours")
        
        today = datetime.now().strftime("%Y-%m-%d")
        current_hours = habit["daily_progress"].get(today, 0)
        
        hours = st.slider(
            "Hours completed today", 
            min_value=0.0, 
            max_value=float(habit["target_hours"] * 2), 
            value=float(current_hours),
            step=0.5
        )
        
        if st.button("Save Progress"):
            habit["today_hours"] = hours
            habit["daily_progress"][today] = hours
            habit["completed"] = hours >= habit["target_hours"]
            tracker.save_data()
            st.success("Progress updated! ✅")

# ------------------ MY HABITS ------------------
elif menu == "📋 My Habits":
    st.header("📋 My Habits")
    
    if not tracker.habits:
        st.info("No habits added yet.")
    else:
        for habit in tracker.habits:
            today = datetime.now().strftime("%Y-%m-%d")
            today_hours = habit["daily_progress"].get(today, 0)
            
            st.subheader(f"{habit['name']}")
            st.write(f"**Target:** {habit['target_hours']} hours/day")
            st.write(f"**Today:** {today_hours} hours")
            st.write(f"**Created:** {habit['created_date']}")
            
            if today_hours >= habit["target_hours"]:
                st.success("Completed today! 🎉")
            else:
                st.info(f"Need {habit['target_hours'] - today_hours} more hours")
            
            st.markdown("---")

# ------------------ ANALYTICS ------------------
elif menu == "📊 Analytics":
    st.header("📊 Analytics")
    
    if not tracker.habits:
        st.warning("No data available yet.")
    else:
        # Daily score
        score = tracker.calculate_daily_score()
        st.metric("Overall Score", f"{score['daily_score']}%")
        
        # Weekly progress
        st.subheader("Weekly Progress")
        habit_names = {f"{h['name']}": h['number'] for h in tracker.habits}
        selected = st.selectbox("Select Habit", list(habit_names.keys()))
        habit_num = habit_names[selected]
        
        weekly = tracker.get_weekly_progress(habit_num)
        habit = tracker.find_habit_by_number(habit_num)
        
        for day in weekly:
            status = "✅" if day["completed"] else "❌"
            st.write(f"{day['date']} - {status} {day['hours']}h / {day['target']}h")

# ------------------ MANAGE HABITS ------------------
elif menu == "⚙️ Manage Habits":
    st.header("⚙️ Manage Habits")
    
    if not tracker.habits:
        st.warning("No habits to manage.")
    else:
        habit_names = {f"{h['name']}": h['number'] for h in tracker.habits}
        selected = st.selectbox("Select Habit to Delete", list(habit_names.keys()))
        habit_num = habit_names[selected]
        habit = tracker.find_habit_by_number(habit_num)
        
        st.warning(f"You're about to delete: {habit['name']}")
        
        if st.button("Delete Habit"):
            tracker.habits.remove(habit)
            tracker.save_data()
            st.success(f"Deleted '{habit['name']}'")
            st.rerun()

# Footer
st.markdown("---")
st.write("💪 **Keep building great habits!**")