import streamlit as st
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta
import random

# --- Page Configuration ---
st.set_page_config(
    page_title="StudyPal",
    page_icon="🦉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialisation ---
def initialize_state():
    """Initializes all the necessary variables in the session state."""
    if 'tasks' not in st.session_state:
        st.session_state.tasks = pd.DataFrame(columns=["Subject", "Task", "Deadline", "Completed"])
    if 'subjects' not in st.session_state:
        st.session_state.subjects = ["General", "Math", "History", "Science"]
    if 'study_log' not in st.session_state:
        st.session_state.study_log = pd.DataFrame(columns=["Subject", "Duration (Minutes)", "Date"])
    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False
    if 'timer_end_time' not in st.session_state:
        st.session_state.timer_end_time = None
    if 'timer_subject' not in st.session_state:
        st.session_state.timer_subject = "General"
    if 'pet_xp' not in st.session_state:
        st.session_state.pet_xp = 0

# --- Data & Constants ---
MOTIVATIONAL_QUOTES = [
    "The secret of getting ahead is getting started. - Mark Twain",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "The expert in anything was once a beginner.",
    "Success is the sum of small efforts, repeated day in and day out.",
    "It does not matter how slowly you go as long as you do not stop. - Confucius",
    "Believe you can and you're halfway there. - Theodore Roosevelt"
]

PET_STAGES = {
    0: ("🥚", "Egg"),
    25: ("🐣", "Hatchling"),
    50: ("🐥", "Chick"),
    100: ("🦉", "Fledgling Owl"),
    200: ("🎓🦉", "Scholar Owl")
}

def get_pet_status():
    """Determines the current stage and appearance of the Focus Pet based on XP."""
    current_xp = st.session_state.pet_xp
    current_stage_xp = 0
    pet_emoji = "🥚"
    pet_name = "Egg"
    for xp, (emoji, name) in PET_STAGES.items():
        if current_xp >= xp:
            current_stage_xp = xp
            pet_emoji = emoji
            pet_name = name
    
    next_stage_xp = float('inf')
    for xp in PET_STAGES.keys():
        if xp > current_stage_xp:
            next_stage_xp = xp
            break

    progress = 0
    if next_stage_xp != float('inf'):
        progress = (current_xp - current_stage_xp) / (next_stage_xp - current_stage_xp)

    return pet_emoji, pet_name, progress, next_stage_xp


# --- UI Pages ---

def page_dashboard():
    """Displays the main dashboard with an overview."""
    st.title(f"🦉 Welcome to StudyPal!")
    st.markdown("Your personal academic sidekick to help you stay organized and motivated.")
    st.markdown("---")
    
    col1, col2 = st.columns((2, 1))

    with col1:
        st.header("🗓️ Upcoming Deadlines")
        tasks_df = st.session_state.tasks
        if not tasks_df.empty:
            upcoming_tasks = tasks_df[tasks_df['Completed'] == False].sort_values("Deadline").head(5)
            if not upcoming_tasks.empty:
                for index, row in upcoming_tasks.iterrows():
                    days_left = (row['Deadline'].date() - datetime.now().date()).days
                    if days_left < 0:
                        st.error(f"**{row['Task']}** ({row['Subject']}) was due {abs(days_left)} days ago.", icon="🚨")
                    elif days_left == 0:
                        st.warning(f"**{row['Task']}** ({row['Subject']}) is due **today**!", icon="🔥")
                    else:
                        st.info(f"**{row['Task']}** ({row['Subject']}) is due in {days_left} days.", icon="⏳")
            else:
                st.success("You've completed all your tasks! 🎉")
        else:
            st.info("No tasks added yet. Go to 'Manage Tasks & Subjects' to add some.")

    with col2:
        st.header("✨ Your Focus Pet")
        pet_emoji, pet_name, progress, next_stage_xp = get_pet_status()

        st.markdown(f"<p style='text-align: center; font-size: 80px;'>{pet_emoji}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>{pet_name}</p>", unsafe_allow_html=True)
        
        st.progress(progress)
        if next_stage_xp != float('inf'):
            st.markdown(f"**{st.session_state.pet_xp} / {next_stage_xp} XP** to the next stage.")
        else:
            st.markdown("**Max Level Reached!** You're a true scholar!")

    st.markdown("---")
    st.subheader("💡 Motivational Quote of the Day")
    st.info(f"_{random.choice(MOTIVATIONAL_QUOTES)}_")


def page_manage_tasks():
    """Page for users to add, view, and manage subjects and tasks."""
    st.title("📚 Manage Tasks & Subjects")

    # --- Subject Management ---
    with st.expander("Manage Your Subjects", expanded=False):
        st.subheader("Current Subjects")
        
        # Display subjects with delete buttons
        cols = st.columns(4)
        for i, subject in enumerate(st.session_state.subjects):
            with cols[i % 4]:
                if subject != "General": # Prevent deletion of 'General'
                    if st.button(f"❌ {subject}", key=f"del_{subject}"):
                        st.session_state.subjects.remove(subject)
                        # Also remove tasks associated with the subject
                        st.session_state.tasks = st.session_state.tasks[st.session_state.tasks['Subject'] != subject]
                        st.rerun()
                else:
                    st.markdown(f"**{subject}** (default)")

        st.subheader("Add a New Subject")
        new_subject = st.text_input("Enter subject name:", key="new_subject_input")
        if st.button("Add Subject"):
            if new_subject and new_subject not in st.session_state.subjects:
                st.session_state.subjects.append(new_subject)
                st.success(f"Added subject: {new_subject}")
                st.rerun()
            elif new_subject in st.session_state.subjects:
                st.warning("This subject already exists.")
            else:
                st.warning("Please enter a subject name.")

    # --- Task Management ---
    st.header("📋 Your Task List")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task Description")
    with col2:
        task_subject = st.selectbox("Subject", options=st.session_state.subjects)
    with col3:
        task_deadline = st.date_input("Deadline", min_value=datetime.now())

    if st.button("Add Task", use_container_width=True):
        if task_name:
            new_task = pd.DataFrame([{
                "Subject": task_subject,
                "Task": task_name,
                "Deadline": pd.to_datetime(task_deadline),
                "Completed": False
            }])
            st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
            st.success("Task added successfully!")
        else:
            st.error("Please enter a task description.")

    # Display tasks
    tasks_df = st.session_state.tasks
    if not tasks_df.empty:
        tasks_df = tasks_df.sort_values(by="Deadline")
        st.markdown("---")
        for index, row in tasks_df.iterrows():
            cols = st.columns((1, 4, 2, 2, 1))
            completed = cols[0].checkbox("", value=row["Completed"], key=f"check_{index}")
            
            if completed:
                st.session_state.tasks.loc[index, "Completed"] = True
                cols[1].markdown(f"~~_{row['Task']}_~~")
            else:
                st.session_state.tasks.loc[index, "Completed"] = False
                cols[1].markdown(f"**{row['Task']}**")

            cols[2].write(f"_{row['Subject']}_")
            cols[3].write(row["Deadline"].strftime("%Y-%m-%d"))
            if cols[4].button("Delete", key=f"delete_{index}"):
                st.session_state.tasks = st.session_state.tasks.drop(index)
                st.rerun()
    else:
        st.info("No tasks yet. Add one above!")


def page_focus_timer():
    """Page with the Pomodoro-style study timer."""
    st.title("⏱️ Start a Focus Session")
    
    if st.session_state.timer_active:
        # Timer is running
        end_time = st.session_state.timer_end_time
        time_left = end_time - datetime.now()

        if time_left.total_seconds() > 0:
            st.header(f"Studying: {st.session_state.timer_subject}")
            minutes, seconds = divmod(int(time_left.total_seconds()), 60)
            
            timer_placeholder = st.empty()
            timer_placeholder.metric("Time Remaining", f"{minutes:02d}:{seconds:02d}")
            
            st.progress(time_left.total_seconds() / (25 * 60))

            if st.button("Cancel Session"):
                st.session_state.timer_active = False
                st.warning("Session cancelled. No XP awarded.")
                st.rerun()
            
            time.sleep(1)
            st.rerun()

        else:
            # Timer finished
            st.session_state.timer_active = False
            st.balloons()
            st.success("Focus session complete! Great job!")
            
            # Log study time and award XP
            duration_minutes = 25
            new_log = pd.DataFrame([{
                "Subject": st.session_state.timer_subject,
                "Duration (Minutes)": duration_minutes,
                "Date": datetime.now().date()
            }])
            st.session_state.study_log = pd.concat([st.session_state.study_log, new_log], ignore_index=True)
            st.session_state.pet_xp += duration_minutes
            
            st.info(f"You earned **{duration_minutes} XP** for your Focus Pet! 🦉")

            if st.button("Start Another Session"):
                st.rerun()

    else:
        # Setup for a new timer
        st.subheader("Ready to focus? A session lasts for 25 minutes.")
        subject_to_study = st.selectbox("Which subject are you studying?", options=st.session_state.subjects)
        
        if st.button("Start 25-Minute Timer", type="primary", use_container_width=True):
            st.session_state.timer_active = True
            st.session_state.timer_end_time = datetime.now() + timedelta(minutes=25)
            st.session_state.timer_subject = subject_to_study
            st.rerun()

def page_progress():
    """Page to visualize study habits and progress."""
    st.title("📊 My Progress")
    
    log_df = st.session_state.study_log
    if log_df.empty:
        st.info("No study sessions logged yet. Complete a focus session to see your progress here.")
        return

    # --- Key Metrics ---
    total_time = log_df['Duration (Minutes)'].sum()
    total_sessions = len(log_df)
    avg_duration = log_df['Duration (Minutes)'].mean() if total_sessions > 0 else 0

    st.header("Overall Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Study Time", f"{int(total_time)} min")
    col2.metric("Total Focus Sessions", f"{total_sessions}")
    col3.metric("Average Session", f"{avg_duration:.1f} min")
    st.markdown("---")

    # --- Visualizations ---
    st.header("Time Spent per Subject")
    time_per_subject = log_df.groupby('Subject')['Duration (Minutes)'].sum().reset_index()
    
    chart = alt.Chart(time_per_subject).mark_bar().encode(
        x=alt.X('Subject:N', sort='-y', title='Subject'),
        y=alt.Y('Duration (Minutes):Q', title='Total Minutes Studied'),
        color=alt.Color('Subject:N', legend=None),
        tooltip=['Subject', 'Duration (Minutes)']
    ).properties(
        title='Your Study Time Distribution'
    )
    st.altair_chart(chart, use_container_width=True)

    st.header("Study History")
    st.dataframe(log_df.sort_values(by="Date", ascending=False), use_container_width=True)


# --- Main App Logic ---
initialize_state()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Manage Tasks & Subjects", "Focus Timer", "My Progress"])

if page == "Dashboard":
    page_dashboard()
elif page == "Manage Tasks & Subjects":
    page_manage_tasks()
elif page == "Focus Timer":
    page_focus_timer()
elif page == "My Progress":
    page_progress()

