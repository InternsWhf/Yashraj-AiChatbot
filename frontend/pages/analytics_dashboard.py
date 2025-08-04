import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import numpy as np

# Page configuration
st.set_page_config(
    page_title="WHF Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dashboard styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff6600;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-top: 5px;
    }
    
    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .header {
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>📊 WHF Analytics Dashboard</h1>
    <p>Real-time insights into chatbot usage and performance</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    st.markdown("### 🔧 Dashboard Controls")
    
    # Date range selector
    days = st.slider("Time Period (Days)", 1, 90, 30)
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📈 Key Metrics")
    st.markdown("- **Total Events**: All user interactions")
    st.markdown("- **Unique Users**: Active users in period")
    st.markdown("- **File Uploads**: Documents processed")
    st.markdown("- **Queries**: Questions answered")
    st.markdown("- **Success Rate**: % with context found")

# Function to fetch analytics data
def fetch_analytics_data(days=30):
    try:
        response = requests.get(f"http://localhost:8000/analytics/stats?days={days}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch analytics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to analytics API: {e}")
        return None

# Fetch data
with st.spinner("📊 Loading analytics data..."):
    data = fetch_analytics_data(days)

if data:
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data.get('total_events', 0):,}</div>
            <div class="metric-label">Total Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data.get('unique_users', 0):,}</div>
            <div class="metric-label">Unique Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data.get('file_uploads', 0):,}</div>
            <div class="metric-label">File Uploads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data.get('queries', 0):,}</div>
            <div class="metric-label">Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data.get('query_success_rate', 0):.1f}%</div>
            <div class="metric-label">Query Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data.get('avg_response_time', 0):.2f}s</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts section
    st.markdown("## 📈 Activity Charts")
    
    # Daily activity chart
    if 'daily_stats' in data and data['daily_stats']:
        st.markdown("### Daily Activity")
        
        # Convert daily stats to DataFrame
        daily_data = []
        for date, stats in data['daily_stats'].items():
            daily_data.append({
                'Date': date,
                'File Uploads': stats.get('file_uploads', 0),
                'Queries': stats.get('queries', 0),
                'Logins': stats.get('logins', 0),
                'Users': stats.get('users', 0)
            })
        
        df_daily = pd.DataFrame(daily_data)
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        df_daily = df_daily.sort_values('Date')
        
        # Create line chart
        fig_daily = go.Figure()
        
        fig_daily.add_trace(go.Scatter(
            x=df_daily['Date'],
            y=df_daily['File Uploads'],
            mode='lines+markers',
            name='File Uploads',
            line=dict(color='#ff6600', width=3)
        ))
        
        fig_daily.add_trace(go.Scatter(
            x=df_daily['Date'],
            y=df_daily['Queries'],
            mode='lines+markers',
            name='Queries',
            line=dict(color='#667eea', width=3)
        ))
        
        fig_daily.add_trace(go.Scatter(
            x=df_daily['Date'],
            y=df_daily['Logins'],
            mode='lines+markers',
            name='Logins',
            line=dict(color='#00ff88', width=3)
        ))
        
        fig_daily.update_layout(
            title="Daily Activity Trends",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # File type distribution
    if 'file_types' in data and data['file_types']:
        st.markdown("### File Type Distribution")
        
        file_types = data['file_types']
        if isinstance(file_types, dict):
            df_files = pd.DataFrame([
                {'File Type': k.upper(), 'Count': v} 
                for k, v in file_types.items()
            ])
            
            fig_files = px.pie(
                df_files, 
                values='Count', 
                names='File Type',
                title="Uploaded File Types",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_files.update_layout(height=400)
            st.plotly_chart(fig_files, use_container_width=True)
    
    # User activity heatmap
    st.markdown("### User Activity Heatmap")
    
    # Generate sample heatmap data (replace with real data)
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
    hours = list(range(24))
    
    # Sample data - replace with real user activity data
    heatmap_data = []
    for date in dates:
        for hour in hours:
            # Simulate activity based on time of day
            if 9 <= hour <= 17:  # Business hours
                activity = np.random.randint(5, 20)
            else:
                activity = np.random.randint(0, 5)
            heatmap_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Hour': hour,
                'Activity': activity
            })
    
    df_heatmap = pd.DataFrame(heatmap_data)
    pivot_heatmap = df_heatmap.pivot(index='Hour', columns='Date', values='Activity')
    
    fig_heatmap = px.imshow(
        pivot_heatmap,
        title="User Activity Heatmap (Hourly)",
        labels=dict(x="Date", y="Hour", color="Activity"),
        color_continuous_scale="Viridis"
    )
    
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Recent activity table
    st.markdown("### Recent Activity")
    
    # Sample recent activity data
    recent_activity = [
        {"Time": "2025-07-29 11:30", "User": "user@whf.com", "Action": "File Upload", "Details": "work_instruction.pdf"},
        {"Time": "2025-07-29 11:25", "User": "admin@whf.com", "Action": "Query", "Details": "What are the safety procedures?"},
        {"Time": "2025-07-29 11:20", "User": "user@whf.com", "Action": "Login", "Details": "Email login"},
        {"Time": "2025-07-29 11:15", "User": "admin@whf.com", "Action": "Export", "Details": "PDF export"},
        {"Time": "2025-07-29 11:10", "User": "user@whf.com", "Action": "Query", "Details": "How to operate the hammer?"}
    ]
    
    df_activity = pd.DataFrame(recent_activity)
    st.dataframe(df_activity, use_container_width=True)
    
else:
    st.error("❌ Unable to load analytics data. Please check if the backend is running.")
    
    # Show sample data for demo
    st.markdown("## 📊 Sample Analytics (Demo Mode)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", "1,247")
    with col2:
        st.metric("Unique Users", "45")
    with col3:
        st.metric("File Uploads", "89")
    with col4:
        st.metric("Queries", "1,158")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 20px;">
    <p>📊 WHF Analytics Dashboard | Powered by Forgia AI Assistant</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True) 