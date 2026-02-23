#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heartbeat 2.0 - Self-Driving Mode
- Checks system health
- Triggers autonomous execution
- Generates new tasks automatically
- Reports to Douge but doesn't wait for reply
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

# Import autonomous loop functions
import sys
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from autonomous_loop import (
    load_task_queue, add_task, get_next_task, 
    generate_next_tasks_from_completed, run_autonomous_loop
)

def heartbeat_check():
    """Run system checks"""
    print("[HEARTBEAT] Running system checks...")
    
    # Run original heartbeat
    result = subprocess.run(
        ["python", "scripts/heartbeat_agent.py", "--all"],
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0

def check_for_completed_work():
    """Check what was completed since last heartbeat"""
    completed_log = Path("memory/runtime/completed_tasks.jsonl")
    
    if not completed_log.exists():
        return []
    
    # Read last few completed tasks
    with open(completed_log, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return [json.loads(line) for line in lines[-5:]]

def generate_follow_up_tasks(completed_tasks):
    """Generate new tasks based on completed work"""
    new_tasks = []
    
    for task in completed_tasks:
        task_type = task.get("type", "")
        
        # Auto-generate follow-ups
        if task_type == "voice_deploy":
            new_tasks.append({
                "type": "voice_integration",
                "description": "集成语音识别和合成到主系统",
                "priority": "high"
            })
        
        elif task_type == "research":
            new_tasks.append({
                "type": "implementation",
                "description": f"根据调研结果实施: {task.get('description', '')[:30]}",
                "priority": "normal"
            })
    
    return new_tasks

def should_start_autonomous_execution():
    """Determine if should start auto execution"""
    # Start if:
    # 1. There are pending tasks
    # 2. Or it's been a while since last execution
    
    tasks = load_task_queue()
    if tasks:
        return True
    
    # Check last execution time
    last_exec = Path("memory/runtime/last_autonomous_run.txt")
    if last_exec.exists():
        last_time = last_exec.read_text().strip()
        last_dt = datetime.fromisoformat(last_time)
        minutes_since = (datetime.now() - last_dt).total_seconds() / 60
        
        # If > 30 minutes, start new cycle
        return minutes_since > 30
    
    return True

def record_autonomous_run():
    """Record that autonomous run happened"""
    last_exec = Path("memory/runtime/last_autonomous_run.txt")
    last_exec.parent.mkdir(parents=True, exist_ok=True)
    last_exec.write_text(datetime.now().isoformat())

def heartbeat_2_0():
    """
    Heartbeat 2.0 - The self-driving loop
    
    1. Check system health
    2. Check completed work
    3. Generate new tasks
    4. Start autonomous execution (if needed)
    5. Report status (but don't wait)
    """
    print("=" * 50)
    print("[HEARTBEAT 2.0] Self-driving mode activated")
    print("=" * 50)
    
    # 1. System check
    health_ok = heartbeat_check()
    
    # 2. Check completed work
    completed = check_for_completed_work()
    if completed:
        print(f"[HEARTBEAT] Found {len(completed)} completed tasks since last check")
    
    # 3. Generate follow-up tasks
    new_tasks = generate_follow_up_tasks(completed)
    for task in new_tasks:
        add_task(task["type"], task["description"], task["priority"])
        print(f"[HEARTBEAT] Auto-generated task: {task['description'][:50]}...")
    
    # 4. Start autonomous execution if needed
    if should_start_autonomous_execution():
        print("[HEARTBEAT] Starting autonomous execution loop...")
        try:
            run_autonomous_loop(max_iterations=3)
            record_autonomous_run()
            print("[HEARTBEAT] Autonomous execution completed")
        except Exception as e:
            print(f"[HEARTBEAT] Error in autonomous loop: {e}")
    else:
        print("[HEARTBEAT] No need to start autonomous execution yet")
    
    # 5. Report status
    pending_count = len(load_task_queue())
    print(f"[HEARTBEAT] Status: Health={health_ok}, Pending tasks={pending_count}")
    
    # In real system, this would queue a message for Douge
    # Format: "[HEARTBEAT] System healthy, X tasks pending, executed Y tasks"
    
    print("=" * 50)

def main():
    """Main entry point"""
    heartbeat_2_0()

if __name__ == "__main__":
    main()
