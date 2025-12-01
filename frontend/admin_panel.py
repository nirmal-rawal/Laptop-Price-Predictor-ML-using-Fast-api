import streamlit as st
import requests
import pandas as pd
from typing import Dict, List
import json

# Configure the page
st.set_page_config(
    page_title="Laptop Price Predictor - Admin Panel",
    page_icon="⚙️",
    layout="wide"
)

class AdminPanel:
    def __init__(self):
        self.api_base_url = "http://localhost:8000/api/v1"
        self.admin_base_url = f"{self.api_base_url}/admin"
    
    def check_api_health(self) -> bool:
        """Check if the FastAPI backend is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def render_sidebar(self):
        """Render admin sidebar"""
        st.sidebar.title("⚙️ Admin Panel")
        st.sidebar.markdown("---")
        
        if self.check_api_health():
            st.sidebar.success(" API Connected")
        else:
            st.sidebar.error("API Not Connected")
        
        st.sidebar.markdown("### 📊 Quick Stats")
        
        try:
            # Get predictions count
            count_response = requests.get(f"{self.admin_base_url}/stats/count", timeout=5)
            if count_response.status_code == 200:
                count_data = count_response.json()
                st.sidebar.metric("Total Predictions", count_data.get('total_predictions', 0))
            
            # Get companies stats
            companies_response = requests.get(f"{self.admin_base_url}/stats/companies", timeout=5)
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                if companies_data:
                    st.sidebar.metric("Companies", len(companies_data))
        
        except Exception as e:
            st.sidebar.error("Could not load stats")
    
    def render_predictions_view(self):
        """View all predictions"""
        st.header("📋 All Predictions")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            limit = st.number_input("Records Limit", min_value=10, max_value=1000, value=100)
        
        try:
            response = requests.get(f"{self.admin_base_url}/predictions?limit={limit}", timeout=10)
            if response.status_code == 200:
                predictions = response.json()
                
                if predictions:
                    # Convert to DataFrame for display
                    df_data = []
                    for pred in predictions:
                        df_data.append({
                            'Prediction ID': pred['prediction_id'][:8] + '...',
                            'Company': pred['input_features']['company'],
                            'Type': pred['input_features']['type_name'],
                            'RAM': f"{pred['input_features']['ram']} GB",
                            'Price': pred['price_formatted'],
                            'Timestamp': pred['timestamp'][:19]
                        })
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show detailed view
                    st.subheader("🔍 Detailed View")
                    selected_idx = st.selectbox("Select a prediction to view details:", range(len(predictions)), 
                                              format_func=lambda x: f"{predictions[x]['prediction_id'][:8]}... - {predictions[x]['input_features']['company']} {predictions[x]['input_features']['type_name']}")
                    
                    if selected_idx is not None:
                        pred = predictions[selected_idx]
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.json(pred)
                        
                        with col2:
                            # Delete option
                            if st.button("🗑️ Delete This Prediction", type="secondary"):
                                if self.delete_prediction(pred['prediction_id']):
                                    st.success("Prediction deleted successfully!")
                                    st.rerun()
                else:
                    st.info("No predictions found in the database.")
            
            else:
                st.error("Failed to fetch predictions")
        
        except Exception as e:
            st.error(f"Error fetching predictions: {e}")
    
    def render_search_predictions(self):
        """Search predictions"""
        st.header("🔍 Search Predictions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company = st.selectbox("Company", 
                                 options=["", "Apple", "Dell", "HP", "Asus", "Acer", "Lenovo", "MSI"])
            min_price = st.number_input("Minimum Price", min_value=0, value=0)
        
        with col2:
            search_type = st.selectbox("Search Type", ["All", "By Company", "By Price Range"])
            max_price = st.number_input("Maximum Price", min_value=0, value=1000000)
        
        if st.button("Search", type="primary"):
            try:
                if search_type == "By Company" and company:
                    response = requests.get(f"{self.admin_base_url}/predictions/company/{company}?limit=100", timeout=10)
                elif search_type == "By Price Range":
                    response = requests.get(
                        f"{self.admin_base_url}/predictions/price-range?min_price={min_price}&max_price={max_price}&limit=100", 
                        timeout=10
                    )
                else:
                    response = requests.get(f"{self.admin_base_url}/predictions?limit=100", timeout=10)
                
                if response.status_code == 200:
                    predictions = response.json()
                    st.success(f"Found {len(predictions)} predictions")
                    
                    # Display results
                    if predictions:
                        df_data = []
                        for pred in predictions:
                            df_data.append({
                                'Prediction ID': pred['prediction_id'],
                                'Company': pred['input_features']['company'],
                                'Type': pred['input_features']['type_name'],
                                'RAM': f"{pred['input_features']['ram']} GB",
                                'Price': pred['price_formatted'],
                                'Timestamp': pred['timestamp'][:19]
                            })
                        
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)
                
                else:
                    st.error("Search failed")
            
            except Exception as e:
                st.error(f"Search error: {e}")
    
    def render_statistics(self):
        """Display statistics"""
        st.header("📊 Statistics")
        
        try:
            # Overall statistics
            price_stats_response = requests.get(f"{self.admin_base_url}/stats/price", timeout=5)
            companies_stats_response = requests.get(f"{self.admin_base_url}/stats/companies", timeout=5)
            
            if price_stats_response.status_code == 200:
                price_stats = price_stats_response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Predictions", price_stats.get('total_predictions', 0))
                with col2:
                    st.metric("Average Price", f"₹{price_stats.get('average_price', 0):,}")
                with col3:
                    st.metric("Min Price", f"₹{price_stats.get('min_price', 0):,}")
                with col4:
                    st.metric("Max Price", f"₹{price_stats.get('max_price', 0):,}")
            
            if companies_stats_response.status_code == 200:
                companies_stats = companies_stats_response.json()
                
                st.subheader("📈 Company-wise Statistics")
                
                if companies_stats:
                    # Create chart data
                    companies_df = pd.DataFrame(companies_stats)
                    st.dataframe(companies_df, use_container_width=True)
                    
                    # Bar chart for company counts
                    import plotly.express as px
                    fig = px.bar(
                        companies_df,
                        x='company',
                        y='count',
                        title='Predictions by Company',
                        color='count'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
    
    def render_cleanup(self):
        """Cleanup operations"""
        st.header("🧹 Cleanup Operations")
        
        st.warning("⚠️ These operations are destructive and cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Delete by Company")
            company_to_delete = st.selectbox("Select Company to Delete", 
                                           options=["Apple", "Dell", "HP", "Asus", "Acer", "Lenovo", "MSI"])
            
            if st.button("Delete Company Predictions", type="secondary"):
                try:
                    response = requests.delete(f"{self.admin_base_url}/predictions/company/{company_to_delete}", timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Deleted {result['deleted_count']} predictions for {company_to_delete}")
                    else:
                        st.error("Delete operation failed")
                except Exception as e:
                    st.error(f"Delete error: {e}")
        
        with col2:
            st.subheader("Delete Old Predictions")
            days_old = st.slider("Delete predictions older than (days)", 1, 365, 30)
            
            if st.button("Delete Old Predictions", type="secondary"):
                try:
                    response = requests.delete(f"{self.admin_base_url}/predictions/cleanup/old?days_old={days_old}", timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Deleted {result['deleted_count']} predictions older than {days_old} days")
                    else:
                        st.error("Delete operation failed")
                except Exception as e:
                    st.error(f"Delete error: {e}")
    
    def delete_prediction(self, prediction_id: str) -> bool:
        """Delete a prediction"""
        try:
            response = requests.delete(f"{self.admin_base_url}/predictions/{prediction_id}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run(self):
        """Run the admin panel"""
        self.render_sidebar()
        
        if not self.check_api_health():
            st.error("Backend API is not connected. Please start the FastAPI server.")
            return
        
        # Admin tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 View Predictions", 
            "🔍 Search", 
            "📊 Statistics", 
            "🧹 Cleanup"
        ])
        
        with tab1:
            self.render_predictions_view()
        
        with tab2:
            self.render_search_predictions()
        
        with tab3:
            self.render_statistics()
        
        with tab4:
            self.render_cleanup()

# Run the admin panel
if __name__ == "__main__":
    admin = AdminPanel()
    admin.run()