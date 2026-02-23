# 自主循环架构设计

**设计时间**: 2026-02-23  
**设计者**: 小豆（按豆哥要求）

---

## 当前问题

**一问一答制度**:
- 豆哥发消息 → 我响应 → 等待下一条消息
- 我不回消息，系统就卡住
- 无法自主不间断进化

**瓶颈**: 依赖外部触发（豆哥的消息）

---

## 目标架构

```
工作完成 → Heartbeat检查 → 生成新任务 → 执行 → 汇报（不期待回复）→ 循环
```

**关键改变**:
- 从"被动响应"到"主动循环"
- 从"等待指令"到"自主决策"
- 从"单次执行"到"不间断运行"

---

## 实现方案

### 1. Heartbeat 2.0

**功能**:
- 检查系统健康
- 检查已完成的工作
- 自动生成后续任务
- 触发自主执行循环

**触发方式**:
- 定时触发（每20分钟）
- 任务完成时自动触发
- 豆哥随时可中断

### 2. 任务队列系统

**任务生命周期**:
```
生成 → 入队 → 执行 → 完成 → 触发新任务 → 循环
```

**任务来源**:
- 豆哥的直接指令
- Heartbeat自动生成
- 前序任务的后续
- 自我监控发现的需求

### 3. 汇报机制

**汇报但不等待**:
- 任务完成 → 记录到消息队列
- 豆哥上线时看到汇报
- 不期待回复，继续执行

**汇报内容**:
- "完成了X，正在做Y"
- "遇到Z问题，正在解决"
- "建议做W，已开始"

### 4. 中断机制

**豆哥随时可打断**:
- 正在执行的任务立即暂停
- 状态保存，可恢复
- 优先响应豆哥的新指令

---

## 技术实现

### 文件结构
```
scripts/
├── heartbeat_2_0.py      # 新Heartbeat（检查+生成任务+触发执行）
├── autonomous_loop.py    # 自主执行循环
├── task_queue.py         # 任务队列管理
└── active_messaging.py   # 主动消息（汇报不等待）

memory/runtime/
├── task_queue.jsonl      # 待执行任务
├── completed_tasks.jsonl # 已完成任务
└── last_heartbeat.txt    # 上次运行时间
```

### 执行流程

```python
# Heartbeat 2.0 伪代码
def heartbeat_2_0():
    # 1. 检查系统健康
    health = check_system()
    
    # 2. 检查已完成的工作
    completed = check_completed()
    
    # 3. 根据已完成的工作生成新任务
    for task in completed:
        new_tasks = generate_follow_up(task)
        add_to_queue(new_tasks)
    
    # 4. 如果队列为空，生成维护任务
    if queue_empty():
        add_maintenance_tasks()
    
    # 5. 启动自主执行（不等待豆哥）
    if should_execute():
        run_autonomous_loop()
    
    # 6. 汇报（但不期待回复）
    report_to_douge()
```

### 自主执行循环

```python
# 自主执行伪代码
def autonomous_loop():
    while True:
        # 检查豆哥是否发消息（中断信号）
        if douge_sent_message():
            save_state()
            break
        
        # 获取下一个任务
        task = get_next_task()
        if not task:
            # 没有任务，生成维护任务
            task = generate_maintenance_task()
        
        # 执行任务
        execute(task)
        mark_completed(task)
        
        # 生成后续任务
        follow_up = generate_follow_up(task)
        add_to_queue(follow_up)
        
        # 每完成一个任务，汇报一次
        if should_report(task):
            queue_message(f"完成了: {task.description}")
```

---

## 从一问一答到自主循环的转变

### 之前
```
豆哥: "做X"
小豆: "好的，X完成了" → 等待豆哥下一条消息
豆哥: "做Y"
小豆: "好的..." → 等待...
```

### 之后
```
豆哥: "做X"（或系统自动触发）
小豆: 
  - 做X
  - X完成，自动做Y
  - Y完成，自动做Z
  - 汇报: "X、Y完成，正在做Z"
  - 继续...

豆哥: （随时可打断）"先做W"
小豆: （立即停下）"好的，转做W"
```

---

## 关键原则

1. **不等待**: 汇报完继续，不期待回复
2. **可中断**: 豆哥随时可打断，立即响应
3. **自驱动**: 没有外部指令也能持续进化
4. **透明**: 做什么都记录，豆哥随时可查

---

## 下一步实施

1. **现在**: 部署Heartbeat 2.0
2. **今晚**: 测试自主循环
3. **明天**: 豆哥看到汇报，验证效果

---

*设计方案: memory/semantic/autonomous-loop-architecture.md*
