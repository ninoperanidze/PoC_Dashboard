import streamlit as st  # Import Streamlit for building the web app
import pandas as pd  # Import pandas for data manipulation
import plotly.express as px  # Import Plotly Express for creating plots
import plotly.graph_objects as go  # Import Plotly Graph Objects for advanced plotting
from streamlit_plotly_events import plotly_events  # Import plotly_events for handling Plotly events in Streamlit

# Set page configuration to wide layout
st.set_page_config(layout="wide")

# Load the dataset
file_path = r'data_cleaned_3.xlsx'  # Path to the Excel file containing the data
data = pd.read_excel(file_path)  # Read the Excel file into a pandas DataFrame

# Sidebar for selecting the division column
with st.sidebar:
    division_col_index = st.selectbox("Select Division Column", options=[0, 2, 3], format_func=lambda x: data.columns[x])
    division_col = data.columns[division_col_index]
    feature_columns = [0, 2, 3]
    feature_columns.remove(division_col_index)
    feature_1_col = feature_columns[0]
    feature_2_col = feature_columns[1]

# Define constant columns
period_col = 1  # Assuming 'Period' is always in the second column
metrics_cols = list(range(4, data.shape[1]))  # Assuming metrics start from the 5th column

# Convert period_col to categorical if it is numeric
if pd.api.types.is_numeric_dtype(data.iloc[:, period_col]):
    data.iloc[:, period_col] = data.iloc[:, period_col].astype(str)

# Transform Yes/No columns to boolean and identify other types
boolean_cols = []
numeric_cols = []
single_select_cols = []
multi_select_cols = []

for col in metrics_cols:
    col_name = data.columns[col]
    if '(Y/N)' in col_name:
        data.iloc[:, col] = data.iloc[:, col].str.lower().map({'yes': True, 'y': True, 'no': False, 'n': False})
        boolean_cols.append(col)
    elif '(Single Select)' in col_name:
        single_select_cols.append(col)
    elif '(Multi Select)' in col_name:
        multi_select_cols.append(col)
    else:
        numeric_cols.append(col)


# Define possible metrics for user selection based on survey responses or data columns
metrics_options = data.columns[metrics_cols].tolist()

# Function to update the bar chart based on the selected division
def update_bar_chart(division_name):
    metrics_avg = division_data.mean().sort_values(ascending=True)
    metrics_count = division_data.count()
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
main_content = st.columns([1, 11])  # Sidebar width fixed to 1, main content uses remaining space

with main_content[1]:
    # Tabs for Performance by Division and Performance by Feature 1
    tab1, tab2 = st.tabs([f"Performance by {division_col}", f"Performance by {division_col} Version 2"])

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

            # Calculate the average of the selected metric for boolean and numeric columns
            if selected_metric in data.columns[boolean_cols] or selected_metric in data.columns[numeric_cols]:
                average_metrics = filtered_data.groupby([division_col, data.columns[period_col]])[selected_metric].agg(['mean', 'count']).reset_index()
                average_metrics = average_metrics.sort_values(by='mean', ascending=False)
                overall_avg = filtered_data.groupby(data.columns[period_col])[selected_metric].mean().reset_index()
            # Count occurrences for single select and multi select columns
            elif selected_metric in data.columns[single_select_cols] or selected_metric in data.columns[multi_select_cols]:
                average_metrics = filtered_data.groupby([division_col, data.columns[period_col], selected_metric]).size().reset_index(name='count')
                average_metrics = average_metrics.sort_values(by='count', ascending=False)
                overall_avg = None  

            # Create the scatter plot with Plotly
            if selected_metric in data.columns[boolean_cols]:
                # Handle boolean metrics
                fig = px.scatter(average_metrics, x=division_col, y='mean',
                                color=data.columns[period_col],
                                hover_name=division_col,
                                hover_data={'mean': ':.2%', 'count': True},
                                labels={'mean': 'Average score (%)', 'count': 'Number of responses'},
                                color_discrete_sequence=['#0C275C', '#6398DF'])
                fig.update_layout(
                    yaxis=dict(
                        tickformat=".0%",  # Set y-axis to percentage format
                        range=[0, 1.1],  # Set y-axis range from 0% to 110%
                        showticklabels=True,
                        showgrid=True,  # Show horizontal gridlines
                        zeroline=False
                    ),
                    title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
                    xaxis_showticklabels=False,
                    xaxis=dict(
                        showticklabels=False, 
                        showgrid=False,  # Remove vertical gridlines
                        zeroline=False
                    ),
                    xaxis_title=None,
                    yaxis_title=None,
                    legend=dict(
                        x=1, y=1,
                        xanchor='right', yanchor='top'
                    ),
                    legend_title_text='',
                    margin=dict(l=30, r=5, t=25, b=5)
                )
            
            elif selected_metric in data.columns[single_select_cols] or selected_metric in data.columns[multi_select_cols]:
                # Handle single select and multi select metrics            
                # Combine division_col and 'Year' into a single column for plotting
                average_metrics['Programme_Year'] = average_metrics[division_col] + ' (' + average_metrics['Year'].astype(str) + ')'

                # Calculate the percentage of each count relative to the total count for each Programme_Year
                total_counts = average_metrics.groupby('Programme_Year')['count'].transform('sum')
                average_metrics['percentage'] = average_metrics['count'] / total_counts * 100

                # Determine unique periods and directly assign opacities
                unique_periods = average_metrics['Year'].unique()
                period_opacity_map = {unique_periods[0]: 1, unique_periods[1]: 0.5}  # Assigning opacity directly
                average_metrics['opacity'] = average_metrics['Year'].map(period_opacity_map)

                # Create the vertical 100% stacked bar chart with Plotly
                fig = px.bar(
                    average_metrics,
                    x='percentage',
                    y='Programme_Year',  # Use the combined column as the y-axis
                    color='Choose your favourite class (Single Select)',  # Use the single select column for color
                    orientation='h',
                    labels={'percentage': 'Percentage of responses', 'Programme_Year': 'Programme and Year'},
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    barmode='stack',  # Set barmode to 'stack' for a stacked bar chart
                    text_auto=True,  # Automatically add text labels to the bars
                    opacity=average_metrics['opacity']  # Apply variable opacity based on the period
                )

                fig.update_layout(
                    height=450,  # Fixed height
                    width=700,  # Fixed width to fit the designated area
                    title={'text': f"<b>Choose your favourite class</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
                    xaxis_showticklabels=True,  # Ensure x-axis labels are shown
                    xaxis_title=None,  # Remove the x-axis title
                    yaxis_title=None,  # Remove the y-axis title
                    yaxis=dict(
                        showticklabels=True,  # Enable y-axis labels
                        showgrid=True,  # Show horizontal gridlines
                        zeroline=False,
                        automargin=True  # Automatically adjust margin to fit y-axis labels
                    ),
                    legend=dict(
                        orientation='h',  # Set the orientation of the legend to horizontal
                        x=0.5, y=-0.2,  # Position the legend below the chart, centered
                        xanchor='center', yanchor='bottom',
                        itemwidth=100  # Set a fixed width for each legend item
                    ),
                    legend_title_text='',  # Remove the title from the legend
                    margin=dict(l=10, r=50, t=25, b=5)  # Adjust left, right, top, bottom margins
                )

                # Display the chart
                st.plotly_chart(fig)

            
            else:
                # Handle numeric metrics
                fig = px.scatter(average_metrics, x=division_col, y='mean',
                                color=data.columns[period_col],
                                hover_name=division_col,
                                hover_data={'mean': ':.2f', 'count': True},
                                labels={'mean': 'Average score', 'count': 'Number of responses'},
                                color_discrete_sequence=['#0C275C', '#6398DF'])
                fig.update_layout(
                    title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
                    xaxis_showticklabels=False,
                    xaxis=dict(
                        showticklabels=False, 
                        showgrid=False,  # Remove vertical gridlines
                        zeroline=False
                    ),
                    xaxis_title=None,
                    yaxis_title=None,
                    yaxis=dict(
                        showticklabels=True,
                        showgrid=True,  # Show horizontal gridlines
                        zeroline=False,
                        range=[0, average_metrics['mean'].max() + 1]  # Set the range of the y-axis
                    ),
                    legend=dict(
                        x=1, y=1,
                        xanchor='right', yanchor='top'
                    ),
                    legend_title_text='',
                    margin=dict(l=15, r=5, t=25, b=5)
                )
            
            # Add horizontal lines for the overall average score for each period (only for boolean and numeric metrics)
            if selected_metric in data.columns[boolean_cols] or selected_metric in data.columns[numeric_cols]:
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
            
                # Capture selected points from the scatter plot using plotly_events
                selected_points = plotly_events(fig, key="scatter")
                
                # Update the bar chart if a point is selected
                if selected_points:
                    try:
                        # Check if selected_points is not empty and contains the expected keys
                        if len(selected_points) > 0 and 'x' in selected_points[0]:
                            selected_division_name = selected_points[0]['x']  # Get the division name from the selected point
                            
                            # Check if the selected division name exists in the data
                            if selected_division_name in data[division_col].values:
                               
                                # Show the selected data
                                division_data = data[data[division_col] == selected_division_name]
                                
                                # Filter to include only boolean and numeric columns
                                division_data = division_data[data.columns[boolean_cols + numeric_cols]]
                                update_bar_chart(selected_division_name)  # Update the bar chart with the selected division
                            else:
                                st.write("Selected division name not found in the data.")
                        else:
                            st.write("Key 'x' not found in selected points.")
                    except IndexError as e:
                        st.write("IndexError occurred while accessing selected points:", e)
                    except Exception as e:
                        st.write("An unexpected error occurred:", e)
                else:
                    st.write("No points selected or plotly_events returned an empty list.")

    # with tab2:
    #     # Filters with separate expanders
    #     col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
    #     with col1:
    #         with st.expander("Period"):
    #             selected_period = st.multiselect(f"Select {data.columns[period_col]}:", data.iloc[:, period_col].unique(), default=data.iloc[:, period_col].unique(), key="division_period")

    #     with col2:
    #         with st.expander("Metrics"):
    #             selected_metric = st.selectbox("Select Metric:", data.columns[metrics_cols], index=len(metrics_cols) - 1, key="division_metrics")

    #     with col3:
    #         with st.expander(f"{data.columns[feature_2_col]}"):
    #             selected_feature_2 = st.multiselect(f"Select {data.columns[feature_2_col]}:", data.iloc[:, feature_2_col].unique(), default=data.iloc[:, feature_2_col].unique(), key="division_feature_2")

    #     with col4:
    #         with st.expander(f"{data.columns[feature_1_col]}"):
    #             selected_feature_1 = st.multiselect(f"Select {data.columns[feature_1_col]}:", data.iloc[:, feature_1_col].unique(), default=data.iloc[:, feature_1_col].unique(), key="division_feature_1")

    #     col_chart, col_bar_chart = st.columns([7, 5])
    #     with col_chart:
    #         # Ensure all filters are properly referenced here
    #         filtered_data = data[
    #             (data.iloc[:, period_col].isin(selected_period)) &
    #             (data.iloc[:, feature_2_col].isin(selected_feature_2)) &
    #             (data.iloc[:, feature_1_col].isin(selected_feature_1))
    #         ]

    #         # Calculate the average of the selected metric for boolean and numeric columns
    #         if selected_metric in data.columns[boolean_cols] or selected_metric in data.columns[numeric_cols]:
    #             average_metrics = filtered_data.groupby([division_col, data.columns[period_col]])[selected_metric].agg(['mean', 'count']).reset_index()
    #             average_metrics = average_metrics.sort_values(by='mean', ascending=False)
    #             overall_avg = filtered_data.groupby(data.columns[period_col])[selected_metric].mean().reset_index()
    #         # Count occurrences for single select and multi select columns
    #         elif selected_metric in data.columns[single_select_cols] or selected_metric in data.columns[multi_select_cols]:
    #             average_metrics = filtered_data.groupby([division_col, data.columns[period_col], selected_metric]).size().reset_index(name='count')
    #             average_metrics = average_metrics.sort_values(by='count', ascending=False)
    #             overall_avg = None  

    #         # Create the scatter plot with Plotly
    #         if selected_metric in data.columns[boolean_cols]:
    #             # Handle boolean metrics
    #             fig = px.scatter(average_metrics, x=division_col, y='mean',
    #                             color=data.columns[period_col],
    #                             hover_name=division_col,
    #                             hover_data={'mean': ':.2%', 'count': True},
    #                             labels={'mean': 'Average score (%)', 'count': 'Number of responses'},
    #                             color_discrete_sequence=['#0C275C', '#6398DF'])
    #             fig.update_layout(
    #                 yaxis=dict(
    #                     tickformat=".0%",  # Set y-axis to percentage format
    #                     range=[0, 1.1],  # Set y-axis range from 0% to 110%
    #                     showticklabels=True,
    #                     showgrid=True,  # Show horizontal gridlines
    #                     zeroline=False
    #                 ),
    #                 title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
    #                 xaxis_showticklabels=False,
    #                 xaxis=dict(
    #                     showticklabels=False, 
    #                     showgrid=False,  # Remove vertical gridlines
    #                     zeroline=False
    #                 ),
    #                 xaxis_title=None,
    #                 yaxis_title=None,
    #                 legend=dict(
    #                     x=1, y=1,
    #                     xanchor='right', yanchor='top'
    #                 ),
    #                 legend_title_text='',
    #                 margin=dict(l=30, r=5, t=25, b=5)
    #             )
            
    #         elif selected_metric in data.columns[single_select_cols] or selected_metric in data.columns[multi_select_cols]:
    #             # Handle single select and multi select metrics            
            
    #             # Combine division_col and 'Year' into a single column for plotting
    #             average_metrics['Programme_Year'] = average_metrics[division_col] + ' (' + average_metrics['Year'].astype(str) + ')'
            
    #             # Calculate the percentage of each count relative to the total count for each Programme_Year
    #             total_counts = average_metrics.groupby('Programme_Year')['count'].transform('sum')
    #             average_metrics['percentage'] = average_metrics['count'] / total_counts * 100
            
    #             # Create the vertical 100% stacked bar chart with Plotly
    #             fig = px.bar(
    #                 average_metrics,
    #                 x='percentage',
    #                 y='Programme_Year',  # Use the combined column as the y-axis
    #                 color=selected_metric,  # This should be your selected_metric
    #                 orientation='h',
    #                 labels={'percentage': 'Percentage of responses', 'Programme_Year': 'Programme and Year'},
    #                 color_discrete_sequence=px.colors.qualitative.Plotly,
    #                 barmode='stack',  # Set barmode to 'stack' for a stacked bar chart
    #                 text_auto=True,  # Automatically add text labels to the bars
    #             )
            
    #             fig.update_layout(
    #                 height=450,  # Fixed height
    #                 width=700,  # Fixed width to fit the designated area
    #                 title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
    #                 xaxis_showticklabels=True,  # Ensure x-axis labels are shown
    #                 xaxis_title=None,  # Remove the x-axis title
    #                 yaxis_title=None,  # Remove the y-axis title
    #                 yaxis=dict(
    #                     showticklabels=True,  # Enable y-axis labels
    #                     showgrid=True,  # Show horizontal gridlines
    #                     zeroline=False,
    #                     automargin=True  # Automatically adjust margin to fit y-axis labels
    #                 ),
    #                 legend=dict(
    #                     orientation='h',  # Set the orientation of the legend to horizontal
    #                     x=0.5, y=-0.2,  # Position the legend below the chart, centered
    #                     xanchor='center', yanchor='bottom',
    #                     itemwidth=100  # Set a fixed width for each legend item
    #                 ),
    #                 legend_title_text='',  # Remove the title from the legend
    #                 margin=dict(l=10, r=50, t=25, b=5)  # Adjust left, right, top, bottom margins
    #             )
            
    #             # Display the chart
    #             st.plotly_chart(fig)
            
    #         else:
    #             # Create the horizontal bar chart with Plotly
    #             fig = px.bar(average_metrics, x='mean', y=division_col,
    #                          color=data.columns[period_col],
    #                          orientation='h',
    #                          hover_data={'mean': ':.2f', 'count': True},
    #                          labels={'mean': 'Average score', 'count': 'Number of responses'},
    #                          color_discrete_sequence=['#0C275C', '#6398DF'],
    #                          barmode='group')  # Set barmode to 'group' for a regular bar chart
                
    #             # Update layout with fixed height and responsive width
    #             fig.update_layout(
    #                 height=450,  # Fixed height
    #                 width=700,  # Fixed width to fit the designated area
    #             )
                
    #             # Update traces to customize hover information
    #             fig.update_traces(
    #                 hovertemplate='Average score: %{x:.2f}<br>Number of responses: %{customdata[0]}',
    #                 textangle=0,
    #                 textposition='inside',
    #                 insidetextanchor='start',
    #                 hoverlabel=dict(
    #                     font_size=12,  # Font size of the hover label
    #                     align='left'
    #                 )
    #             )
                
    #             # Add vertical lines for the overall average score for each period
    #             for period, color in zip(overall_avg[data.columns[period_col]], ['#0C275C', '#6398DF']):
    #                 avg_score = overall_avg[overall_avg[data.columns[period_col]] == period][selected_metric].values[0]
    #                 fig.add_vline(x=avg_score, line_color=color, line_width=2,
    #                               annotation_text=f"Avg: {avg_score:.1f}",  # Text indicating the average
    #                               annotation_position="top right",  # Positioning it at the top right
    #                               annotation_font_size=10,  # Setting the font size
    #                               annotation_font_color=color,  # Making the font color the same as the line color
    #                               annotation_showarrow=False)  # Not showing any arrow pointing to the line
                
    #             # Update the layout of the bar chart
    #             fig.update_layout(
    #                 title={'text': f"<b>{selected_metric}</b>", 'font': {'size': 12, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},  # Set the title of the chart to the selected metric, make it bold, reduce the size, set the color to black, and align it to the left
    #                 xaxis_showticklabels=True,  # Ensure x-axis labels are shown
    #                 xaxis=dict(
    #                     showticklabels=True, 
    #                     showgrid=True,  # Show vertical gridlines
    #                     zeroline=False
    #                 ),
    #                 xaxis_title=None,  # Remove the x-axis title
    #                 yaxis_title=None,  # Remove the y-axis title
    #                 yaxis=dict(
    #                     showticklabels=True,  # Enable y-axis labels
    #                     showgrid=True,  # Show horizontal gridlines
    #                     zeroline=False,
    #                     automargin=True,  # Automatically adjust margin to fit y-axis labels
    #                     range=[0, average_metrics['mean'].max() + 2]  # Set the range of the y-axis
    #                 ),
    #                 legend=dict(
    #                     orientation='h',  # Set the orientation of the legend to horizontal
    #                     x=-0.4, y=-0.2,  # Position the legend on top of the chart, centered
    #                     xanchor='left', yanchor='bottom',
    #                     itemwidth=80
    #                 ),
    #                 legend_title_text='',  # Remove the title from the legend
    #                 margin=dict(l=10, r=50, t=25, b=5)  # Adjust left, right, top, bottom margins
    #             )
                
    #             # Capture selected points from the bar chart using plotly_events
    #             selected_points = plotly_events(fig, key="feature1_bar_events")
                
    #             # Update the bar chart if a point is selected
    #             if selected_points:
    #                 try:
    #                     # Check if selected_points is not empty and contains the expected keys
    #                     if len(selected_points) > 0 and 'x' in selected_points[0]:
    #                         selected_division_name = selected_points[0]['x']  # Get the division name from the selected point
    #                         st.write("Selected Division Name:", selected_division_name)
                            
    #                         # Check if the selected division name exists in the data
    #                         if selected_division_name in data[division_col].values:
    #                             st.write("Division name found in data. Updating bar chart...")
                                
    #                             # Show the selected data
    #                             division_data = data[data[division_col] == selected_division_name]
                                
    #                             # Filter to include only boolean and numeric columns
    #                             division_data = division_data[data.columns[boolean_cols + numeric_cols]]
                                
    #                             st.write("Division Data:", division_data)
                                
    #                             update_bar_chart(selected_division_name)  # Update the bar chart with the selected division
    #                         else:
    #                             st.write("Selected division name not found in the data.")
    #                     else:
    #                         st.write("Key 'x' not found in selected points.")
    #                 except IndexError as e:
    #                     st.write("IndexError occurred while accessing selected points:", e)
    #                 except Exception as e:
    #                     st.write("An unexpected error occurred:", e)
    #             else:
    #                 st.write("No points selected or plotly_events returned an empty list.")