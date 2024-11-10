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

# Function to categorize age into predefined ranges
def map_age_to_range(age):
    if age <= 5:
        return "<6 years"
    elif 6 <= age <= 7:
        return "6-7 years"
    elif 7 < age <= 9:
        return "8-9 years"
    else:
        return ">9 years"

# Apply the function to create a new column in the dataframe for age ranges
data['Age Range'] = data['Age'].apply(map_age_to_range)

# Define possible metrics for user selection based on survey responses or data columns
metrics_options = [
    "How well do our coaches teach children?",
    "How would you rate the professionalism of our coaches?",
    "How would you rate our coaches' enthusiasm and their ability to engage the children?",
    "How much individual attention/support does your child receive from our coaches?",
    "How organised and structured are our classes?",
    "Rate the punctuality of your child's coach",
    "Rate the improvement in your child’s football skills since attending our classes.",
    "Rate the growth of your child’s confidence level since joining our classes.",
    "How would you rate the quality of support provided by our customer service team?",
    "How likely are you to recommend Samba Soccer Schools to your friends and family?"
]

# Function to update the bar chart based on the selected class
def update_bar_chart(class_name):
    class_data = data[data['Class'] == class_name]
    metrics_avg = class_data[metrics_options].mean().sort_values(ascending=True)
    bar_fig = px.bar(metrics_avg, x=metrics_avg.values, y=metrics_avg.index, orientation='h',
                     text=metrics_avg.values, labels={'y': '', 'x': 'Average Score'})  # Remove y-axis labels
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

    bar_fig.update_traces(texttemplate='%{x:.1f}', textposition='inside', marker_color='#0C275C', textfont_color='white', textangle=0)  # Display values outside the bars and set bar color

    bar_fig.update_layout(
        title={'text': f"<b>{class_name}</b>", 'font': {'size': 14, 'color': 'black'}, 'x': 0, 'xanchor': 'left'},
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels
            showgrid=False, 
            zeroline=False,
            range=[0, 11]  # Set the range of the x-axis from 0 to 11
        ),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        showlegend=False,
        margin=dict(l=15, r=50, t=42, b=5),  
        bargap=0.55,  
        annotations=annotations  # Add annotations to the layout
    )

    col_bar_chart.plotly_chart(bar_fig, use_container_width=True)

# Main layout: Divide the main area into a sidebar for filters and a main content area for displaying charts
left_margin, main_content = st.columns([3, 12])

with main_content:
    # Tabs for Performance by Class and Performance by Age Group
    tab1, tab2 = st.tabs(["Performance by Class", "Performance by Age Group"])

    with tab1:
        # Filters with separate expanders
        col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
        with col1:
            with st.expander("Period"):
                selected_period = st.multiselect("Select Period:", data['Period'].unique(), default=data['Period'].unique(), key="class_period")

        with col2:
            with st.expander("Metrics"):
                selected_metric = st.selectbox("Select Metric:", metrics_options, index=9, key="class_metrics")

        with col3:
            with st.expander("Membership Period"):
                selected_membership_period = st.multiselect("Select Membership Period:", data['How long have you been a member at Samba Soccer Schools?'].unique(), default=data['How long have you been a member at Samba Soccer Schools?'].unique(), key="class_membership_period")

        with col4:
            with st.expander("Age Group"):
                selected_age_group = st.multiselect("Select Age Group:", ["<6 years", "6-7 years", "8-9 years", ">9 years"], default=["<6 years", "6-7 years", "8-9 years", ">9 years"], key="class_age_group")

        col_chart, col_bar_chart = st.columns([7, 5])
        with col_chart:
            # Ensure all filters are properly referenced here
            filtered_data = data[
                (data['Period'].isin(selected_period)) &
                (data['How long have you been a member at Samba Soccer Schools?'].isin(selected_membership_period)) &
                (data['Age Range'].isin(selected_age_group))
            ]

            # Calculate the average of the selected metric
            average_metrics = filtered_data.groupby(['Class', 'Period'])[selected_metric].agg(['mean', 'count']).reset_index()
            average_metrics = average_metrics.sort_values(by='mean', ascending=False)

            # Calculate the overall average score for each period
            overall_avg = filtered_data.groupby('Period')[selected_metric].mean().reset_index()

            # Create the scatter plot with Plotly
            fig = px.scatter(average_metrics, x='Class', y='mean',
                            color='Period',
                            hover_name='Class',
                            hover_data={'mean': ':.2f', 'count': True},
                            labels={'mean': 'Average score', 'count': 'Number of responses'},
                            color_discrete_sequence=['#0C275C', '#6398DF'])

            # Add horizontal lines for the overall average score for each period
            for period, color in zip(overall_avg['Period'], ['#0C275C', '#6398DF']):
                avg_score = overall_avg[overall_avg['Period'] == period][selected_metric].values[0]
                fig.add_hline(y=avg_score, line_color=color, line_width=2,
                            annotation_text=f"Avg: {avg_score:.1f}",  # Text indicating the average
                            annotation_position="top right",  # Positioning it at the top right
                            annotation_font_size=10,  # Setting the font size
                            annotation_font_color=color,  # Making the font color the same as the line color
                            annotation_showarrow=False)  # Not showing any arrow pointing to the line

            # Add a note in the bottom left area of the scatter chart
            fig.add_annotation(
                text="Please click on the class to see the detailed performance",
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
                selected_class_name = selected_points[0]['x']  # Get the class name from the selected point
                update_bar_chart(selected_class_name)  # Update the bar chart with the selected class
                

    # Second tab: Performance by Age Group
    with tab2:
        # Filters with separate expanders
        col1, col2, col3, col4 = st.columns([3.5, 3.5, 3.5, 3.5])
        with col1:
            with st.expander("Period"):
                selected_period = st.multiselect("", data['Period'].unique(), default=data['Period'].unique(), key="age_group_period")

        with col2:
            with st.expander("Metrics"):
                selected_metric = st.selectbox("", metrics_options, index=9, key="age_group_metrics")

        with col3:
            with st.expander("Membership Period"):
                selected_membership_period = st.multiselect("", data['How long have you been a member at Samba Soccer Schools?'].unique(), default=data['How long have you been a member at Samba Soccer Schools?'].unique(), key="age_group_membership_period")

        with col4:
            with st.expander("Class"):
                selected_class = st.multiselect("", data['Class'].unique(), default=data['Class'].unique(), key="age_group_class")

        col_chart, col_bar_chart = st.columns([7, 5])
        with col_chart:
            # Ensure all filters are properly referenced here
            filtered_data = data[
                (data['Period'].isin(selected_period)) &
                (data['How long have you been a member at Samba Soccer Schools?'].isin(selected_membership_period)) &
                (data['Class'].isin(selected_class))
            ]

            # Calculate the average of the selected metric for each age group and period
            average_metrics_age_group = filtered_data.groupby(['Age Range', 'Period'])[selected_metric].mean().reset_index()

            # Calculate the overall average score for each period
            overall_avg_age_group = filtered_data.groupby('Period')[selected_metric].mean().reset_index()

            # Create the column chart with Plotly
            fig_age_group = px.bar(
                average_metrics_age_group,
                x='Age Range',
                y=selected_metric,
                color='Period',
                barmode='group',
                labels={selected_metric: 'Average Score', 'Age Range': 'Age Group'},
                title=f"<b>{selected_metric}</b>",
                color_discrete_sequence=['rgba(12, 39, 92, 0.7)', 'rgba(99, 152, 223, 0.7)'],  # Add transparency to bar colors
                category_orders={'Age Range': ["<6 years", "6-7 years", "8-9 years", ">9 years"]}  # Sort x-axis labels
            )
            
            # Add horizontal lines for the overall average score for each period
            for period, color in zip(overall_avg_age_group['Period'], ['rgba(12, 39, 92, 0.7)', 'rgba(99, 152, 223, 0.7)']):
                avg_score = overall_avg_age_group[overall_avg_age_group['Period'] == period][selected_metric].values[0]
                fig_age_group.add_hline(y=avg_score, line_color=color, line_width=2,
                                        annotation_text=f"Avg: {avg_score:.1f}",  # Text indicating the average
                                        annotation_position="right",  # Positioning it at the right
                                        annotation_font_size=10,  # Setting the font size
                                        annotation_font_color=color,  # Making the font color the same as the line color
                                        annotation_showarrow=False)  # Not showing any arrow pointing to the line
            
            # Update the layout of the column chart
            fig_age_group.update_layout(
                title_text=f"<b>{selected_metric}</b>",  # Set the title text
                title_font=dict(size=12, color='black'),  # Set the title font
                title_x=0,  # Align the title to the left
                xaxis_title=None,  # Remove the x-axis title
                yaxis_title=None,  # Remove the y-axis title
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, zeroline=False, range=[0, average_metrics_age_group[selected_metric].max() + 1]),  # Set y-axis range from 0 to max + 1
                showlegend=True,
                legend=dict(
                    orientation='h',  # Distribute legend items horizontally
                    x=0.5, y=0.95,  # Position the legend on top of the chart, centered
                    xanchor='center', yanchor='bottom',
                    itemwidth=100,  # Set a fixed width for each legend item
                    traceorder='normal'  # Control the order of the legend items
                ),
                legend_title_text='', 
                margin=dict(l=20, r=100, t=50, b=50),  # Adjust top margin to create space for the legend
                bargap=0.3
            )
            
            # Add an annotation to the column chart
            fig_age_group.add_annotation(
                text="Click on the columns to see the top performing classes in this age group",
                xref="paper", yref="paper",
                x=0, y=-0.1,  # Adjust the position of the annotation
                xanchor='left',  # Align the text to the left
                showarrow=False,
                font=dict(size=10, color="grey")
            )

            # Capture selected points from the column chart using plotly_events
            selected_points_age_group = plotly_events(fig_age_group, key="age_group_bar", override_width="100%")

        with col_bar_chart:
            if selected_points_age_group:
                selected_age_group = selected_points_age_group[0]['x']  # Get the age group from the selected point

                # Filter data for the selected age group
                filtered_data_age_group = filtered_data[filtered_data['Age Range'] == selected_age_group]

                # Calculate the average of the selected metric for each class
                average_metrics_class = filtered_data_age_group.groupby('Class')[selected_metric].mean().sort_values(ascending=True).head(10).reset_index()

                # Create the bar chart with Plotly
                fig_class = px.bar(average_metrics_class, x=selected_metric, y='Class', orientation='h',
                                   text=average_metrics_class[selected_metric], labels={'y': '', 'x': 'Average Score'},  # Remove axis titles
                                   title=f"Top 10 Classes in {selected_age_group}",
                                   color_discrete_sequence=['#0C275C'])
                
                # Configure the text and positioning for annotations
                annotations = []
                for idx, row in average_metrics_class.iterrows():
                    annotations.append({
                        'x': 0,  # Set x position to 0
                        'y': row['Class'],  # Position at the respective class
                        'xref': 'x',  # Reference to the x-axis for x-coordinate
                        'yref': 'y',  # Reference to the y-axis for y-coordinate
                        'text': row['Class'],  # Class name as text
                        'font': {'color': 'black', 'size': 12},
                        'xanchor': 'left',  # Align text to the left
                        'xshift': 0,  # No horizontal shift
                        'showarrow': False,  # Remove the arrow
                        'yshift': +18,  # Vertical offset to push the text above the bar
                    })
                
                # Update the layout of the bar chart
                fig_class.update_traces(texttemplate='%{x:.1f}', textposition='inside', marker_color='#0C275C', textfont_color='white', textangle=0)  # Display values inside the bars and set bar color
                fig_class.update_layout(
                    title_text=f"<b>Top 10 Classes in {selected_age_group}</b>",  # Set the title text and make it bold
                    title_font=dict(size=12, color='black'),  # Set the title font
                    title_x=0,  # Align the title to the left
                    xaxis_title=None,  # Remove the x-axis title
                    yaxis_title=None,  # Remove the y-axis title
                    xaxis=dict(
                        showticklabels=False,  # Hide x-axis labels
                        showgrid=False, 
                        zeroline=False,
                        range=[0, 11]  # Set the range of the x-axis from 0 to 11
                    ),
                    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                    showlegend=False,
                    margin=dict(l=15, r=5, t=50, b=0),  
                    bargap=0.55,  
                    annotations=annotations  # Add annotations to the layout
                )
                
                # Render the bar chart within the specified column width
                plotly_events(fig_class, key="class_bar")