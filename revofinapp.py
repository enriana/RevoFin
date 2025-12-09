# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# 3. Define a function to load the CSV files
@st.cache_data
def load_data():
    try:
        df_cohort_metrics = pd.read_csv('cohort_metrics.csv')
        df_high_risk_cohort = pd.read_csv('high_risk_cohort.csv')
        df_other_cohorts = pd.read_csv('other_cohorts.csv')
        
        # Ensure 'issue_date' is datetime for proper sorting and plotting
        df_cohort_metrics['issue_date'] = pd.to_datetime(df_cohort_metrics['issue_date'], format='%m-%Y')
        df_cohort_metrics = df_cohort_metrics.sort_values(by='issue_date').reset_index(drop=True)
        
        return df_cohort_metrics, df_high_risk_cohort, df_other_cohorts
    except FileNotFoundError:
        st.error("One or more CSV files not found. Please ensure 'cohort_metrics.csv', 'high_risk_cohort.csv', and 'other_cohorts.csv' are in the same directory.")
        return None, None, None

# 4. In the main part of the Streamlit app:

st.title('RevoFin Loan Portfolio Analysis')
st.write("Exploring loan portfolio trends and comparing a high-risk cohort (04-2014) with other cohorts.")

df_cohort_metrics, df_high_risk_cohort, df_other_cohorts = load_data()

if df_cohort_metrics is not None:
    # c. Display a section for 'TKB30 Trend Over Time'
    st.header('TKB30 Trend Over Time')
    fig_tkb30, ax_tkb30 = plt.subplots(figsize=(15, 7))
    sns.lineplot(x='issue_date', y='TKB30', data=df_cohort_metrics, ax=ax_tkb30)
    ax_tkb30.set_title('TKB30 Trend Over Time')
    ax_tkb30.set_xlabel('Issue Date')
    ax_tkb30.set_ylabel('TKB30')
    ax_tkb30.tick_params(axis='x', rotation=45, ha='right')
    ax_tkb30.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig_tkb30)

    # d. Display a section for 'Outstanding Amount (OS) Trend Over Time'
    st.header('Outstanding Amount (OS) Trend Over Time')
    fig_os, ax_os = plt.subplots(figsize=(15, 7))
    sns.lineplot(x='issue_date', y='Outstanding Amount (OS)', data=df_cohort_metrics, ax=ax_os)
    ax_os.set_title('Outstanding Amount (OS) Trend Over Time')
    ax_os.set_xlabel('Issue Date')
    ax_os.set_ylabel('Outstanding Amount (OS)')
    ax_os.tick_params(axis='x', rotation=45, ha='right')
    ax_os.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig_os)

    # e. Create an interactive comparison section
    st.header('High-Risk Cohort (04-2014) vs. Other Cohorts Comparison')
    st.write("Here's a detailed comparison of loan and customer attributes between the high-risk cohort (04-2014) and all other cohorts.")

    if df_high_risk_cohort is not None and df_other_cohorts is not None:
        # f. For categorical comparisons
        categorical_cols = ['home_ownership', 'emp_length', 'addr_state', 'purpose']
        for col in categorical_cols:
            st.subheader(f'Distribution of {col.replace("_", " ").title()}')
            col1, col2 = st.columns(2)
            with col1:
                st.write(f'**High-Risk Cohort (04-2014) - {col.replace("_", " ").title()}**')
                if col in ['addr_state', 'purpose']:
                    st.dataframe(df_high_risk_cohort[col].value_counts(normalize=True).head(5))
                else:
                    st.dataframe(df_high_risk_cohort[col].value_counts(normalize=True))
            with col2:
                st.write(f'**Other Cohorts - {col.replace("_", " ").title()}**')
                if col in ['addr_state', 'purpose']:
                    st.dataframe(df_other_cohorts[col].value_counts(normalize=True).head(5))
                else:
                    st.dataframe(df_other_cohorts[col].value_counts(normalize=True))

        # g. For numerical comparisons
        numerical_cols = ['annual_inc', 'int_rate']
        for col in numerical_cols:
            st.subheader(f'Descriptive Statistics of {col.replace("_", " ").title()}')
            col1, col2 = st.columns(2)
            with col1:
                st.write(f'**High-Risk Cohort (04-2014) - {col.replace("_", " ").title()}**')
                st.dataframe(df_high_risk_cohort[col].describe())
            with col2:
                st.write(f'**Other Cohorts - {col.replace("_", " ").title()}**')
                st.dataframe(df_other_cohorts[col].describe())

    # h. Add a final section to summarize the findings
    st.header('Summary of Anomaly Cohort (04-2014) Characteristics')
    st.markdown("""
    Based on the detailed comparisons, the '04-2014' cohort, identified as a high-risk cohort due to its lowest TKB30,
    exhibits several distinguishing characteristics compared to 'df_other_cohorts' (all other cohorts).

    #### Key Differences:

    1.  **Home Ownership:** The high-risk cohort has a higher proportion of borrowers with `MORTGAGE` (60.12% vs. 48.93%) and a lower proportion with `RENT` (33.04% vs. 39.14%). This suggests a potential difference in financial stability indicators.

    2.  **Employment Length (`emp_length`):** The high-risk cohort shows a slightly higher percentage of borrowers with `10+ years` of employment (35.42% vs. 32.54%), but a lower representation of very short employment lengths (`< 1 year` is 6.25% vs 9.72%). Experience alone does not mitigate risk in this cohort.

    3.  **Annual Income (`annual_inc`):** The mean annual income in the high-risk cohort is lower (\$74,094.31) than in other cohorts (\$81,094.02), with a less diverse income range (lower standard deviation).

    4.  **Interest Rate (`int_rate`):** The high-risk cohort has a notably higher mean interest rate (0.1611) compared to other cohorts (0.1293), suggesting these loans were perceived as higher risk during underwriting.

    5.  **Address State (`addr_state`):** While top states are consistent, there are minor percentage shifts. For instance, Illinois (IL) is notably higher in the high-risk cohort (6.25% vs 4.11%) indicating potential regional risk concentrations.

    6.  **Purpose (`purpose`):** There's a higher concentration in `debt_consolidation` (60.42% vs. 55.14%) and `credit_card` (26.49% vs. 24.57%) in the high-risk cohort, reinforcing these as key drivers of higher risk.

    #### Overall Characterization:

    The '04-2014' high-risk cohort tends to consist of borrowers with slightly lower average annual incomes, higher interest rates, and a more pronounced focus on debt consolidation and credit card refinancing purposes. These factors, combined with specific home ownership and employment length distributions, suggest that these borrowers might have had higher initial risk profiles or were subject to less stringent lending criteria, leading to the observed lower TKB30.
    """)
    