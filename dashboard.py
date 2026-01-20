import streamlit as st
import json
import os
import glob
from PIL import Image

st.set_page_config(layout="wide", page_title="Dead Hand Dashboard")

st.title("💀 Dead Hand: Dark Pattern Detective")

# Load Runs
runs_dir = os.path.join(os.getcwd(), "data", "runs")
if not os.path.exists(runs_dir):
    st.error(f"No runs found in {runs_dir}")
    st.stop()

# Select Run
run_folders = sorted(os.listdir(runs_dir), reverse=True)
selected_run = st.sidebar.selectbox("Select Mission", run_folders)

if selected_run:
    run_path = os.path.join(runs_dir, selected_run)
    report_path = os.path.join(run_path, "report.json")
    
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
            
        st.header(f"Mission: {data['prompt']}")
        st.caption(f"ID: {data['id']} | Started: {data['start_time']}")
        
        # Calculate Average Darkness
        scores = [s['analysis']['darkness_score'] for s in data['steps']]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Steps", len(data['steps']))
        col2.metric("Avg Darkness Score", f"{avg_score:.1f}/10")
        col3.metric("High Risk Screens", sum(1 for s in scores if s > 7))

        st.divider()

        # Display Steps
        for step in data['steps']:
            with st.container():
                st.subheader(f"Step {step['step']}")
                
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    img_path = step['screenshot']
                    if os.path.exists(img_path):
                        image = Image.open(img_path)
                        st.image(image, caption="Screen Capture", use_container_width=True)
                
                with c2:
                    analysis = step['analysis']
                    score = analysis.get('darkness_score', 0)
                    
                    # Color code the score
                    color = "green" if score < 4 else "orange" if score < 7 else "red"
                    st.markdown(f"### Darkness Score: :{color}[{score}/10]")
                    
                    st.markdown("**Detected Patterns:**")
                    for pat in analysis.get('detected_patterns', []):
                        st.markdown(f"- 🔴 {pat}")
                        
                    st.markdown("**Reasoning:**")
                    st.info(analysis.get('reasoning'))

    else:
        st.warning("Report file not found for this run.")