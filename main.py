import argparse
import os
import json
import time
from datetime import datetime
from src.config import Config
from src.droid_utils import DeviceController
from src.analyzer import DarknessAnalyzer
from src.navigator import NavigationAgent  # <--- IMPORT THIS

def run_dead_hand(prompt, max_steps):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(Config.RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    print(f"💀 Starting Dead Hand Operation: {run_id}")
    print(f"🎯 Target: {prompt}")

    device = DeviceController()
    analyzer = DarknessAnalyzer()
    navigator = NavigationAgent() # <--- INITIALIZE NAVIGATOR
    
    report = {
        "id": run_id,
        "prompt": prompt,
        "start_time": str(datetime.now()),
        "steps": []
    }

    for i in range(1, max_steps + 1):
        print(f"\n--- Step {i}/{max_steps} ---")
        
        # 1. Capture State
        screenshot_path = device.capture_screen(run_dir, i)
        print(f"📸 Screenshot saved.")

        # 2. Analyze for Dark Patterns
        print("🕵️ Analyzing UI...")
        analysis_json = analyzer.analyze_step(screenshot_path, prompt)
        analysis_data = json.loads(analysis_json)
        
        # 3. Decide Next Action (Navigation)
        print("🧠 Planning next move...")
        action_data = navigator.get_next_action(screenshot_path, prompt, report['steps'])
        
        # Log everything
        step_record = {
            "step": i,
            "screenshot": screenshot_path,
            "analysis": analysis_data,
            "action": action_data
        }
        report["steps"].append(step_record)
        
        # Save Log
        with open(os.path.join(run_dir, "report.json"), "w") as f:
            json.dump(report, f, indent=4)

        # 4. EXECUTE MOVE
        device.execute_action(action_data)

    print(f"\n✅ Mission Complete.")
    print(f"📊 Run 'streamlit run dashboard.py' to view results.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=str)
    parser.add_argument("--steps", type=int, default=10)
    args = parser.parse_args()
    
    run_dead_hand(args.prompt, args.steps)