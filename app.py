import streamlit as st  # Import Streamlit for building the web app
import pandas as pd  # Import pandas for data manipulation
import plotly.express as px  # Import Plotly Express for creating plots
import plotly.graph_objects as go  # Import Plotly Graph Objects for advanced plotting
from streamlit_plotly_events import plotly_events  # Import plotly_events for handling Plotly events in Streamlit

# Set page configuration to wide layout
st.set_page_config(layout="wide")

# Load the dataset
file_path = r'data_cleaned.xlsx'  # Path to the Excel file containing the data
data = pd.read_excel(file_path)  # Read the Excel file into a pandas DataFrame

# Define column indices
division_col = 0  # Index of the 'Division' column (previously 'Class')
period_col = 1  # Index of the 'Period' column
feature_1_col = 2  # Index of the 'Feature 1' column (previously 'Age')
feature_2_col = 3  # Index of the 'Feature 2' column (previously 'Membership Period')
metrics_cols = list(range(4, data.shape[1]))  # Indices of the metrics columns

# Convert period_col to categorical if it is numeric
if pd.api.types.is_numeric_dtype(data.iloc[:, period_col]):
    data.iloc[:, period_col] = data.iloc[:, period_col].astype(str)

# Define possible metrics for user selection based on survey responses or data columns
metrics_options = data.columns[metrics_cols].tolist()

# Function to update the bar chart based on the selected division
def update_bar_chart(division_name):
    division_data = data[data.iloc[:, division_col] == division_name]
    metrics_avg = division_data.iloc[:, metrics_cols].mean().sort_values(ascending=True)
    metrics_count = division_data.iloc[:, metrics_cols].count()
    num_bars = len(metrics_avg)
    fig_height = 450  # Fixed height of the figure in pixels
    bar_height = 20  # Fixed height of each bar in pixels

    bar_fig = px.bar(
        metrics_avg,
        x=metrics_avg.values,
        y=metrics_avg.index,
        orientation='h',
        text=metrics_avg.values,
        labels={'y': '', 'x': 'Average Score'},
        hover_data={'Number of responses': metrics_count.values}  # Add number of responses as hover data
    )
    # Configure the text and positioning for annotations
    annotations = []
    for idx, value in enumerate(metrics_avg.values):
        annotations.append({
            'x': 0,  # Set x position to 0
            'y': metrics_avg.index[idx],  # Position at the respective metric
            'xref': 'x',  # Reference to the x-axis for x-coordinate
            'yref': 'y',  # Reference to the y-axis for y-coordinate
            'text': metrics_avg.index[idx],  # Metric name as text
            'font': {'color': 'black', 'size': 12},
            'xanchor': 'left',  # Align text to the left
            'xshift': 0,  # No horizontal shift
            'showarrow': False,  # Remove the arrow
            'yshift': +18,  # Vertical offset to push the text above the bar
        })

    bar_fig.update_traces(
        texttemplate='%{x:.1f}', 
        textposition='inside', 
        marker_color='#0C275C', 
        textfont_color='white', 
        textangle=0
    )  # Display values outside the bars and set bar color

    bar_fig.update_layout(
        title={'text': f"<b>{division_name}</b>", 'font': {'size': 14, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels
            showgrid=False, 
            zeroline=False,
            range=[0, 11]  # Set the range of the x-axis from 0 to 11
        ),
        yaxis=dict(
            showticklabels=False, 
            showgrid=False, 
            zeroline=False,
            fixedrange=True  # Fix the range of the y-axis
        ),
        showlegend=False,
        margin=dict(l=15, r=50, t=42, b=5),  
        bargap=(fig_height - num_bars * bar_height) / fig_height,  # Adjust the gap between bars
        annotations=annotations,  # Add annotations to the layout
        height=fig_height  # Set the height of the figure
    )

    col_bar_chart.plotly_chart(bar_fig, use_container_width=True, key=f"bar_chart_{division_name}")

# Main layout: Divide the main area into a sidebar for filters and a main content area for displaying charts
left_margin, main_content = st.columns([3, 12])

with main_content:
    # Tabs for Performance by Division and Performance by Feature 1
    tab1, tab2 = st.tabs([f"Performance by {data.columns[division_col]}", f"Performance by {data.columns[division_col]} Version 2"])

    with tab1:
        # Filters with separate expanders
        col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
        with col1:
            with st.expander("Period"):
                selected_period = st.multiselect(f"Select {data.columns[period_col]}:", data.iloc[:, period_col].unique(), default=data.iloc[:, period_col].unique(), key="division_period")

        with col2:
            with st.expander("Metrics"):
                selected_metric = st.selectbox("Select Metric:", data.columns[metrics_cols], index=len(metrics_cols) - 1, key="division_metrics")

        with col3:
            with st.expander(f"{data.columns[feature_2_col]}"):
                selected_feature_2 = st.multiselect(f"Select {data.columns[feature_2_col]}:", data.iloc[:, feature_2_col].unique(), default=data.iloc[:, feature_2_col].unique(), key="division_feature_2")

        with col4:
            with st.expander(f"{data.columns[feature_1_col]}"):
                selected_feature_1 = st.multiselect(f"Select {data.columns[feature_1_col]}:", data.iloc[:, feature_1_col].unique(), default=data.iloc[:, feature_1_col].unique(), key="division_feature_1")

        col_chart, col_bar_chart = st.columns([7, 5])
        with col_chart:
            # Ensure all filters are properly referenced here
            filtered_data = data[
                (data.iloc[:, period_col].isin(selected_period)) &
                (data.iloc[:, feature_2_col].isin(selected_feature_2)) &
                (data.iloc[:, feature_1_col].isin(selected_feature_1))
            ]

            # Calculate the average of the selected metric
            average_metrics = filtered_data.groupby([data.columns[division_col], data.columns[period_col]])[selected_metric].agg(['mean', 'count']).reset_index()
            average_metrics = average_metrics.sort_values(by='mean', ascending=False)

            # Calculate the overall average score for each period
            overall_avg = filtered_data.groupby(data.columns[period_col])[selected_metric].mean().reset_index()

            # Create the scatter plot with Plotly
            fig = px.scatter(average_metrics, x=data.columns[division_col], y='mean',
                            color=data.columns[period_col],
                            hover_name=data.columns[division_col],
                            hover_data={'mean': ':.2f', 'count': True},
                            labels={'mean': 'Average score', 'count': 'Number of responses'},
                            color_discrete_sequence=['#0C275C', '#6398DF'])

            # Add horizontal lines for the overall average score for each period
            for period, color in zip(overall_avg[data.columns[period_col]], ['#0C275C', '#6398DF']):
                avg_score = overall_avg[overall_avg[data.columns[period_col]] == period][selected_metric].values[0]
                fig.add_hline(y=avg_score, line_color=color, line_width=2,
                            annotation_text=f"Avg: {avg_score:.1f}",  # Text indicating the average
                            annotation_position="top right",  # Positioning it at the top right
                            annotation_font_size=10,  # Setting the font size
                            annotation_font_color=color,  # Making the font color the same as the line color
                            annotation_showarrow=False)  # Not showing any arrow pointing to the line

            # Add a note in the bottom left area of the scatter chart
            fig.add_annotation(
                text="Please click on the division to see the detailed performance",
                xref="paper", yref="paper",
                x=0, y=0,
                showarrow=False,
                font=dict(size=10, color="grey")
            )

            # Update the layout of the scatter plot
            fig.update_layout(
                title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},  # Set the title of the chart to the selected metric, make it bold, reduce the size, set the color to black, and align it to the left
                xaxis_showticklabels=False,  # Ensure x-axis labels are not shown
                xaxis=dict(
                    showticklabels=False, 
                    showgrid=False,  # Remove vertical gridlines
                    zeroline=False
                ),
                xaxis_title=None,  # Remove the x-axis title
                yaxis_title=None,  # Remove the y-axis title
                yaxis=dict(
                    showticklabels=True,  # Enable y-axis labels
                    showgrid=True,  # Show horizontal gridlines
                    zeroline=False,
                    range=[0, average_metrics['mean'].max() + 1]  # Set the range of the y-axis
                ),
                legend=dict(
                    x=1, y=1,
                    xanchor='right', yanchor='top'
                ),
                legend_title_text='',  # Remove the title from the legend
                margin=dict(l=15, r=5, t=25, b=5)  # Adjust left, right, top, bottom margins
            )

            # Capture selected points from the scatter plot using plotly_events
            selected_points = plotly_events(fig, key="scatter")

            # Update the bar chart if a point is selected
            if selected_points:
                selected_division_name = selected_points[0]['x']  # Get the division name from the selected point
                update_bar_chart(selected_division_name)  # Update the bar chart with the selected division

    with tab2:
        # Filters with separate expanders
        col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
        with col1:
            with st.expander("Period"):
                selected_period = st.multiselect(f"Select {data.columns[period_col]}:", data.iloc[:, period_col].unique(), default=data.iloc[:, period_col].unique(), key="feature1_period")

        with col2:
            with st.expander("Metrics"):
                selected_metric = st.selectbox("Select Metric:", data.columns[metrics_cols], index=len(metrics_cols) - 1, key="feature1_metrics")

        with col3:
            with st.expander(f"{data.columns[feature_2_col]}"):
                selected_feature_2 = st.multiselect(f"Select {data.columns[feature_2_col]}:", data.iloc[:, feature_2_col].unique(), default=data.iloc[:, feature_2_col].unique(), key="feature1_feature_2")

        with col4:
            with st.expander(f"{data.columns[feature_1_col]}"):
                selected_feature_1 = st.multiselect(f"Select {data.columns[feature_1_col]}:", data.iloc[:, feature_1_col].unique(), default=data.iloc[:, feature_1_col].unique(), key="feature1_feature_1")

        col_chart, col_bar_chart = st.columns([7, 5])
        with col_chart:
            # Ensure all filters are properly referenced here
            filtered_data = data[
                (data.iloc[:, period_col].isin(selected_period)) &
                (data.iloc[:, feature_2_col].isin(selected_feature_2)) &
                (data.iloc[:, feature_1_col].isin(selected_feature_1))
            ]

            # Calculate the average of the selected metric
            average_metrics = filtered_data.groupby([data.columns[division_col], data.columns[period_col]])[selected_metric].agg(['mean', 'count']).reset_index()
            average_metrics = average_metrics.sort_values(by='mean', ascending=False)

            # Calculate the overall average score for each period
            overall_avg = filtered_data.groupby(data.columns[period_col])[selected_metric].mean().reset_index()

            # Create the column chart with Plotly
            fig = px.bar(average_metrics, x=data.columns[division_col], y='mean',
                         color=data.columns[period_col],
                         hover_name=data.columns[division_col],
                         hover_data={'mean': ':.2f', 'count': True},
                         labels={'mean': 'Average score', 'count': 'Number of responses'},
                         color_discrete_sequence=['#0C275C', '#6398DF'],
                         barmode='group')  # Set barmode to 'group' for a regular column chart

            # Add horizontal lines for the overall average score for each period
            for period, color in zip(overall_avg[data.columns[period_col]], ['#0C275C', '#6398DF']):
                avg_score = overall_avg[overall_avg[data.columns[period_col]] == period][selected_metric].values[0]
                fig.add_hline(y=avg_score, line_color=color, line_width=2,
                              annotation_text=f"Avg: {avg_score:.1f}",  # Text indicating the average
                              annotation_position="top right",  # Positioning it at the top right
                              annotation_font_size=10,  # Setting the font size
                              annotation_font_color=color,  # Making the font color the same as the line color
                              annotation_showarrow=False)  # Not showing any arrow pointing to the line

            # Add a note in the bottom left area of the column chart
            fig.add_annotation(
                text="Please click on the division to see the detailed performance",
                xref="paper", yref="paper",
                x=0, y=-0.05,
                showarrow=False,
                font=dict(size=10, color="grey")
            )

            # Update the layout of the column chart
            fig.update_layout(
                title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},  # Set the title of the chart to the selected metric, make it bold, reduce the size, set the color to black, and align it to the left
                xaxis_showticklabels=False,  # Ensure x-axis labels are not shown
                xaxis=dict(
                    showticklabels=False, 
                    showgrid=False,  # Remove vertical gridlines
                    zeroline=False
                ),
                xaxis_title=None,  # Remove the x-axis title
                yaxis_title=None,  # Remove the y-axis title
                yaxis=dict(
                    showticklabels=True,  # Enable y-axis labels
                    showgrid=True,  # Show horizontal gridlines
                    zeroline=False,
                    range=[0, average_metrics['mean'].max() + 1]  # Set the range of the y-axis
                ),
                legend=dict(
                    orientation='h',  # Distribute legend items horizontally
                    x=0.5, y=0.9,  # Position the legend on top of the chart, centered
                    xanchor='center', yanchor='bottom',
                    itemwidth=100  # Set a fixed width for each legend item
                ),
                legend_title_text='',  # Remove the title from the legend
                margin=dict(l=15, r=100, t=25, b=5)  # Adjust left, right, top, bottom margins
            )

            # Capture selected points from the column chart using plotly_events
            selected_points = plotly_events(fig, key="feature1_bar")

            # Update the bar chart if a point is selected
            if selected_points:
                selected_division_name = selected_points[0]['x']  # Get the division name from the selected point
                update_bar_chart(selected_division_name)  # Update the bar chart with the selected division
