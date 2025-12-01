import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="Laptop Price Predictor",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .feature-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
    }
    .price-display {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00cc96;
        text-align: center;
        margin: 1rem 0;
    }
    .price-comparison {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class LaptopPricePredictorFrontend:
    def __init__(self):
        self.api_base_url = "http://localhost:8000/api/v1"
        self.available_companies = [
            "Apple", "HP", "Acer", "Asus", "Dell", "Lenovo", 
            "MSI", "Toshiba", "Samsung", "Other"
        ]
        self.available_types = [
            "Ultrabook", "Notebook", "Netbook", "Gaming", 
            "2 in 1 Convertible", "Workstation"
        ]
        self.available_cpus = [
            "Intel Core i3", "Intel Core i5", "Intel Core i7", 
            "Intel Core i9", "AMD Processor", "Other Intel Processor"
        ]
        self.available_gpus = ["Intel", "AMD", "Nvidia"]
        self.available_os = ["Mac", "Windows", "Others/No OS/Linux"]

    def format_price(self, price: float) -> str:
        """Format price as Indian Rupees with proper comma separation"""
        try:
            # Handle both string and float inputs
            if isinstance(price, str):
                # Remove ₹ symbol if present and convert to float
                price = float(price.replace('₹', '').replace(',', ''))
            
            # Format with commas for thousands and two decimal places
            formatted = f"₹{price:,.2f}"
            return formatted
        except (ValueError, TypeError):
            # Fallback formatting
            return f"₹{price}"

    def check_api_health(self) -> bool:
        """Check if the FastAPI backend is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def make_prediction(self, features: Dict[str, Any]) -> Dict:
        """Make prediction through FastAPI"""
        try:
            response = requests.post(
                f"{self.api_base_url}/predict",
                json=features,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None

    def get_prediction_history(self) -> list:
        """Get prediction history from API"""
        try:
            response = requests.get(f"{self.api_base_url}/predictions?limit=50", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []

    def render_sidebar(self):
        """Render the sidebar with app information"""
        st.sidebar.title("💻 Laptop Price Predictor")
        st.sidebar.markdown("---")
        
        # API status
        if self.check_api_health():
            st.sidebar.success(" API Connected")
        else:
            st.sidebar.error(" API Not Connected")
            st.sidebar.info("Please ensure the FastAPI server is running on http://localhost:8000")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 About")
        st.sidebar.markdown("""
        This app predicts laptop prices based on specifications using machine learning.
        
        **Features:**
        -  Real-time price prediction
        - 📊 Price comparison
        - 💾 Prediction history
        - 📱 Responsive design
        
        **Backend:** FastAPI + Scikit-learn
        **Frontend:** Streamlit
        """)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🛠️ Developer")
        st.sidebar.markdown("""
        Built with ❤️ using:
        - Python
        - FastAPI
        - Streamlit
        - Scikit-learn
        - MongoDB
        """)

    def render_feature_input_form(self) -> Dict[str, Any]:
        """Render the feature input form"""
        st.markdown('<div class="main-header">💻 Laptop Price Predictor</div>', unsafe_allow_html=True)
        
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Basic Specifications")
            
            company = st.selectbox(
                "Manufacturer",
                options=self.available_companies,
                index=4,  # Default to Dell
                help="Select the laptop manufacturer"
            )
            
            type_name = st.selectbox(
                "Laptop Type",
                options=self.available_types,
                index=1,  # Default to Notebook
                help="Select the type of laptop"
            )
            
            ram = st.selectbox(
                "RAM (GB)",
                options=[2, 4, 6, 8, 12, 16, 24, 32, 64],
                index=3,  # Default to 8GB
                help="Select the amount of RAM"
            )
            
            weight = st.slider(
                "Weight (kg)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.1,
                help="Select the laptop weight"
            )
            
            ppi = st.slider(
                "Screen PPI (Pixels Per Inch)",
                min_value=90,
                max_value=400,
                value=141,
                step=1,
                help="Screen pixel density"
            )

        with col2:
            st.markdown("### ⚙️ Advanced Specifications")
            
            cpu_brand = st.selectbox(
                "Processor",
                options=self.available_cpus,
                index=1,  # Default to Intel Core i5
                help="Select the CPU model"
            )
            
            gpu_brand = st.selectbox(
                "Graphics Card",
                options=self.available_gpus,
                index=0,  # Default to Intel
                help="Select the GPU brand"
            )
            
            os = st.selectbox(
                "Operating System",
                options=self.available_os,
                index=1,  # Default to Windows
                help="Select the operating system"
            )
            
            # Storage options
            st.markdown("#### 💾 Storage Configuration")
            ssd = st.selectbox(
                "SSD Storage (GB)",
                options=[0, 128, 256, 512, 1024, 2048],
                index=2,  # Default to 256GB
                help="Select SSD storage capacity"
            )
            
            hdd = st.selectbox(
                "HDD Storage (GB)",
                options=[0, 500, 1000, 2000],
                index=0,  # Default to 0GB
                help="Select HDD storage capacity"
            )
            
            # Display options
            st.markdown("#### 🖥️ Display Features")
            col3, col4 = st.columns(2)
            with col3:
                touchscreen = st.checkbox("Touchscreen", value=False)
            with col4:
                ips = st.checkbox("IPS Display", value=True)

        # Prepare features dictionary
        features = {
            "company": company,
            "type_name": type_name,
            "ram": ram,
            "weight": weight,
            "touchscreen": 1 if touchscreen else 0,
            "ips": 1 if ips else 0,
            "ppi": float(ppi),
            "cpu_brand": cpu_brand,
            "hdd": hdd,
            "ssd": ssd,
            "gpu_brand": gpu_brand,
            "os": os
        }
        
        return features

    def render_prediction_result(self, prediction_data: Dict):
        """Render the prediction results"""
        if not prediction_data:
            return
        
        st.markdown("---")
        st.markdown("##  Prediction Results")
        
        # Price display card
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
            st.markdown("### Predicted Price")
            
            # Ensure proper price formatting
            price_display = prediction_data.get("price_formatted", "")
            if not price_display.startswith("₹") or "," not in price_display:
                # Reformat the price if needed
                raw_price = prediction_data.get("predicted_price", 0)
                price_display = self.format_price(raw_price)
            
            st.markdown(f'<div class="price-display">{price_display}</div>', unsafe_allow_html=True)
            st.markdown(f"**Prediction ID:** `{prediction_data['prediction_id']}`")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.metric("RAM", f"{prediction_data['features']['ram']} GB")
            st.metric("SSD", f"{prediction_data['features']['ssd']} GB")
        
        with col3:
            st.metric("HDD", f"{prediction_data['features']['hdd']} GB")
            st.metric("Weight", f"{prediction_data['features']['weight']} kg")
        
        # Feature summary
        st.markdown("### 📋 Configuration Summary")
        features = prediction_data['features']
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("**Basic Specs:**")
            st.write(f"- **Manufacturer:** {features['company']}")
            st.write(f"- **Type:** {features['type_name']}")
            st.write(f"- **Processor:** {features['cpu_brand']}")
            st.write(f"- **Graphics:** {features['gpu_brand']}")
        
        with col5:
            st.markdown("**Display & Storage:**")
            st.write(f"- **OS:** {features['os']}")
            st.write(f"- **Touchscreen:** {'Yes' if features['touchscreen'] else 'No'}")
            st.write(f"- **IPS Display:** {'Yes' if features['ips'] else 'No'}")
            st.write(f"- **Screen PPI:** {features['ppi']}")

    def render_price_comparison(self, current_prediction: Dict):
        """Render price comparison with common configurations"""
        st.markdown("---")
        st.markdown("## 📊 Price Comparison")
        
        # Common laptop configurations for comparison
        common_configs = [
            {
                "name": "Budget Laptop",
                "company": "Acer",
                "type_name": "Notebook",
                "ram": 4,
                "weight": 2.2,
                "touchscreen": 0,
                "ips": 0,
                "ppi": 120,
                "cpu_brand": "Intel Core i3",
                "hdd": 1000,
                "ssd": 0,
                "gpu_brand": "Intel",
                "os": "Windows"
            },
            {
                "name": "Mid-range Laptop",
                "company": "Dell",
                "type_name": "Notebook",
                "ram": 8,
                "weight": 2.0,
                "touchscreen": 0,
                "ips": 1,
                "ppi": 141,
                "cpu_brand": "Intel Core i5",
                "hdd": 0,
                "ssd": 256,
                "gpu_brand": "Intel",
                "os": "Windows"
            },
            {
                "name": "Gaming Laptop",
                "company": "Asus",
                "type_name": "Gaming",
                "ram": 16,
                "weight": 2.5,
                "touchscreen": 0,
                "ips": 1,
                "ppi": 141,
                "cpu_brand": "Intel Core i7",
                "hdd": 1000,
                "ssd": 512,
                "gpu_brand": "Nvidia",
                "os": "Windows"
            },
            {
                "name": "Apple MacBook",
                "company": "Apple",
                "type_name": "Ultrabook",
                "ram": 8,
                "weight": 1.3,
                "touchscreen": 0,
                "ips": 1,
                "ppi": 227,
                "cpu_brand": "Intel Core i5",
                "hdd": 0,
                "ssd": 256,
                "gpu_brand": "Intel",
                "os": "Mac"
            }
        ]
        
        # Add current configuration to comparison
        current_config = {
            "name": "Your Configuration",
            "company": current_prediction["features"]["company"],
            "type_name": current_prediction["features"]["type_name"],
            "ram": current_prediction["features"]["ram"],
            "weight": current_prediction["features"]["weight"],
            "touchscreen": current_prediction["features"]["touchscreen"],
            "ips": current_prediction["features"]["ips"],
            "ppi": current_prediction["features"]["ppi"],
            "cpu_brand": current_prediction["features"]["cpu_brand"],
            "hdd": current_prediction["features"]["hdd"],
            "ssd": current_prediction["features"]["ssd"],
            "gpu_brand": current_prediction["features"]["gpu_brand"],
            "os": current_prediction["features"]["os"]
        }
        
        all_configs = common_configs + [current_config]
        
        # Get predictions for all configs
        predictions = []
        for config in all_configs:
            try:
                result = self.make_prediction(config)
                if result:
                    # Ensure proper price formatting
                    price_display = result.get("price_formatted", "")
                    if not price_display.startswith("₹") or "," not in price_display:
                        raw_price = result.get("predicted_price", 0)
                        price_display = self.format_price(raw_price)
                    
                    predictions.append({
                        "name": config["name"],
                        "price": result["predicted_price"],
                        "formatted_price": price_display,
                        "is_current": config["name"] == "Your Configuration"
                    })
            except Exception as e:
                st.warning(f"Could not get prediction for {config['name']}: {e}")
                continue
        
        if len(predictions) > 1:
            # Create comparison chart
            df = pd.DataFrame(predictions)
            
            # Create bar chart
            fig = px.bar(
                df, 
                x='name', 
                y='price',
                title="Price Comparison: Laptop Configurations",
                labels={'name': 'Laptop Type', 'price': 'Price (₹)'},
                color='is_current',
                color_discrete_map={True: '#00cc96', False: '#1f77b4'},
                text='formatted_price'
            )
            
            fig.update_traces(
                texttemplate='%{text}',
                textposition='outside'
            )
            
            fig.update_layout(
                xaxis_title="Laptop Configuration",
                yaxis_title="Predicted Price (₹)",
                showlegend=False,
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display comparison table
            st.markdown("### 📋 Detailed Comparison")
            comparison_data = []
            for pred in predictions:
                comparison_data.append({
                    "Configuration": pred["name"],
                    "Predicted Price": pred["formatted_price"],
                    "Your Choice": " Yes" if pred["is_current"] else "No"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    def render_prediction_history(self):
        """Render prediction history"""
        st.markdown("---")
        st.markdown("## 📈 Prediction History")
        
        history = self.get_prediction_history()
        
        if history:
            # Convert to DataFrame for display
            history_data = []
            for record in history:
                # Format price properly
                price_display = record.get("price_formatted", "")
                if not price_display.startswith("₹") or "," not in price_display:
                    raw_price = record.get("output_prediction", 0)
                    price_display = self.format_price(raw_price)
                
                history_data.append({
                    "Prediction ID": record["prediction_id"][:8] + "...",
                    "Price": price_display,
                    "Company": record["input_features"]["company"],
                    "Type": record["input_features"]["type_name"],
                    "RAM": f"{record['input_features']['ram']} GB",
                    "Timestamp": record["timestamp"][:19]  # Truncate to remove milliseconds
                })
            
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True)
            
            # Price distribution chart
            prices = [float(record["output_prediction"]) for record in history]
            
            fig = px.histogram(
                x=prices,
                title="Price Distribution History",
                labels={"x": "Price (₹)", "y": "Frequency"},
                nbins=20
            )
            
            # Format x-axis with Indian Rupee format
            fig.update_layout(
                xaxis=dict(
                    tickformat=",",
                    tickprefix="₹"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No prediction history available. Make some predictions to see them here!")

    def run(self):
        """Main method to run the Streamlit app"""
        # Render sidebar
        self.render_sidebar()
        
        # Check API connection
        if not self.check_api_health():
            st.error("""
            ## Backend Not Connected
            
            Please ensure the FastAPI backend is running:
            ```bash
            uvicorn main:app --reload --host 0.0.0.0 --port 8000
            ```
            
            The backend should be accessible at: http://localhost:8000
            """)
            return
        
        # Render main content
        features = self.render_feature_input_form()
        
        # Prediction button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            predict_button = st.button(
                " Predict Price", 
                type="primary", 
                use_container_width=True,
                help="Click to predict the laptop price based on your specifications"
            )
        
        if predict_button:
            with st.spinner("🤖 Analyzing specifications and predicting price..."):
                prediction_data = self.make_prediction(features)
                
            if prediction_data:
                self.render_prediction_result(prediction_data)
                self.render_price_comparison(prediction_data)
                self.render_prediction_history()
        
        # Show sample configurations even without prediction
        else:
            st.info("💡 **Tip:** Configure your laptop specifications and click 'Predict Price' to see the estimated price.")

# Run the app
if __name__ == "__main__":
    app = LaptopPricePredictorFrontend()
    app.run()