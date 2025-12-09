import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# Set a global style for matplotlib plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('viridis') # You can choose other palettes like 'pastel', 'deep', 'muted', 'colorblind', 'rocket', etc.

# 3. Define a function to load the CSV files
@st.cache_data
def load_data():
    try:
        df_cohort_metrics = pd.read_csv('cohort_metrics.csv')
        df_high_risk_cohort = pd.read_csv('high_risk_cohort.csv')

        # Load pre-calculated summary files for other_cohorts
        other_home_ownership_dist = pd.read_csv('other_cohorts_home_ownership_dist.csv')
        other_emp_length_dist = pd.read_csv('other_cohorts_emp_length_dist.csv')
        other_addr_state_dist_top5 = pd.read_csv('other_cohorts_addr_state_dist_top5.csv')
        other_purpose_dist_top5 = pd.read_csv('other_cohorts_purpose_dist_top5.csv')
        other_annual_inc_desc = pd.read_csv('other_cohorts_annual_inc_desc.csv')
        other_int_rate_desc = pd.read_csv('other_cohorts_int_rate_desc.csv')

        # Ensure 'issue_date' is datetime for proper sorting and plotting
        df_cohort_metrics['issue_date'] = pd.to_datetime(df_cohort_metrics['issue_date'], format='%m-%Y')
        df_cohort_metrics = df_cohort_metrics.sort_values(by='issue_date').reset_index(drop=True)

        return df_cohort_metrics, df_high_risk_cohort, \
               other_home_ownership_dist, other_emp_length_dist, \
               other_addr_state_dist_top5, other_purpose_dist_top5, \
               other_annual_inc_desc, other_int_rate_desc
               
    except FileNotFoundError:
        st.error("One or more CSV files not found. Please ensure all required CSVs are in the same directory.")
        # Return None for all expected dataframes if any file is missing
        return None, None, None, None, None, None, None, None

# 4. In the main part of the Streamlit app:

st.title('RevoFin Loan Portfolio Analysis')
st.write("Exploring loan portfolio trends and comparing a high-risk cohort (04-2014) with other cohorts.")

df_cohort_metrics, df_high_risk_cohort, \
other_home_ownership_dist, other_emp_length_dist, \
other_addr_state_dist_top5, other_purpose_dist_top5, \
other_annual_inc_desc, other_int_rate_desc = load_data()

if df_cohort_metrics is not None:
    st.header('1. Portfolio Performance Trends Over Time')
    st.markdown("Use the slider below to filter the date range for the trend plots.")

    # Interactive date range slider
    min_date = df_cohort_metrics['issue_date'].min().to_pydatetime()
    max_date = df_cohort_metrics['issue_date'].max().to_pydatetime()
    date_range = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MM-YYYY"
    )

    filtered_df_cohort_metrics = df_cohort_metrics[
        (df_cohort_metrics['issue_date'] >= date_range[0]) &
        (df_cohort_metrics['issue_date'] <= date_range[1])
    ]

    # c. Display a section for 'TKB30 Trend Over Time'
    st.subheader('TKB30 Trend Over Time')
    fig_tkb30, ax_tkb30 = plt.subplots(figsize=(15, 7))
    sns.lineplot(x='issue_date', y='TKB30', data=filtered_df_cohort_metrics, ax=ax_tkb30)
    ax_tkb30.set_title('TKB30 Trend Over Time', fontsize=16)
    ax_tkb30.set_xlabel('Issue Date', fontsize=12)
    ax_tkb30.set_ylabel('TKB30', fontsize=12)
    ax_tkb30.set_xticklabels(ax_tkb30.get_xticklabels(), rotation=45, ha='right')
    ax_tkb30.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig_tkb30)

    # d. Display a section for 'Outstanding Amount (OS) Trend Over Time'
    st.subheader('Outstanding Amount (OS) Trend Over Time')
    fig_os, ax_os = plt.subplots(figsize=(15, 7))
    sns.lineplot(x='issue_date', y='Outstanding Amount (OS)', data=filtered_df_cohort_metrics, ax=ax_os)
    ax_os.set_title('Outstanding Amount (OS) Trend Over Time', fontsize=16)
    ax_os.set_xlabel('Issue Date', fontsize=12)
    ax_os.set_ylabel('Outstanding Amount (OS)', fontsize=12)
    ax_os.set_xticklabels(ax_os.get_xticklabels(), rotation=45, ha='right')
    ax_os.grid(True, linestyle='--', alpha=0.7)
    plt.ticklabel_format(style='plain', axis='y') # Prevent scientific notation on y-axis
    plt.tight_layout()
    st.pyplot(fig_os)

    # e. Create an interactive comparison section
    st.header('2. High-Risk Cohort (04-2014) vs. Other Cohorts Comparison')
    st.write("Here's a detailed comparison of loan and customer attributes between the high-risk cohort (04-2014) and all other cohorts.")

    if df_high_risk_cohort is not None and other_home_ownership_dist is not None:
        # f. For categorical comparisons (using bar charts)
        categorical_cols_data = {
            'home_ownership': {'HighRisk': df_high_risk_cohort['home_ownership'].value_counts(normalize=True).reset_index(name='proportion'),
                               'Other': other_home_ownership_dist},
            'emp_length': {'HighRisk': df_high_risk_cohort['emp_length'].value_counts(normalize=True).reset_index(name='proportion'),
                           'Other': other_emp_length_dist},
            'addr_state': {'HighRisk': df_high_risk_cohort['addr_state'].value_counts(normalize=True).head(5).reset_index(name='proportion'),
                           'Other': other_addr_state_dist_top5},
            'purpose': {'HighRisk': df_high_risk_cohort['purpose'].value_counts(normalize=True).head(5).reset_index(name='proportion'),
                        'Other': other_purpose_dist_top5}
        }

        for col_name, data_dict in categorical_cols_data.items():
            st.subheader(f'Distribution of {col_name.replace("_", " ").title()}')
            col1, col2 = st.columns(2)
            with col1:
                st.write(f'**High-Risk Cohort (04-2014) - {col_name.replace("_", " ").title()}**')
                fig, ax = plt.subplots(figsize=(6, 4))
                sns.barplot(x=data_dict['HighRisk'].columns[0], y='proportion', data=data_dict['HighRisk'], ax=ax)
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            with col2:
                st.write(f'**Other Cohorts - {col_name.replace("_", " ").title()}**')
                fig, ax = plt.subplots(figsize=(6, 4))
                sns.barplot(x=data_dict['Other'].columns[0], y='proportion', data=data_dict['Other'], ax=ax)
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)

        # g. For numerical comparisons (displaying descriptive statistics tables)
        st.subheader("Numerical Comparisons (Descriptive Statistics)")
        st.info("Box plots for numerical comparisons are not displayed as raw 'other_cohorts.csv' is not loaded. Displaying descriptive statistics in table format instead.")
        numerical_cols_desc_data = {
            'annual_inc': {'HighRisk': df_high_risk_cohort['annual_inc'].describe().reset_index(),
                           'Other': other_annual_inc_desc},
            'int_rate': {'HighRisk': df_high_risk_cohort['int_rate'].describe().reset_index(),
                         'Other': other_int_rate_desc}
        }
        for col_name, data_dict in numerical_cols_desc_data.items():
            st.subheader(f'Descriptive Statistics of {col_name.replace("_", " ").title()}')
            col1, col2 = st.columns(2)
            with col1:
                st.write(f'**High-Risk Cohort (04-2014) - {col_name.replace("_", " ").title()}**')
                st.dataframe(data_dict['HighRisk'])
            with col2:
                st.write(f'**Other Cohorts - {col_name.replace("_", " ").title()}**')
                st.dataframe(data_dict['Other'])

    # h. Add a final section to summarize the findings
    st.header('3. Summary of Anomaly Cohort (04-2014) Characteristics')
    st.markdown("""
    Based on the detailed comparisons, the '04-2014' cohort, identified as a high-risk cohort due to its lowest TKB30,
    exhibits several distinguishing characteristics compared to 'df_other_cohorts' (all other cohorts).\n
    #### Key Differences:\n
    1.  **Home Ownership:** The high-risk cohort has a higher proportion of borrowers with `MORTGAGE` (60.12% vs. 48.93%) and a lower proportion with `RENT` (33.04% vs. 39.14%). This suggests a potential difference in financial stability indicators.\n
    2.  **Employment Length (`emp_length`):** The high-risk cohort shows a slightly higher percentage of borrowers with `10+ years` of employment (35.42% vs. 32.54%), but a lower representation of very short employment lengths (`< 1 year` is 6.25% vs 9.72%). Experience alone does not mitigate risk in this cohort.\n
    3.  **Annual Income (`annual_inc`):** The mean annual income in the high-risk cohort is lower ($74,094.31) than in other cohorts ($81,094.02), with a less diverse income range (lower standard deviation).\n
    4.  **Interest Rate (`int_rate`):** The high-risk cohort has a notably higher mean interest rate (0.1611) compared to other cohorts (0.1293), suggesting these loans were perceived as higher risk during underwriting.\n
    5.  **Address State (`addr_state`):** While top states are consistent, there are minor percentage shifts. For instance, Illinois (IL) is notably higher in the high-risk cohort (6.25% vs 4.11%) indicating potential regional risk concentrations.\n
    6.  **Purpose (`purpose`):** There's a higher concentration in `debt_consolidation` (60.42% vs. 55.14%) and `credit_card` (26.49% vs. 24.57%) in the high-risk cohort, reinforcing these as key drivers of higher risk.\n
    #### Overall Characterization:\n
    The '04-2014' high-risk cohort tends to consist of borrowers with slightly lower average annual incomes, higher interest rates, and a more pronounced focus on debt consolidation and credit card refinancing purposes. These factors, combined with specific home ownership and employment length distributions, suggest that these borrowers might have had higher initial risk profiles or were subject to less stringent lending criteria, leading to the observed lower TKB30.\n    """)
