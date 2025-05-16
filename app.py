import streamlit as st
import pandas as pd

# Load O*NET datasets
st.title("Role Recomposer: Tool-Driven Trait Mapping")

tasks_file = st.file_uploader("Upload task_statements.csv", type="csv")
tools_file = st.file_uploader("Upload tools_used.csv", type="csv")
tasks_to_dwa_file = st.file_uploader("Upload tasks_to_dwa.csv", type="csv")
dwa_map_file = st.file_uploader("Upload work_activities_to_iwa_to_dwa.csv", type="csv")
abilities_link_file = st.file_uploader("Upload abilities_to_work_activities.csv", type="csv")
abilities_file = st.file_uploader("Upload abilities.csv", type="csv")

if all([tasks_file, tools_file, tasks_to_dwa_file, dwa_map_file, abilities_link_file, abilities_file]):
    tasks_df = pd.read_csv(tasks_file)
    tools_df = pd.read_csv(tools_file)
    tasks_to_dwa = pd.read_csv(tasks_to_dwa_file)
    dwa_map = pd.read_csv(dwa_map_file)
    ability_links = pd.read_csv(abilities_link_file)
    ability_scores = pd.read_csv(abilities_file)

    soc_input = st.text_input("Enter SOC Code to analyze (e.g. 53-7062.00)")
    selected_tool = st.selectbox("Select a tool to simulate", tools_df["Commodity Title"].dropna().unique())

    if soc_input and selected_tool:
        # SOCs that use the tool
        socs_with_tool = tools_df[tools_df["Commodity Title"] == selected_tool]["O*NET-SOC Code"].unique()

        # DWAs linked to those SOCs
        dw_tasks = tasks_df[tasks_df["O*NET-SOC Code"].isin(socs_with_tool)]
        dw_dwas = tasks_to_dwa[tasks_to_dwa["Task ID"].isin(dw_tasks["Task ID"])][["DWA ID", "DWA Title"]].drop_duplicates()

        # Work activities linked to DWAs
        dw_was = dwa_map[dwa_map["DWA Element ID"].isin(dw_dwas["DWA ID"])][["Work Activities Element Name"]].drop_duplicates()

        # Abilities linked to work activities
        relevant_abilities = ability_links[ability_links["Work Activities Element Name"].isin(dw_was["Work Activities Element Name"])]
        ability_names = relevant_abilities["Abilities Element Name"].unique()

        # Compare to base SOC's ability scores
        soc_abilities = ability_scores[ability_scores["O*NET-SOC Code"] == soc_input]
        soc_ability_subset = soc_abilities[soc_abilities["Abilities Element Name"].isin(ability_names)]

        # Mark new vs already present
        soc_ability_subset["Already Required"] = "Yes"
        unmatched = set(ability_names) - set(soc_ability_subset["Abilities Element Name"])
        additional_abilities = pd.DataFrame({"Abilities Element Name": list(unmatched), "Already Required": "No"})

        all_abilities = pd.concat([soc_ability_subset[["Abilities Element Name", "Scale Name", "Data Value", "Already Required"]],
                                   additional_abilities], ignore_index=True)

        st.subheader(f"Abilities Impacted by Adding: {selected_tool}")
        st.dataframe(all_abilities.sort_values(by="Already Required", ascending=False).reset_index(drop=True))
