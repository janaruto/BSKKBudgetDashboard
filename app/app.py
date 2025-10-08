import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# --- Load data ---
df = pd.read_csv('data/1826.csv')

# --- Create unique ID for divisor selection ---
df['Divisor_ID'] = df['Hauptkategorie'].astype(str) + " | " + df['Subkategorie_2'].astype(str)

# --- Streamlit App ---
st.title("BSKK Budget Visualization App")

# --- Sidebar Filters ---
st.sidebar.header('Filter by categories')

# Helper to drop NaN and sort unique values
def unique_nonan(series):
    return sorted(series.dropna().unique())

# Step 1: Filter by Produktgruppe
produktgruppe_options = unique_nonan(df['Produktgruppe'])
selected_produktgruppe = st.sidebar.multiselect("Select Produktgruppe", produktgruppe_options, default=[])

if selected_produktgruppe:
    df_filtered = df[df['Produktgruppe'].isin(selected_produktgruppe)]
else:
    df_filtered = df.copy()

# Step 2: Subprodukt
subprodukt_options = unique_nonan(df_filtered['Subprodukt'])
selected_subprodukt = st.sidebar.multiselect("Select Subprodukt", subprodukt_options, default=[])

if selected_subprodukt:
    df_filtered = df_filtered[df_filtered['Subprodukt'].isin(selected_subprodukt)]

# Step 3: Hauptkategorie
hauptkategorie_options = unique_nonan(df_filtered['Hauptkategorie'])
selected_hauptkategorie = st.sidebar.multiselect("Select Hauptkategorie", hauptkategorie_options, default=[])

if selected_hauptkategorie:
    df_filtered = df_filtered[df_filtered['Hauptkategorie'].isin(selected_hauptkategorie)]

# Step 4: Subkategorie_1
subkategorie_1_options = unique_nonan(df_filtered['Subkategorie_1'])
selected_subkategorie_1 = st.sidebar.multiselect("Select Subkategorie_1", subkategorie_1_options, default=[])

if selected_subkategorie_1:
    df_filtered = df_filtered[df_filtered['Subkategorie_1'].isin(selected_subkategorie_1)]

# Step 5: Subkategorie_2
subkategorie_2_options = unique_nonan(df_filtered['Subkategorie_2'])
selected_subkategorie_2 = st.sidebar.multiselect("Select Subkategorie_2", subkategorie_2_options, default=[])

if selected_subkategorie_2:
    df_filtered = df_filtered[df_filtered['Subkategorie_2'].isin(selected_subkategorie_2)]

# --- Unselect All Button ---
if st.sidebar.button("Unselect All"):
    selected_produktgruppe = []
    selected_subprodukt = []
    selected_hauptkategorie = []
    selected_subkategorie_1 = []
    selected_subkategorie_2 = []
    st.experimental_rerun()

# --- Division Settings ---
st.sidebar.header("Division Settings")

divisor_options = unique_nonan(df['Divisor_ID'])
default_divisor = "Leistungsmengen | Anzahl Schüler:innen im Kindergarten und Primarschule"
selected_divisor = st.sidebar.selectbox(
    "Select divisor row",
    divisor_options,
    index=list(divisor_options).index(default_divisor) if default_divisor in divisor_options else 0
)

divide_clicked = st.sidebar.button("Divide")

# --- Manage session state for division ---
if "divided" not in st.session_state:
    st.session_state.divided = False
    st.session_state.current_filters = None

# Rebuild a unique filter signature
current_filters_signature = str(selected_produktgruppe) + str(selected_subprodukt) + \
    str(selected_hauptkategorie) + str(selected_subkategorie_1) + str(selected_subkategorie_2)

# Reset division if filters changed
if st.session_state.current_filters != current_filters_signature:
    st.session_state.divided = False
    st.session_state.current_filters = current_filters_signature

# --- Plotting Section ---
if not any([selected_produktgruppe, selected_subprodukt, selected_hauptkategorie, selected_subkategorie_1, selected_subkategorie_2]) == False:
    # Prepare data for plotting
    value_vars = ['Ist 2018', 'Soll 2019', 'Soll 2020', 'Ist 2021', 'Ist 2022', 'Ist 2023',
                  'Ist 2024', 'Soll 2025', 'Plan 2026', 'Plan 2027', 'Plan 2028']

    melted_df = pd.melt(
        df_filtered,
        id_vars=['Hauptkategorie', 'Subkategorie_1', 'Subkategorie_2', 'Produktgruppe', 'Subprodukt'],
        value_vars=value_vars,
        var_name='Year',
        value_name='Value'
    )

    # Custom hover label
    def create_hover_label(row):
        if row['Subkategorie_1'] == row['Subkategorie_2']:
            return f"{row['Hauptkategorie']}, {row['Subkategorie_1']}, {row['Produktgruppe']}, {row['Subprodukt']}"
        elif row['Hauptkategorie'] == row['Subkategorie_1']:
            return f"{row['Subkategorie_1']}, {row['Subkategorie_2']}, {row['Produktgruppe']}, {row['Subprodukt']}"
        elif row['Produktgruppe'] == row['Subprodukt']:
            return f"{row['Hauptkategorie']}, {row['Subkategorie_1']}, {row['Subkategorie_2']}, {row['Produktgruppe']}"
        else:
            return f"{row['Hauptkategorie']}, {row['Subkategorie_1']}, {row['Subkategorie_2']}, {row['Produktgruppe']}, {row['Subprodukt']}"

    melted_df['Hover_Label'] = melted_df.apply(create_hover_label, axis=1)

    # --- Apply Division if clicked ---
    if divide_clicked and not st.session_state.divided:
        divisor_row = df[df['Divisor_ID'] == selected_divisor]

        if not divisor_row.empty:
            divisor_values = divisor_row.melt(
                id_vars=['Hauptkategorie', 'Subkategorie_1', 'Subkategorie_2', 'Produktgruppe', 'Subprodukt'],
                value_vars=value_vars,
                var_name='Year',
                value_name='Divisor_Value'
            )[["Year", "Divisor_Value"]]

            # Divide chart data
            melted_df = melted_df.merge(divisor_values, on='Year', how='left')
            melted_df['Value'] = melted_df['Value'] / melted_df['Divisor_Value']

            # Divide table data
            for col in ['Ist 2018', 'Ist 2024']:
                df_filtered[col] = df_filtered[col] / float(divisor_values.loc[divisor_values['Year'] == col, 'Divisor_Value'])

            # Recalculate percentage change
            df_filtered['Percentagechange Ist 2018 vs. Ist 2024'] = (
                (df_filtered['Ist 2024'] - df_filtered['Ist 2018']) / df_filtered['Ist 2018'] * 100
            )

            st.session_state.divided = True
            st.success(f"✅ Division applied using '{selected_divisor}'")
        else:
            st.warning("⚠️ Selected divisor not found in dataset.")

    # --- Plot using Plotly Express ---
    fig = px.line(
        melted_df,
        x='Year',
        y='Value',
        color='Hover_Label',
        hover_name='Hover_Label',
        line_group='Hover_Label',
        labels={'Year': 'Year', 'Value': 'Value'}
    )

    fig.update_layout(
        width=1200,
        height=600,
        title='Interactive Plot',
        legend_title_text='Hover Label',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

    fig.update_traces(mode="lines+markers", hovertemplate="%{hovertext}<extra></extra>")

    st.plotly_chart(fig, use_container_width=True)

    # --- Updated Percentage Change Table ---
    if 'Percentagechange Ist 2018 vs. Ist 2024' in df_filtered.columns:
        percentage_change_df = df_filtered[['Ist 2018', 'Ist 2024', 'Percentagechange Ist 2018 vs. Ist 2024']].copy()
        percentage_change_df.index = melted_df['Hover_Label'].unique()
        st.subheader("Percentage Change Table (Updated)")
        st.table(percentage_change_df)

else:
    st.write("Please select at least one filter to display the plot.")