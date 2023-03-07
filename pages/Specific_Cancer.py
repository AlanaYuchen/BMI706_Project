
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

# set up page sidebar
st.set_page_config(page_title="Explore a Specific Cancer", page_icon="📈")
st.sidebar.header("Explore a Specific Cancer")

@st.cache_data
def load_data():
  clinical_df = pd.read_csv("clinical.tsv", delimiter = "\t")
  family_df = pd.read_csv("family_history.tsv", delimiter = "\t")

  # ================ clean clinical_df data ===============
  # replace '-- with empty space and collapse columns with cancer stage to one
  clinical_df = clinical_df.replace("'--","")
  clinical_df = clinical_df.fillna('')

  stage_columns = clinical_df.filter(regex=("stage.*"))
  stage_columns.drop(axis = 1, columns = ["ajcc_clinical_stage", "ann_arbor_clinical_stage"])
  agg_df = stage_columns.agg(lambda x: ''.join(x.astype(str)), axis=1)
  clinical_df['stage'] = agg_df

  # select columns of interest
  clinical_df_filtered = clinical_df[['project_id', 'case_id','primary_diagnosis', 'ethnicity', 'gender', 'race', 'vital_status',
  'stage', 'year_of_diagnosis', 'age_at_diagnosis', 'year_of_birth', 'year_of_death', 'site_of_resection_or_biopsy', 
  'tissue_or_organ_of_origin', 'tumor_grade', 'days_to_death']]

  # ================ clean family history data ================
  family_df = family_df.replace("'--","")
  family_df_filtered = family_df[['case_id', 'project_id', 
  'relationship_gender', 'relationship_primary_diagnosis', 
  'relationship_type', 'relative_with_cancer_history']]

  # ================ merge both datasets ================
  full_df = pd.merge(clinical_df_filtered, family_df_filtered, on = "case_id", how = "left")
  full_df = full_df.replace("",np.nan)
  return full_df

full_df = load_data()

# record stages in full_df 
full_df[full_df['stage'] == "Stage 1"] = "Stage I"
full_df[full_df['stage'] == "Stage 2"] = "Stage II"
full_df[full_df['stage'] == "Stage 3"] = "Stage III"
full_df[full_df['stage'] == "Stage 4"] = "Stage IV"

full_df[full_df['stage'] == "I"] = "Stage I"
full_df[full_df['stage'] == "II"] = "Stage II"
full_df[full_df['stage'] == "III"] = "Stage III"
full_df[full_df['stage'] == "IV"] = "Stage IV"

full_df[full_df['stage'] == "Unknown"] = "Not Reported"
full_df[full_df['stage'] == "Not ReportedNot Reported"] = "Not Reported"

full_df[full_df['stage'] == "Stage IIAStage IIA"] = "Stage IIA"
full_df[full_df['stage'] == "Stage IIICStage IIIC"] = "Stage IIIC"
full_df[full_df['stage'] == "Stage IIBStage IIB"] = "Stage IIB"

st.write("# Explore a Specific Cancer")

# ============================================= Visualization 6 =============================================
#subset one cancer type of user's choice
cancer = st.selectbox(label = "Cancer", options = full_df['tissue_or_organ_of_origin'].unique())
subset = full_df[full_df["tissue_or_organ_of_origin"] == cancer]
Q6 = subset[['stage', 'ethnicity', 'gender', 'age_at_diagnosis']]
Q6['age_at_diagnosis_year'] = pd.to_numeric(Q6['age_at_diagnosis'])/365
Q6['age_group'] = np.select(
    [
        Q6['age_at_diagnosis_year'].between(0, 20, inclusive=False), 
        Q6['age_at_diagnosis_year'].between(20, 40, inclusive=False),
        Q6['age_at_diagnosis_year'].between(40, 60, inclusive=False),
        Q6['age_at_diagnosis_year'].between(60, 100, inclusive=True)
    ], 
    [
        'Ages 0 - 19', 
        'Ages 20 - 39',
        'Ages 40 - 59',
        'Over 60'
    ], 
    default='Unknown'
)
Q6 = Q6.dropna()

# ========= gender =========
st.write("### Explore Cancer Stage Across Ethnicities and Gender")
# add selector 
select_stage_gender = alt.selection_single(encodings=["x"])

# bar chart 
base = alt.Chart(Q6).properties(width = 300, height = 200)
cancerstage_gender = base.mark_bar().encode(
  x = alt.X("stage:O",title='Cancer Stage'), 
  y = alt.Y(aggregate = "count",title='Count'),
  color = alt.Color('gender',title='Gender',scale = alt.Scale(domain=['female','male','unknown'], range=["pink", "lightskyblue","snow3"])), 
  tooltip = [alt.Tooltip("stage",title='Cancer stage'),alt.Tooltip("gender",title='Gender'), alt.Tooltip("count()",title='Count')],
  opacity=alt.condition(select_stage_gender, alt.value(1), alt.value(0.2))
).add_selection(
    select_stage_gender
)

diagnosisage_gender = base.mark_bar(opacity = 0.8).encode(
  x = alt.X("age_group:O", axis=alt.Axis(labelAngle=360),title='Age group'), 
  y = alt.Y(aggregate = "count",title='Count'),
  color = alt.Color('gender',title='Gender',scale = alt.Scale(domain=['female','male','unknown'], range=["pink", "lightskyblue","snow3"])), 
  tooltip = [alt.Tooltip("age_group",title='Age group'),alt.Tooltip("gender",title='Gender'), alt.Tooltip("count()",title='Count')]
).transform_filter(
    select_stage_gender
)

both_plots = cancerstage_gender | diagnosisage_gender
st.altair_chart(both_plots, use_container_width=True)

# ========= ethnicity =========
st.write("### Explore Age of Diagnosis Across Ethnicities and Gender")
# add selector 
select_stage_ethnicity = alt.selection_single(encodings=["x"])

base = alt.Chart(Q6).properties(width = 300, height = 200)
cancerstage_ethnicity = base.mark_bar().encode(
  x = alt.X("stage:O",title='Cancer stage'), 
  y = alt.Y(aggregate = "count",title='Count'),
  color = alt.Color('ethnicity',title='Ethnicity'), 
  tooltip = [alt.Tooltip("stage",title='Cancer stage'),alt.Tooltip("ethnicity",title='Ethnicity'), alt.Tooltip("count()",title='Count')],
  opacity=alt.condition(select_stage_ethnicity, alt.value(1), alt.value(0.2))
).add_selection(
    select_stage_ethnicity
)

diagnosisage_ethnicity = base.mark_bar(opacity = 0.8).encode(
  x = alt.X("age_group:O", axis=alt.Axis(labelAngle=360),title='Age group'), 
  y = alt.Y(aggregate = "count",title='Count'),
  color = alt.Color('ethnicity',title='Ethnicity'), 
  tooltip = [alt.Tooltip("age_group",title='Age group'),alt.Tooltip("ethnicity",title='Ethnicity'), alt.Tooltip("count()",title='Count')]
).transform_filter(
    select_stage_ethnicity
)

both_plots_ethnicity = cancerstage_ethnicity | diagnosisage_ethnicity
st.altair_chart(both_plots_ethnicity, use_container_width=True)