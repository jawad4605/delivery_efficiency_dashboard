"""
Delivery Efficiency Dashboard
Visualizes data from data/ folder with enhanced visualizations and export capabilities
"""

import os
import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Create outputs directory
os.makedirs('outputs', exist_ok=True)

# ---------- Data Loading ----------
try:
    master = pd.read_csv('data/device_master.csv')
    perf = pd.read_csv('data/performance.csv')
    loads = pd.read_csv('data/loads_by_day.csv', parse_dates=['date'])
    heat_df = pd.read_csv('data/idle_heatmap.csv').set_index('device_id')
    flows = pd.read_csv('data/sankey_flows.csv')
    events = pd.read_csv('data/warehouse_events.csv')
    summary = pd.read_csv('data/summary_metrics.csv').iloc[0]
    
    # Merge data
    master = master.merge(perf[['device_id','total_deliveries']], on='device_id', how='left').fillna(0)
    
except Exception as e:
    print(f"Error loading data: {e}")
    raise

# ---------- Enhanced Visualization Functions ----------
def create_map():
    # Add size scaling based on deliveries with a minimum size
    max_deliveries = master['total_deliveries'].max()
    size_scale = 15  # Base size for devices with 0 deliveries
    master['scaled_size'] = size_scale + (master['total_deliveries'] / max_deliveries * 25) if max_deliveries > 0 else size_scale
    
    # Create custom hover text
    master['hover_text'] = master.apply(
        lambda x: f"<b>{x['device_id']}</b><br>"
                 f"City: {x['city']}<br>"
                 f"Zone: {x['zone']}<br>"
                 f"Deliveries: {x['total_deliveries']}<br>"
                 f"Status: {x['status']}",
        axis=1
    )
    
    fig = px.scatter_mapbox(
        master,
        lat="lat",
        lon="lon",
        color="status",
        size="scaled_size",
        hover_name="hover_text",
        zoom=5,
        height=600,
        color_discrete_map={
            "Moving": "#2ECC40",  # Green
            "On-route": "#0074D9",  # Blue
            "Idling": "#FF851B",  # Orange
            "Inactive": "#AAAAAA"  # Gray
        },
        category_orders={"status": ["Moving", "On-route", "Idling", "Inactive"]}
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            center=dict(lat=master['lat'].mean(), lon=master['lon'].mean()),
            zoom=4.5
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Add a title annotation
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        text="Fleet Location and Status",
        showarrow=False,
        font=dict(size=16, family="Arial", color="black")
    )
    
    return fig

def create_sankey():
    nodes = pd.unique(flows[['src','trg']].values.ravel('K'))
    node_indices = {node: i for i, node in enumerate(nodes)}
    
    fig = go.Figure(go.Sankey(
        node=dict(
            label=nodes,
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.5),
            color=["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]
        ),
        link=dict(
            source=[node_indices[src] for src in flows['src']],
            target=[node_indices[trg] for trg in flows['trg']],
            value=flows['count'],
            color=["rgba(99, 110, 250, 0.3)" for _ in flows['count']]
        )
    ))
    
    fig.update_layout(
        title_text="<b>Delivery Flow Analysis</b>",
        title_font=dict(size=16, family="Arial"),
        height=500,
        margin={"r":0,"t":50,"l":0,"b":0},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_heatmap():
    # Add annotations to show values in cells
    annotations = []
    for y in range(heat_df.shape[0]):
        for x in range(heat_df.shape[1]):
            val = heat_df.iloc[y, x]
            if val > 0:  # Only show annotations for non-zero values
                annotations.append(
                    dict(
                        x=x,
                        y=y,
                        text=str(int(val)),
                        font=dict(color='white' if val > heat_df.values.max()/2 else 'black'),
                        showarrow=False
                    )
                )
    
    fig = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns,
        y=heat_df.index,
        colorscale='Viridis',
        hoverongaps=False,
        hoverinfo='z',
        colorbar=dict(title='Idle Minutes')
    ))
    
    fig.update_layout(
        title="<b>Idle Time Heatmap by Device and Day</b>",
        title_font=dict(size=16, family="Arial"),
        height=500,
        margin={"r":0,"t":50,"l":0,"b":0},
        xaxis_title="Day of Week",
        yaxis_title="Device ID",
        annotations=annotations
    )
    return fig

def create_donut():
    status_counts = master['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    # Create a subplot to add a title properly
    fig = make_subplots(rows=1, cols=1, specs=[[{'type':'domain'}]])
    
    fig.add_trace(go.Pie(
        labels=status_counts['status'],
        values=status_counts['count'],
        hole=0.5,
        marker_colors=["#2ECC40", "#0074D9", "#FF851B", "#AAAAAA"],
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='radial'
    ))
    
    fig.update_layout(
        title_text="<b>Fleet Status Distribution</b>",
        title_font=dict(size=16, family="Arial"),
        showlegend=False,
        margin={"r":0,"t":50,"l":0,"b":0},
        height=400
    )
    
    return fig

def create_barchart():
    loads['day'] = loads['date'].dt.strftime('%a')
    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    fig = px.bar(
        loads,
        x='day',
        y='loads',
        color='week',
        barmode='group',
        category_orders={"day": day_order},
        color_discrete_map={'current': '#1f77b4', 'last': '#d62728'},
        height=400,
        text='loads'
    )
    
    fig.update_traces(
        textposition='outside',
        textfont_size=12,
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8
    )
    
    fig.update_layout(
        title="<b>Weekly Load Comparison</b>",
        title_font=dict(size=16, family="Arial"),
        xaxis_title="Day of Week",
        yaxis_title="Number of Loads",
        margin={"r":0,"t":50,"l":0,"b":0},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title_text='Week'
    )
    
    return fig

def save_plot_images():
    """Export all visualizations as PNG files"""
    try:
        plots = {
            'fleet_map': create_map(),
            'delivery_flows': create_sankey(),
            'idle_time_heatmap': create_heatmap(),
            'status_distribution': create_donut(),
            'weekly_loads': create_barchart()
        }
        
        for name, fig in plots.items():
            fig.write_image(f"outputs/{name}.png", scale=2, width=1200, height=800)
        print("Successfully exported all plots as PNG files")
    except Exception as e:
        print(f"Error exporting plots: {e}")

# ---------- Dashboard Layout ----------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Delivery Efficiency Dashboard"

app.layout = html.Div([
    html.Div([
        html.H1("Delivery Fleet Efficiency Dashboard", 
                style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'})
    ], className='header'),
    
    # KPI Cards
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-truck", style={'fontSize': '24px', 'color': '#3498db'}),
                    html.Div("Active Devices", style={'fontSize': '14px', 'marginLeft': '10px'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Div(f"{summary['active_devices']}", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#2c3e50', 'marginTop': '10px'})
            ], className='kpi-card-content')
        ], className='kpi-card'),
        
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-clock", style={'fontSize': '24px', 'color': '#e74c3c'}),
                    html.Div("Idling Devices", style={'fontSize': '14px', 'marginLeft': '10px'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Div(f"{summary['idling_devices']}", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#2c3e50', 'marginTop': '10px'})
            ], className='kpi-card-content')
        ], className='kpi-card'),
        
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-boxes", style={'fontSize': '24px', 'color': '#2ecc71'}),
                    html.Div("Completed Loads", style={'fontSize': '14px', 'marginLeft': '10px'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Div(f"{summary['completed_loads']}", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#2c3e50', 'marginTop': '10px'})
            ], className='kpi-card-content')
        ], className='kpi-card'),
        
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-hourglass-half", style={'fontSize': '24px', 'color': '#f39c12'}),
                    html.Div("Idling Hours", style={'fontSize': '14px', 'marginLeft': '10px'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Div(f"{summary['total_idling_hr']:.1f}", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#2c3e50', 'marginTop': '10px'})
            ], className='kpi-card-content')
        ], className='kpi-card')
    ], className='kpi-row'),
    
    # First Row
    html.Div([
        html.Div([
            dcc.Graph(figure=create_map(), config={'displayModeBar': True})
        ], className='map-container'),
        
        html.Div([
            dcc.Graph(figure=create_sankey(), config={'displayModeBar': True})
        ], className='sankey-container')
    ], className='row'),
    
    # Second Row
    html.Div([
        html.Div([
            dcc.Graph(figure=create_heatmap(), config={'displayModeBar': True})
        ], className='heatmap-container'),
        
        html.Div([
            dcc.Graph(figure=create_donut(), config={'displayModeBar': True}),
            dcc.Graph(figure=create_barchart(), config={'displayModeBar': True})
        ], className='side-container')
    ], className='row'),
    
    # Events Table
    html.Div([
        html.H3("Recent Warehouse Events", style={'color': '#2c3e50', 'marginTop': '20px'}),
        dash_table.DataTable(
            id='events-table',
            columns=[{'name': col, 'id': col} for col in events.columns],
            data=events.to_dict('records'),
            page_size=10,
            style_table={
                'overflowX': 'auto',
                'borderRadius': '8px',
                'boxShadow': '0 4px 6px 0 rgba(0, 0, 0, 0.1)'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Arial',
                'border': '1px solid #e0e0e0'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], className='table-container')
], style={'padding': '20px', 'fontFamily': 'Arial'})

# CSS Styles
app.css.append_css({
    'external_url': [
        'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ]
})

app.css.append_css({
    'external_url': '''
    .header {
        background: linear-gradient(90deg, #3498db, #2c3e50);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: white;
    }
    
    .kpi-row {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    
    .kpi-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        flex: 1;
        margin: 10px;
        min-width: 200px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px 0 rgba(0, 0, 0, 0.15);
    }
    
    .kpi-card-content {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .row {
        display: flex;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .map-container {
        flex: 2;
        margin: 10px;
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        min-width: 60%;
    }
    
    .sankey-container {
        flex: 1;
        margin: 10px;
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        min-width: 35%;
    }
    
    .heatmap-container {
        flex: 2;
        margin: 10px;
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        min-width: 60%;
    }
    
    .side-container {
        flex: 1;
        margin: 10px;
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        min-width: 35%;
    }
    
    .table-container {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    
    @media (max-width: 1200px) {
        .map-container, .heatmap-container {
            min-width: 100%;
        }
        
        .sankey-container, .side-container {
            min-width: 100%;
        }
    }
    '''
})

# HTML Export Template
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Delivery Efficiency Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Save HTML dashboard
with open('outputs/delivery_dashboard.html', 'w') as f:
    f.write(app.index())

if __name__ == '__main__':
    save_plot_images()  # Export all plots as PNGs
    app.run(debug=True, port=8050)