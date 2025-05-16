import streamlit as st
import pandas as pd

def classify_task(text):
    text = text.lower()
    if any(word in text for word in ['enter', 'record', 'update']):
        return 'Automatable', 'RPA'
    elif any(word in text for word in ['lift', 'move', 'carry', 'transport']):
        return 'Automatable', 'AGV / Robotic Arm'
    elif any(word in text for word in ['inspect', 'sort']):
        return 'Automatable', 'Computer Vision'
    else:
        return 'Human', 'Human-required'

# Load file
st.title("Role Automation Recomposer")
uploaded_file = st.file_uploader("Upload task_statements.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    soc_code = st.text_input("Enter SOC Code (e.g. 53-7062.00)")

    if soc_code:
        filtered = df[df['O*NET-SOC Code'] == soc_code]
        if filtered.empty:
            st.warning("No tasks found for this SOC code.")
        else:
            filtered['Classification'], filtered['Suggested Tech'] = zip(*filtered['Task Title'].map(classify_task))
            auto_percent = (filtered['Classification'] == 'Automatable').mean() * 100

            st.subheader(f"Tasks Automatable: {auto_percent:.1f}%")

            st.subheader("Automation Plan")
            st.dataframe(filtered[['Task Title', 'Classification', 'Suggested Tech']])

            st.subheader("Retained Human Tasks")
            retained = filtered[filtered['Classification'] == 'Human']
            st.write(retained['Task Title'].tolist())
