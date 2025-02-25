import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Read in data
df = pd.read_csv('data/1825.csv')

# Streamlit App
st.title("BSKK Budget Visualization App")

# Sidebar with filters and 'Unselect All' button
st.sidebar.header('Filter by categories')

# Step 1: Filter by Produktgruppe first
produktgruppe_options = df['Produktgruppe'].unique()
selected_produktgruppe = st.sidebar.multiselect("Select Produktgruppe", produktgruppe_options, default=[])

# Filter based on Produktgruppe
if selected_produktgruppe:
    df_filtered = df[df['Produktgruppe'].isin(selected_produktgruppe)]
else:
    df_filtered = df.copy()

# Step 2: Dynamically update Subprodukt options based on Produktgruppe
subprodukt_options = df_filtered['Subprodukt'].unique()
selected_subprodukt = st.sidebar.multiselect("Select Subprodukt", subprodukt_options, default=[])

if selected_subprodukt:
    df_filtered = df_filtered[df_filtered['Subprodukt'].isin(selected_subprodukt)]

# Step 3: Dynamically update Hauptkategorie options based on Subprodukt
hauptkategorie_options = df_filtered['Hauptkategorie'].unique()
selected_hauptkategorie = st.sidebar.multiselect("Select Hauptkategorie", hauptkategorie_options, default=[])

if selected_hauptkategorie:
    df_filtered = df_filtered[df_filtered['Hauptkategorie'].isin(selected_hauptkategorie)]

# Step 4: Dynamically update Subkategorie_1 options based on Hauptkategorie
subkategorie_1_options = df_filtered['Subkategorie_1'].unique()
selected_subkategorie_1 = st.sidebar.multiselect("Select Subkategorie_1", subkategorie_1_options, default=[])

if selected_subkategorie_1:
    df_filtered = df_filtered[df_filtered['Subkategorie_1'].isin(selected_subkategorie_1)]

# Step 5: Dynamically update Subkategorie_2 options based on Subkategorie_1
subkategorie_2_options = df_filtered['Subkategorie_2'].unique()
selected_subkategorie_2 = st.sidebar.multiselect("Select Subkategorie_2", subkategorie_2_options, default=[])

if selected_subkategorie_2:
    df_filtered = df_filtered[df_filtered['Subkategorie_2'].isin(selected_subkategorie_2)]

# "Unselect All" Button
if st.sidebar.button("Unselect All"):
    selected_produktgruppe = []
    selected_subprodukt = []
    selected_hauptkategorie = []
    selected_subkategorie_1 = []
    selected_subkategorie_2 = []
    st.experimental_rerun()

# Plot the data if any selection is made
if not any([selected_produktgruppe, selected_subprodukt, selected_hauptkategorie, selected_subkategorie_1, selected_subkategorie_2]) == False:
    # Melt the DataFrame for plotting
    value_vars = ['Ist 2018', 'Soll 2019', 'Soll 2020', 'Ist 2021', 'Ist 2022', 'Ist 2023', 'Soll 2024', 'Soll 2025', 'Plan 2026', 'Plan 2027', 'Plan 2028']
    melted_df = pd.melt(df_filtered, id_vars=['Hauptkategorie', 'Subkategorie_1', 'Subkategorie_2', 'Produktgruppe', 'Subprodukt'], 
                        value_vars=value_vars, var_name='Year', value_name='Value')

    # Custom hover label concatenation logic
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

    # Plotting using Plotly Express
    fig = px.line(melted_df, x='Year', y='Value', color='Hover_Label', hover_name='Hover_Label',
                    line_group='Hover_Label', labels={'Year': 'Year', 'Value': 'Value'})

    # Update layout for a wider plot and move the legend to the right
    fig.update_layout(
        width=1200,  # Explicitly set width
        height=600,
        title='Interactive Plot',
        legend_title_text='Hover Label',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02  # Move the legend to the right
        )
    )

    # Add hover effects
    fig.update_traces(mode="lines+markers", hovertemplate="%{hovertext}<extra></extra>")


    # Display plot with full width of page
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a DataFrame for the percentage change plot
    percentage_change_df = df_filtered[['Ist 2018', 'Ist 2023', 'Percentagechange Ist 2018 vs. Ist 2023']]
    percentage_change_df.index = melted_df['Hover_Label'].unique()
    percentage_change_df['Percentagechange Ist 2018 vs. Ist 2023'] = percentage_change_df['Percentagechange Ist 2018 vs. Ist 2023'].astype(int)
    #percentage_change_df['Ist 2018'] = percentage_change_df['Ist 2018'].astype(int)
    #percentage_change_df['Ist 2023'] = percentage_change_df['Ist 2023'].astype(int)
    
    st.table(percentage_change_df)
    
else:
    st.write("Please select at least one filter to display the plot.")