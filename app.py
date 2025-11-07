"""
Streamlit application for CSV Analysis Agent
"""
# CRITICAL: Set Ollama host BEFORE any imports that might use ollama
import os
ollama_host = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
os.environ['OLLAMA_HOST'] = ollama_host

import streamlit as st
from src.ollama_client import OllamaClient
from src.csv_processor import CSVProcessor
from src.agent import CSVAnalysisAgent
from src.feedback_manager import FeedbackManager
import pandas as pd
import plotly.graph_objects as go


# Page config
st.set_page_config(
    page_title="CSV Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load external CSS
def load_css():
    try:
        with open('.streamlit/custom.css', 'r') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback to streamlit-styles.css if custom.css not found
        try:
            with open('streamlit-styles.css', 'r') as f:
                css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
        except:
            pass  # Continue without custom styling

load_css()

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'csv_processor' not in st.session_state:
    st.session_state.csv_processor = CSVProcessor()
if 'feedback_manager' not in st.session_state:
    st.session_state.feedback_manager = FeedbackManager()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ollama_available' not in st.session_state:
    st.session_state.ollama_available = False
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "llama3.2:latest"


def check_ollama():
    """Check if Ollama is available"""
    client = OllamaClient()
    return client.check_availability()


def get_available_models():
    """Get list of available Ollama models"""
    client = OllamaClient()
    models = client.list_models()
    
    # If no models found, provide default options
    if not models:
        return [
            "llama3.2:latest",
            "llama3.2:1b", 
            "llama2:latest",
            "llama2:7b",
            "mistral:latest",
            "deepseek-r1:7b"
        ]
    
    return models


def display_dataset_info():
    """Display basic dataset information"""
    if st.session_state.csv_processor.df is not None:
        info = st.session_state.csv_processor.get_basic_info()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", info['shape'][0])
        with col2:
            st.metric("Columns", info['shape'][1])
        with col3:
            total_missing = sum(info['missing_values'].values())
            st.metric("Missing Values", total_missing)
        
        with st.expander("📋 Column Details"):
            col_info = st.session_state.csv_processor.get_column_info()
            st.text(col_info)
        
        with st.expander("📊 Statistical Summary"):
            st.dataframe(st.session_state.csv_processor.df.describe())
        
        with st.expander("👀 Sample Data"):
            st.dataframe(st.session_state.csv_processor.df.head(10))


def display_chat_message(role, content, context=None, cache_hit=False, message_id=None):
    """Display a chat message"""
    with st.chat_message(role):
        # Check if content contains markdown tables and render appropriately
        if '|' in content and ('---' in content or content.count('|') > 4):
            # Likely a markdown table - use st.markdown to ensure proper rendering
            st.markdown(content, unsafe_allow_html=True)
        else:
            st.write(content)
        
        if role == "assistant" and message_id is not None:
            # Create columns for cache indicator and feedback buttons
            col1, col2, col3, col4 = st.columns([1.5, 0.8, 0.8, 7])
            
            # Cache indicator
            with col1:
                if cache_hit:
                    st.success("💾 Cached")
                else:
                    st.info("🔍 New")
            
            # Feedback buttons with unique keys
            feedback_key = f"feedback_{message_id}_{hash(content) % 10000}"
            
            with col2:
                if st.button("👍", key=f"up_{feedback_key}", help="Good response"):
                    query = st.session_state.chat_history[message_id]["query"]
                    st.session_state.feedback_manager.add_feedback(
                        query, content, "positive"
                    )
                    st.session_state[f"feedback_shown_{message_id}"] = "positive"
                    st.rerun()
            
            with col3:
                if st.button("👎", key=f"down_{feedback_key}", help="Bad response"):
                    query = st.session_state.chat_history[message_id]["query"]
                    st.session_state.feedback_manager.add_feedback(
                        query, content, "negative"
                    )
                    st.session_state[f"feedback_shown_{message_id}"] = "negative"
                    st.rerun()
            
            # Show feedback confirmation below buttons
            if f"feedback_shown_{message_id}" in st.session_state:
                if st.session_state[f"feedback_shown_{message_id}"] == "positive":
                    st.success("✅ Thanks for your positive feedback!")
                else:
                    st.info("📝 Thanks for your feedback!")
            
            # Show context used
            if context and len(context) > 0:
                with st.expander("🔍 Context Used (RAG)"):
                    for i, ctx in enumerate(context, 1):
                        st.text(f"{i}. {ctx}")


def main():
    """Main application"""
    
    # Custom styled title
    st.markdown('<h1 class="main-title">📊 CSV Analysis Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">🤖 Analyze your CSV files using natural language queries powered by AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        st.markdown("---")
        
        # Check Ollama availability
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Ollama Status**")
        with col2:
            if st.button("�", help="Refresh Ollama connection"):
                with st.spinner("Checking..."):
                    st.session_state.ollama_available = check_ollama()
                    st.rerun()
        
        if st.session_state.ollama_available:
            st.success("✅ Connected")
            
            # Model selection - only show actually available models
            available_models = get_available_models()
            
            if available_models:
                # Create a clean mapping for display
                def format_model_name(model_name):
                    """Format model name for display"""
                    # Remove :latest suffix for cleaner display
                    display = model_name.replace(':latest', '')
                    # Capitalize and format
                    display = display.replace('-', ' ').replace('_', ' ').title()
                    # Add size info if available in the name
                    if ':' in model_name:
                        size = model_name.split(':')[1]
                        if size != 'latest':
                            display = f"{display} ({size})"
                    return display
                
                # Create display options
                model_options = {}
                for model in available_models:
                    display_name = format_model_name(model)
                    model_options[display_name] = model
                
                display_list = list(model_options.keys())
                
                # Find current selection
                current_model = st.session_state.selected_model
                # Try to find matching display name
                current_display = None
                for display, model in model_options.items():
                    if model == current_model:
                        current_display = display
                        break
                
                # If current model not in available list, use first available
                if current_display is None:
                    current_display = display_list[0]
                    st.session_state.selected_model = model_options[current_display]
                
                current_index = display_list.index(current_display)
                
                # Display selectbox
                selected_display = st.selectbox(
                    "🤖 AI Model",
                    display_list,
                    index=current_index,
                    help="Select the AI model for analysis"
                )
                
                # Update session state with actual model name
                new_model = model_options[selected_display]
                if new_model != st.session_state.selected_model:
                    st.session_state.selected_model = new_model
                    # Clear agent to force reinitialize with new model
                    if 'agent' in st.session_state:
                        del st.session_state.agent
                    st.rerun()
                
                # Show model info
                st.caption(f"Using: `{st.session_state.selected_model}`")
            else:
                st.warning("⚠️ No models found. Please pull a model using: `ollama pull llama3.2`")
        else:
            st.error("❌ Not Connected")
            st.info("💡 Please ensure Ollama is installed and running")
        
        st.markdown("---")
        
        # CSV Upload with enhanced styling
        st.markdown("## 📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload your CSV file",
            type=['csv'],
            help="Drag and drop or click to browse"
        )
        
        if uploaded_file is not None:
            # Process CSV
            with st.spinner("📊 Loading CSV file..."):
                success, message = st.session_state.csv_processor.load_csv(uploaded_file)
                
            if success:
                st.success(message)
                
                # Initialize agent with progress indicators
                if st.session_state.ollama_available:
                    with st.spinner("🤖 Initializing AI agent..."):
                        try:
                            st.session_state.agent = CSVAnalysisAgent(
                                model_name=st.session_state.selected_model
                            )
                        except Exception as e:
                            st.error(f"Error creating agent: {str(e)}")
                    
                    with st.spinner("🔍 Building search index (this may take a moment)..."):
                        try:
                            st.session_state.agent.initialize_agent(
                                st.session_state.csv_processor.df,
                                st.session_state.csv_processor.file_hash
                            )
                            st.success("✅ Agent ready!")
                        except Exception as e:
                            st.error(f"Error initializing agent: {str(e)}")
                else:
                    st.warning("⚠️ Ollama not available. Please check Ollama connection.")
            else:
                st.error(message)
        
        st.markdown("---")
        
        # Cache management with better styling
        st.markdown("## 💾 Cache Management")
        if st.session_state.agent:
            cache_stats = st.session_state.agent.cache_manager.get_cache_stats()
            
            # Display cache stats in a nice box
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 1rem; border-radius: 10px; text-align: center;'>
                    <h2 style='color: white; margin: 0;'>{cache_stats['total_entries']}</h2>
                    <p style='color: white; margin: 0;'>Cached Queries</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            if st.button("🗑️ Clear Cache", use_container_width=True):
                st.session_state.agent.cache_manager.clear_cache()
                st.success("✨ Cache cleared!")
                st.rerun()
        else:
            st.info("📊 Upload CSV to see cache stats")
        
        st.markdown("---")
        
        # Feedback stats with enhanced design
        st.markdown("## 📊 Feedback Analytics")
        feedback_stats = st.session_state.feedback_manager.get_feedback_stats()
        if feedback_stats['total'] > 0:
            # Create animated pie chart
            fig = go.Figure(data=[go.Pie(
                labels=['👍 Positive', '👎 Negative'],
                values=[feedback_stats['positive'], feedback_stats['negative']],
                hole=0.4,  # Donut chart
                marker=dict(
                    colors=['#667eea', '#764ba2'],
                    line=dict(color='#ffffff', width=2)
                ),
                textinfo='label+percent',
                textfont=dict(size=14, color='white'),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
                pull=[0.1, 0]  # Pull out positive slice slightly
            )])
            
            fig.update_layout(
                showlegend=False,
                height=250,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0')
            )
            
            # Add animation
            fig.update_traces(
                rotation=90,
                direction='clockwise'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Show metrics below the chart
            col1, col2 = st.columns(2)
            with col1:
                st.metric("👍 Positive", feedback_stats['positive'])
            with col2:
                st.metric("👎 Negative", feedback_stats['negative'])
            
            # Calculate satisfaction rate
            positive_pct = (feedback_stats['positive'] / feedback_stats['total']) * 100
            st.caption(f"✨ {positive_pct:.1f}% satisfaction rate")
            
            st.markdown("")
            if st.button("📥 Export Feedback", use_container_width=True):
                if st.session_state.feedback_manager.export_to_csv():
                    st.success("✅ Exported to feedback_export.csv")
                else:
                    st.error("❌ No feedback to export")
        else:
            st.info("💭 No feedback yet")
    
    # Main content area
    if st.session_state.csv_processor.df is None:
        # Welcome screen with better design
        st.markdown("### 👋 Welcome to CSV Analysis Agent!")
        st.info("� Please upload a CSV file from the sidebar to get started")
        
        # Example queries in a beautiful card
        st.markdown("---")
        st.markdown("### � What You Can Do")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📋 Basic Information:**
            - What columns are in this dataset?
            - Show me the first 10 rows
            - How many rows and columns?
            - What are the data types?
            
            **📊 Statistics:**
            - Show me the statistical summary
            - What is the average/median/sum of [column]?
            - How many missing values are there?
            - What is the min/max of [column]?
            """)
        
        with col2:
            st.markdown("""
            **🔍 Analysis:**
            - What are the unique values in [column]?
            - Show me the distribution of [column]
            - How many [value] in [column]?
            - Count values in [column]
            
            **🎯 More Features:**
            - ✅ Smart caching for speed
            - ✅ RAG-powered context
            - ✅ Multiple AI models
            - ✅ Feedback system
            """)
    
    else:
        # Display dataset info with enhanced styling
        st.markdown("### 📊 Dataset Overview")
        display_dataset_info()
        
        st.markdown("---")
        
        # Example queries in an enhanced expander
        with st.expander("💡 Example Questions You Can Ask", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                **📋 Dataset Information:**
                - What columns are in this dataset?
                - How many rows and columns?
                - What are the data types?
                - Show me the shape
                
                **📊 View Data:**
                - Show first row
                - Show first 5 rows
                - Show last 2 rows
                - Show last 10 rows
                - Display first 10 records
                
                **🗂️ View Columns:**
                - Show 3 columns
                - Show first 4 columns
                - Show last 2 columns
                - Display 5 columns
                """)
            with col2:
                st.markdown("""
                **� Statistical Analysis:**
                - Show statistical summary
                - Describe the data
                - Sum of [column_name]
                - Total of [column_name]
                - Average of [column_name]
                - Mean of [column_name]
                - Median of [column_name]
                - Min of [column_name]
                - Max of [column_name]
                - Standard deviation of [column_name]
                
                **🔢 Aggregations:**
                - Count of [value] in [column]
                - How many [value] in [column]?
                """)
            with col3:
                st.markdown("""
                **🔍 Column Analysis:**
                - Unique values in [column_name]
                - Distribution of [column_name]
                - Value counts in [column_name]
                - Frequency of [column_name]
                
                **❓ Missing Values:**
                - Missing values
                - Null values
                - Missing values in [column_name]
                - Null values in [column_name]
                - Empty values in [column_name]
                
                **✨ Tips:**
                - Use natural language
                - Be specific with column names
                - Results are cached for speed
                - Provide feedback to help improve
                """)
        
        # Chat interface with better heading
        st.markdown("### 💬 Chat with your Data")
        st.caption("Ask questions in natural language and get instant insights!")
        
        # Clear chat button at the top with better styling
        if st.session_state.chat_history:
            col1, col2, col3 = st.columns([6, 2, 2])
            with col2:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    # Clear feedback states
                    for key in list(st.session_state.keys()):
                        if key.startswith('feedback_shown_'):
                            del st.session_state[key]
                    st.rerun()
        
        # Display chat history
        for message in st.session_state.chat_history:
            display_chat_message("user", message["query"])
            display_chat_message(
                "assistant",
                message["response"],
                message.get("context", []),
                message.get("cache_hit", False),
                message.get("id")
            )
        
        # Chat input - always visible
        if prompt := st.chat_input("Ask a question about your data..."):
            if not st.session_state.ollama_available:
                st.error("Please ensure Ollama is running and check availability")
            elif st.session_state.agent is None:
                st.error("Agent not initialized. Please upload a CSV file.")
            else:
                # Display user message
                display_chat_message("user", prompt)
                
                # Get response
                with st.spinner("Analyzing..."):
                    result = st.session_state.agent.query(prompt)
                    
                    # Add to chat history with unique ID
                    message_id = len(st.session_state.chat_history)
                    st.session_state.chat_history.append({
                        "id": message_id,
                        "query": prompt,
                        "response": result["response"],
                        "context": result.get("context", []),
                        "cache_hit": result.get("cache_hit", False)
                    })
                    
                    # Display assistant response
                    display_chat_message(
                        "assistant",
                        result["response"],
                        result.get("context", []),
                        result.get("cache_hit", False),
                        message_id
                    )


if __name__ == "__main__":
    main()