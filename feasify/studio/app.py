"""Feasify Studio - AI Agent Interface for Non-Technical Users."""
import streamlit as st
import os
import json
from datetime import datetime
import time

st.set_page_config(
    page_title="Feasify Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0A9396;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6C757D;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #0A9396 0%, #1D3557 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0A9396 0%, #1D3557 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .status-success { color: #2D6A4F; }
    .status-warning { color: #E9C46A; }
    .status-error { color: #E76F51; }
</style>
""", unsafe_allow_html=True)


def check_api_keys():
    """Check if API keys are configured."""
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    return {
        "gemini": bool(google_key),
        "groq": bool(groq_key),
    }


def init_session_state():
    """Initialize Streamlit session state."""
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "current_project" not in st.session_state:
        st.session_state.current_project = {}


def run_swarm_analysis(
    cts_number: str,
    zone: str,
    road_width: float,
    use: str,
    plot_area: float,
    land_cost: float = 0,
    finish: str = "standard",
):
    """Run the Feasify Swarm analysis."""
    try:
        from feasify.swarm import FeasifySwarm
        
        swarm = FeasifySwarm()
        result = swarm.analyze(
            cts_number=cts_number,
            zone=zone,
            road_width_m=road_width,
            use=use,
            plot_area_sqm=plot_area,
            land_cost=land_cost,
        )
        return result
    except Exception as e:
        return {"error": str(e)}


def display_fsi_summary(fsi_data):
    """Display FSI analysis summary."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Base FSI", f"{fsi_data.get('base', 0):.2f}")
    with col2:
        st.metric("Premium FSI", f"{fsi_data.get('premium', 0):.2f}")
    with col3:
        st.metric("Total FSI", f"{fsi_data.get('total', 0):.2f}")
    with col4:
        st.metric("Max BUA (sq.m)", f"{fsi_data.get('max_buildable_sqm', 0):,.0f}")


def display_cost_summary(cost_data):
    """Display cost summary."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Cost", f"₹{cost_data.get('total', 0):,.0f}")
    with col2:
        st.metric("Cost/sq.ft", f"₹{cost_data.get('cost_per_sqft', 0):,.0f}")
    with col3:
        st.metric("Cost/sq.m", f"₹{cost_data.get('cost_per_sqm', 0):,.0f}")


def display_verdict(verdict: str, can_proceed: bool):
    """Display feasibility verdict."""
    if verdict == "VIABLE":
        st.success(f"✅ VERDICT: VIABLE - Project can proceed!")
    elif verdict == "MARGINAL":
        st.warning(f"⚠️ VERDICT: MARGINAL - Proceed with caution")
    elif verdict == "BLOCKED":
        st.error(f"❌ VERDICT: BLOCKED - Project has blocking issues")
    else:
        st.info(f"📋 VERDICT: {verdict}")


def main():
    init_session_state()
    
    # Header
    st.markdown('<p class="main-header">🏠 Feasify Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Real Estate Feasibility Analysis for Mumbai</p>', unsafe_allow_html=True)
    
    # Check API keys
    keys = check_api_keys()
    
    if not keys["gemini"] and not keys["groq"]:
        st.warning("""
        ### ⚠️ API Keys Not Configured
        
        Please set up your AI API key to start analyzing projects.
        
        Run the setup command:
        ```bash
        python -m feasify on boarding
        ```
        
        Or set environment variables manually:
        - `GOOGLE_API_KEY` (recommended - free tier)
        - `GROQ_API_KEY` (backup option)
        """)
        return
    
    # Main content
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("📋 Project Details")
        
        cts_number = st.text_input(
            "CTS Number",
            placeholder="e.g., 1234/567",
            help="Enter the CTS (Cadastral Survey Number) for the plot"
        )
        
        zone = st.selectbox(
            "Zone",
            options=["suburbs", "island_city", "extended_suburbs", "barc_area"],
            help="Mumbai zone classification"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            plot_area = st.number_input(
                "Plot Area (sq.m)",
                min_value=100,
                max_value=100000,
                value=1000,
                help="Total plot area in square meters"
            )
        with col_b:
            road_width = st.number_input(
                "Road Width (m)",
                min_value=3.0,
                max_value=100.0,
                value=12.0,
                help="Width of access road in meters"
            )
        
        use = st.selectbox(
            "Building Use",
            options=["residential", "commercial", "industrial"],
            help="Intended use of the building"
        )
        
        col_c, col_d = st.columns(2)
        with col_c:
            land_cost = st.number_input(
                "Land Cost (₹)",
                min_value=0,
                value=0,
                help="Purchase price of the land (optional)"
            )
        with col_d:
            finish = st.selectbox(
                "Finish Grade",
                options=["basic", "standard", "premium"],
                help="Construction quality level"
            )
        
        analyze_button = st.button("🔍 Analyze Feasibility", type="primary", use_container_width=True)
    
    with col_right:
        if analyze_button and cts_number:
            with st.spinner("🤖 Running AI analysis..."):
                result = run_swarm_analysis(
                    cts_number=cts_number,
                    zone=zone,
                    road_width=road_width,
                    use=use,
                    plot_area=plot_area,
                    land_cost=land_cost,
                    finish=finish,
                )
                
                st.session_state.analysis_results = result
                st.session_state.analysis_history.append({
                    "cts": cts_number,
                    "zone": zone,
                    "timestamp": datetime.now(),
                    "verdict": result.get("verdict", "UNKNOWN")
                })
        
        if st.session_state.analysis_results:
            result = st.session_state.analysis_results
            
            if "error" in result:
                st.error(f"Analysis failed: {result['error']}")
            else:
                display_verdict(
                    result.get("verdict", "UNKNOWN"),
                    result.get("can_proceed", False)
                )
                
                # Tabs for detailed results
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📐 FSI Analysis",
                    "💰 Cost Analysis", 
                    "⚠️ Risks",
                    "📊 Full Report"
                ])
                
                with tab1:
                    fsi = result.get("fsi_summary", {})
                    if fsi:
                        display_fsi_summary(fsi)
                        
                        st.markdown("### FSI Breakdown")
                        st.bar_chart({
                            "Base": [fsi.get("base", 0)],
                            "Premium": [fsi.get("premium", 0)],
                            "TDR": [fsi.get("tdr", 0)],
                            "Fungible": [fsi.get("fungible", 0)],
                        })
                        
                        st.markdown(f"""
                        **Max Buildable Area:** {fsi.get('max_buildable_sqm', 0):,.0f} sq.m  
                        **Saleable Area:** {fsi.get('saleable_sqm', 0):,.0f} sq.m
                        """)
                
                with tab2:
                    cost = result.get("cost_summary", {})
                    if cost:
                        display_cost_summary(cost)
                        
                        ratios = result.get("feasibility_ratios", {})
                        if ratios:
                            st.markdown("### Feasibility Ratios")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Gross Margin", f"{ratios.get('gross_margin_pct', 0):.1f}%")
                            with col2:
                                st.metric("ROI", f"{ratios.get('roi_pct', 0):.1f}%")
                            with col3:
                                st.metric("Breakeven", f"₹{ratios.get('breakeven_rate_sqft', 0):,.0f}/sqft")
                
                with tab3:
                    risks = result.get("risk_manifest", [])
                    blockers = result.get("blockers", [])
                    
                    if blockers:
                        st.error("### 🚫 Blocking Issues")
                        for b in blockers:
                            st.markdown(f"- **{b.get('type')}**: {b.get('description')}")
                            st.markdown(f"  Action: {b.get('recommended_action', 'N/A')}")
                    
                    if risks:
                        st.warning("### ⚠️ Risk Assessment")
                        for r in risks:
                            sev = r.get("severity", "LOW")
                            emoji = {"BLOCKER": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
                            st.markdown(f"{emoji} **{r.get('check')}** ({sev}): {r.get('description')}")
                
                with tab4:
                    st.json(result)
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Quick Guide")
        
        st.markdown("""
        **How to use Feasify:**
        
        1. Enter the CTS Number from your property documents
        2. Select the Mumbai zone
        3. Enter plot area and road width
        4. Choose building use type
        5. Click "Analyze Feasibility"
        
        **Understanding Results:**
        - ✅ **VIABLE**: Good project, proceed
        - ⚠️ **MARGINAL**: Proceed with caution
        - ❌ **BLOCKED**: Fix issues first
        """)
        
        st.divider()
        
        st.subheader("📜 Recent Analysis")
        for item in st.session_state.analysis_history[-5:]:
            ts = item["timestamp"].strftime("%H:%M")
            verdict_emoji = {"VIABLE": "✅", "MARGINAL": "⚠️", "BLOCKED": "❌"}.get(item["verdict"], "📋")
            st.markdown(f"{verdict_emoji} `{item['cts']}` - {ts}")
        
        st.divider()
        
        st.caption(f"Powered by Gemini AI • {datetime.now().strftime('%Y')}")


if __name__ == "__main__":
    main()