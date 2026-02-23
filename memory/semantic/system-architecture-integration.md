# 系统架构说明 - Heartbeat与自主循环的关系

**文档时间**: 2026-02-23  
**状态**: 架构整合说明

---

## 现有系统

### 1. Heartbeat Agent (原系统)

**文件**:
- `HEARTBEAT.md` - 文档
- `heartbeat_agent.py` - 实施脚本
- `memory/procedural/heartbeat-guidelines.md` - 规则定义

**功能**:
- 系统健康检查（磁盘、内存、Gateway）
- 项目状态检查（小说进度、备份）
- 安全检查（配置、权限）
- 生成检查报告

**触发**: 每20分钟定时运行

**输出**: 检查报告（HEARTBEAT_OK / WARNING / CRITICAL）

### 2. 自主循环系统 (新系统)

**文件**:
- `scripts/autonomous_loop.py` - 任务执行引擎
- `scripts/heartbeat_2_0.py` - 循环触发器
- `.github/workflows/autonomous-loop.yml` - GitHub Actions

**功能**:
- 任务队列管理
- 事件驱动执行
- 自动生成后续任务
- 永不停歇的自我改进

**触发**: 事件驱动（任务完成即触发）

**输出**: 任务执行结果，新任务生成

---

## 冲突点

### 1. 命名冲突
- 两个系统都叫 "Heartbeat"
- 容易混淆

### 2. 功能边界模糊
- heartbeat_agent 生成检查任务
- heartbeat_2_0 也生成任务
- 可能重复或冲突

### 3. 调用关系
- heartbeat_2_0 调用了 heartbeat_agent
- 形成嵌套调用

---

## 整合方案

### 明确分工

```
┌─────────────────────────────────────────────────────────┐
│                    自主循环系统                           │
│              (Self-Driving Loop)                         │
├─────────────────────────────────────────────────────────┤
│  核心引擎: scripts/autonomous_loop.py                   │
│  - 任务队列管理                                          │
│  - 事件驱动执行                                          │
│  - 自动生成任务                                          │
│  - 永不停歇循环                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼ (调用)
┌─────────────────────────────────────────────────────────┐
│                   系统检查模块                           │
│              (System Check Module)                       │
├─────────────────────────────────────────────────────────┤
│  检查脚本: heartbeat_agent.py                           │
│  - 系统健康检查                                          │
│  - 项目状态检查                                          │
│  - 安全检查                                              │
│  - 生成检查结果                                          │
└─────────────────────────────────────────────────────────┘
```

### 重命名避免混淆

**建议重命名**:
- `heartbeat_2_0.py` → `self_driver.py` (自主驱动器)
- `HEARTBEAT.md` → `HEARTBEAT_CHECK.md` (明确是检查)

**保留**:
- `heartbeat_agent.py` (系统检查Agent)
- `autonomous_loop.py` (自主循环引擎)

### 调用关系

```python
# autonomous_loop.py 中
当需要系统检查时:
    result = subprocess.run(["python", "heartbeat_agent.py", "--all"])
    # 检查结果，生成后续任务

# 不通过 heartbeat_2_0/self_driver 间接调用
# 直接调用，避免嵌套
```

---

## 实施计划

### 立即执行
1. 重命名 heartbeat_2_0.py → self_driver.py
2. 更新 GitHub Actions 引用
3. 修改 autonomous_loop.py，直接调用 heartbeat_agent

### 文档更新
1. 更新 HEARTBEAT.md，明确说明这是"系统检查"
2. 创建 SELF_DRIVING.md，说明自主循环系统
3. 在 README 中说明两个系统的关系

---

## 当前状态

**已部署但需整合**:
- ✅ heartbeat_agent.py (系统检查)
- ✅ autonomous_loop.py (任务执行)
- ✅ heartbeat_2_0.py (需重命名)
- ⚠️ 命名和调用关系需理清

**下一步**: 立即执行整合

---

*记录位置: memory/semantic/system-architecture-integration.md*
