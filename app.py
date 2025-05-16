import streamlit as st
import pandas as pd

# --- Helper function for task automation classification ---
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

# --- Streamlit UI ---
st.title("Role Automation Recomposer + Tool-Driven Reconfiguration")

uploaded_tasks = st.file_uploader("Upload task_statements.csv", type="csv")
uploaded_tools = st.file_uploader("Upload tools_used.csv", type="csv")

if uploaded_tasks:
    tasks_df = pd.read_csv(uploaded_tasks)
    soc_code = st.text_input("Enter SOC Code (e.g. 53-7062.00)")

    if soc_code:
        # Filter for selected SOC code
        role_tasks = tasks_df[tasks_df['O*NET-SOC Code'] == soc_code]

        if role_tasks.empty:
            st.warning("No tasks found for this SOC code.")
        else:
            # Automation classification
            role_tasks['Classification'], role_tasks['Suggested Tech'] = zip(*role_tasks['Task Title'].map(classify_task))
            auto_percent = (role_tasks['Classification'] == 'Automatable').mean() * 100

            st.subheader(f"Tasks Automatable: {auto_percent:.1f}%")
            st.dataframe(role_tasks[['Task Title', 'Classification', 'Suggested Tech']])

            retained = role_tasks[role_tasks['Classification'] == 'Human']

            st.subheader("Retained Human Tasks")
            st.write(retained['Task Title'].tolist())

            # TOOL EXTENSION
            if uploaded_tools:
                tools_df = pd.read_csv(uploaded_tools)
                available_tools = tools_df['Commodity Title'].dropna().unique().tolist()
                selected_tools = st.multiselect("Select tools to incorporate into this role", sorted(available_tools))

                if selected_tools:
                    # Find all SOC codes linked to the selected tools
                    matching_rows = tools_df[tools_df['Commodity Title'].isin(selected_tools)]
                    tool_socs = matching_rows['O*NET-SOC Code'].unique()

                    # Pull new tasks from task_df for any of those SOCs
                    new_tasks = tasks_df[tasks_df['O*NET-SOC Code'].isin(tool_socs)]

                    # Remove duplicates and already-retained tasks
                    new_task_texts = set(new_tasks['Task Title']) - set(retained['Task Title'])
                    new_tasks_filtered = new_tasks[new_tasks['Task Title'].isin(new_task_texts)]

                    st.subheader("Tool-Enabled Tasks")
                    st.write(new_tasks_filtered['Task Title'].drop_duplicates().tolist())

                    st.subheader("Updated Role Summary")
                    total_tasks = list(retained['Task Title']) + list(new_tasks_filtered['Task Title'].drop_duplicates())
                    st.write(total_tasks)
