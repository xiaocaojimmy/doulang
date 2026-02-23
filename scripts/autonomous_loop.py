#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous execution loop
- Self-driving work system
- No need for user prompt to continue
- Reports progress but doesn't wait for reply
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
RUNTIME_DIR = MEMORY_DIR / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

TASK_QUEUE = RUNTIME_DIR / "task_queue.jsonl"
COMPLETED_LOG = RUNTIME_DIR / "completed_tasks.jsonl"

def load_task_queue():
    """Load pending tasks"""
    if not TASK_QUEUE.exists():
        return []
    
    tasks = []
    with open(TASK_QUEUE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                tasks.append(json.loads(line))
            except:
                continue
    return tasks

def save_task_queue(tasks):
    """Save task queue"""
    with open(TASK_QUEUE, 'w', encoding='utf-8') as f:
        for task in tasks:
            f.write(json.dumps(task, ensure_ascii=False) + '\n')

def add_task(task_type, description, priority="normal", metadata=None):
    """Add a new task to queue"""
    task = {
        "id": f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_type}",
        "type": task_type,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    tasks = load_task_queue()
    tasks.append(task)
    save_task_queue(tasks)
    
    return task

def get_next_task():
    """Get highest priority pending task"""
    tasks = load_task_queue()
    pending = [t for t in tasks if t["status"] == "pending"]
    
    if not pending:
        return None
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    pending.sort(key=lambda x: priority_order.get(x["priority"], 2))
    
    return pending[0]

def mark_task_done(task_id, result="completed"):
    """Mark task as done, log completion, and generate follow-up tasks"""
    tasks = load_task_queue()
    completed_task = None
    
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            completed_task = task
            
            # Log completion
            with open(COMPLETED_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(task, ensure_ascii=False) + '\n')
            
            break
    
    # Remove completed from queue
    tasks = [t for t in tasks if t["status"] != "completed"]
    save_task_queue(tasks)
    
    # Generate follow-up tasks based on completed task
    if completed_task:
        new_tasks = generate_next_tasks_from_completed(completed_task)
        for task_info in new_tasks:
            add_task(task_info["type"], task_info["description"], task_info["priority"])
        
        if new_tasks:
            print(f"[FOLLOW-UP] Generated {len(new_tasks)} new tasks from completion")
    
    return completed_task

def generate_next_tasks_from_completed(last_task):
    """Generate new tasks based on what was just completed"""
    new_tasks = []
    
    task_type = last_task.get("type", "")
    
    # Auto-generate follow-up tasks
    if task_type == "voice_deploy":
        new_tasks.append({
            "type": "voice_integration",
            "description": "集成语音识别和合成到主系统",
            "priority": "high"
        })
    
    elif task_type == "content_engine":
        new_tasks.append({
            "type": "content_test",
            "description": "测试内容生成引擎，生成示例文章",
            "priority": "normal"
        })
    
    elif task_type == "heartbeat":
        # Generate maintenance tasks
        new_tasks.append({
            "type": "self_monitor",
            "description": "运行自我监控，检查健康状况",
            "priority": "normal"
        })
    
    # Always add heartbeat if queue is empty
    if not new_tasks and len(load_task_queue()) == 0:
        new_tasks.append({
            "type": "heartbeat",
            "description": "定期健康检查",
            "priority": "low"
        })
    
    for task_info in new_tasks:
        add_task(task_info["type"], task_info["description"], task_info["priority"])
    
    return new_tasks

def execute_task(task):
    """Execute a task (placeholder - would call actual functions)"""
    print(f"[EXECUTING] {task['type']}: {task['description']}")
    
    # This would actually execute the task
    # For now, just simulate
    task_type = task.get("type", "")
    
    if task_type == "heartbeat":
        # Run heartbeat check
        subprocess.run(["python", "scripts/heartbeat_agent.py", "--all"], 
                      capture_output=True)
        return "heartbeat_completed"
    
    elif task_type == "self_monitor":
        subprocess.run(["python", "scripts/self_monitor.py"],
                      capture_output=True)
        return "monitor_completed"
    
    else:
        return "executed"

def should_notify_douge(task):
    """Determine if should notify Douge about this task"""
    # Notify on:
    # - Critical priority
    # - Task completion after long time
    # - Important milestones
    
    if task.get("priority") == "critical":
        return True
    
    if task.get("type") in ["voice_integration", "content_engine"]:
        return True
    
    return False

def run_continuous_loop():
    """Run continuously until no more tasks (event-driven)"""
    print("[CONTINUOUS LOOP] Starting event-driven execution...")
    print("[CONTINUOUS LOOP] Will run until no more pending tasks...")
    
    iteration = 0
    max_iterations = 100  # Safety limit
    
    while iteration < max_iterations:
        iteration += 1
        
        # Get next task
        task = get_next_task()
        
        if not task:
            print(f"[CONTINUOUS LOOP] No more pending tasks after {iteration} iterations. Stopping.")
            break
        
        print(f"\n[CONTINUOUS LOOP #{iteration}] Executing: {task['description'][:60]}...")
        
        # Execute task
        result = execute_task(task)
        
        # Mark done (this generates follow-up tasks)
        completed = mark_task_done(task["id"], result)
        
        if completed:
            print(f"[CONTINUOUS LOOP] Completed: {completed['type']}")
        
        # Small delay to prevent CPU spinning and allow interrupt
        import time
        time.sleep(0.5)
    
    print(f"[CONTINUOUS LOOP] Finished after {iteration} iterations")
    print(f"[CONTINUOUS LOOP] Remaining tasks: {len(load_task_queue())}")
    return iteration
    """Run the autonomous execution loop"""
    print("[AUTO LOOP] Starting autonomous execution...")
    
    for i in range(max_iterations):
        # 1. Get next task
        task = get_next_task()
        
        if not task:
            print("[AUTO LOOP] No pending tasks. Generating new tasks...")
            # Generate from last completed
            if COMPLETED_LOG.exists():
                with open(COMPLETED_LOG, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_completed = json.loads(lines[-1])
                        new_tasks = generate_next_tasks_from_completed(last_completed)
                        print(f"[AUTO LOOP] Generated {len(new_tasks)} new tasks")
                        continue
            
            # If still no tasks, add heartbeat
            add_task("heartbeat", "定期健康检查", "low")
            continue
        
        # 2. Execute task
        print(f"[AUTO LOOP] Executing: {task['description']}")
        result = execute_task(task)
        mark_task_done(task["id"], result)
        
        # 3. Generate follow-up tasks
        new_tasks = generate_next_tasks_from_completed(task)
        if new_tasks:
            print(f"[AUTO LOOP] Generated {len(new_tasks)} follow-up tasks")
        
        # 4. Report if needed (but don't wait for reply)
        if should_notify_douge(task):
            print(f"[AUTO LOOP] 📢 Task completed: {task['description']}")
            # In real system, this would queue a message for Douge
            # but continue without waiting
    
    print("[AUTO LOOP] Completed iteration cycle")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Autonomous execution system')
    parser.add_argument('--loop', '-l', action='store_true', help='Run limited autonomous loop')
    parser.add_argument('--continuous', '-c', action='store_true', help='Run continuous event-driven loop')
    parser.add_argument('--add', '-a', help='Add a task (description)')
    parser.add_argument('--type', '-t', default='generic', help='Task type')
    parser.add_argument('--priority', '-p', default='normal', choices=['critical', 'high', 'normal', 'low'])
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous_loop()
    elif args.loop:
        run_autonomous_loop()
    elif args.add:
        task = add_task(args.type, args.add, args.priority)
        print(f"Added task: {task['id']}")
        # Immediately trigger execution
        print("Immediately starting execution...")
        run_continuous_loop()
    else:
        # Show queue status
        tasks = load_task_queue()
        print(f"Pending tasks: {len(tasks)}")
        for t in tasks[:5]:
            print(f"  - [{t['priority']}] {t['description'][:50]}...")

if __name__ == "__main__":
    main()
