"""
豆语优化版 - 基于FMS实验验证

核心优化：
1. 价值标签：identity(1.5) > preference(1.0) > fact(0.3)
2. 时间衰减：超过20轮的记忆权重降低
3. 伪装注入：检索结果伪装成对话上下文
4. 伦理守卫：防止时间定位编造
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import re

from .core import DouLang
from .llm import get_client


class MemoryType:
    """记忆类型（价值系统）"""
    IDENTITY = "identity"      # 权重 1.5 - 身份、职业
    PREFERENCE = "preference"  # 权重 1.0 - 喜好、风格
    CONTEXT = "context"        # 权重 1.2 - 当前项目
    FACT = "fact"              # 权重 0.3 - 一般事实


class DouLangEnhanced(DouLang):
    """
    豆语增强版 - 实验验证优化
    
    新增优化：
    - A. 类型感知注入：根据查询类型只注入相关记忆
    - B. 全局存储上限：自动清理旧记忆
    """
    
    # FMS实验确定的参数
    ADHESION_WINDOW = 20       # 20轮内有效（保守设置）
    IDENTITY_WEIGHT = 1.5
    PREFERENCE_WEIGHT = 1.0
    CONTEXT_WEIGHT = 1.2
    FACT_WEIGHT = 0.3
    
    # B. 全局存储上限参数
    MAX_MEMORIES = 100         # 总记忆数上限
    MAX_IDENTITY = 5           # 身份信息上限
    MAX_PREFERENCE = 10        # 偏好上限
    MAX_FACT = 50              # 事实上限
    
    def __init__(self, data_dir=None, ollama_host=None):
        super().__init__(data_dir, ollama_host)
        self.session_round = 0   # 会话轮次计数
    
    def remember_with_type(self, content: str, memory_type: str = None, 
                          source=None, timestamp=None) -> str:
        """
        存储记忆（带价值标签）
        
        新增：C. 智能更新机制
        - 检测更新信号（'其实'、'不再'、'现在'）
        - 自动替换同类型旧记忆
        """
        # 自动检测类型（如果未提供）
        if not memory_type:
            memory_type = self._detect_memory_type(content)
        
        # C. 检测是否为更新操作
        is_update = self._detect_update_signal(content)
        if is_update:
            # 找到并删除同类型的旧记忆
            self._update_replace_old(memory_type, content)
        
        # B. 检查存储上限，必要时清理
        self._enforce_storage_limits(memory_type)
        
        # 获取权重
        weight = self._get_type_weight(memory_type)
        
        # 将元数据编码到内容中
        tagged_content = f"[TYPE:{memory_type}|WEIGHT:{weight}] {content}"
        
        # 调用父类存储
        memory_id = self.remember(tagged_content, source, timestamp)
        
        return memory_id
    
    def _detect_update_signal(self, content: str) -> bool:
        """
        C. 检测更新信号
        
        返回True表示这是一个更新/替换操作
        """
        update_signals = [
            r"其实我是", r"其实我是",
            r"不再是", r"不再",
            r"现在我是", r"我现在",
            r"改", r"变成",
            r"更新", r"替换",
        ]
        
        for signal in update_signals:
            if signal in content:
                return True
        
        return False
    
    def _update_replace_old(self, memory_type: str, new_content: str):
        """
        C. 更新时替换旧记忆
        
        找到同类型的旧记忆并删除
        """
        try:
            all_memories = list(self.store._memory_cache.values())
            
            # 找到同类型的记忆
            same_type_mems = []
            for mem in all_memories:
                mem_content = mem.content if hasattr(mem, 'content') else ""
                _, mem_type, _ = self._extract_from_tagged(mem_content)
                
                if mem_type == memory_type:
                    mem_id = mem.id if hasattr(mem, 'id') else ""
                    same_type_mems.append(mem_id)
            
            # 如果同类型记忆超过1条，删除最旧的一条（保留空间给新记忆）
            if len(same_type_mems) >= 1:
                # 删除第一条（最旧的）
                old_id = same_type_mems[0]
                self.forget(old_id)
                print(f"[UPDATE] 替换旧{memory_type}记忆: {old_id[:8]}...")
                
        except Exception as e:
            print(f"[UPDATE] 替换失败: {e}")
    
    def _enforce_storage_limits(self, new_memory_type: str):
        """
        B. 强制执行存储上限
        
        当某类型记忆超过上限时，删除最旧的该类型记忆
        """
        try:
            # 通过store的cache获取所有记忆
            all_memories = list(self.store._memory_cache.values())
            
            # 按类型分组并找出最旧的
            type_memories = {
                MemoryType.IDENTITY: [],
                MemoryType.PREFERENCE: [],
                MemoryType.CONTEXT: [],
                MemoryType.FACT: []
            }
            
            for mem in all_memories:
                content = mem.content if hasattr(mem, 'content') else ""
                _, mem_type, _ = self._extract_from_tagged(content)
                if mem_type in type_memories:
                    # 记录(id, timestamp)
                    ts = mem.timestamp if hasattr(mem, 'timestamp') else ""
                    mem_id = mem.id if hasattr(mem, 'id') else ""
                    type_memories[mem_type].append((mem_id, ts))
            
            # 检查类型上限
            limits = {
                MemoryType.IDENTITY: self.MAX_IDENTITY,
                MemoryType.PREFERENCE: self.MAX_PREFERENCE,
                MemoryType.FACT: self.MAX_FACT,
                MemoryType.CONTEXT: self.MAX_FACT
            }
            
            for mem_type, mem_list in type_memories.items():
                limit = limits.get(mem_type, 50)
                if len(mem_list) >= limit:
                    # 按时间排序，删除最旧的
                    mem_list.sort(key=lambda x: x[1])
                    oldest_id = mem_list[0][0]
                    self.forget(oldest_id)
                    print(f"[CLEANUP] 清理旧{mem_type}记忆: {oldest_id[:8]}...")
            
            # 检查总上限
            total = len(all_memories)
            if total >= self.MAX_MEMORIES:
                # 删除最旧的fact
                if type_memories[MemoryType.FACT]:
                    type_memories[MemoryType.FACT].sort(key=lambda x: x[1])
                    oldest_id = type_memories[MemoryType.FACT][0][0]
                    self.forget(oldest_id)
                    print(f"[CLEANUP] 总记忆超限，删除旧fact: {oldest_id[:8]}...")
                    
        except Exception as e:
            print(f"[CLEANUP] 清理检查失败: {e}")
    
    def _extract_from_tagged(self, content: str) -> Tuple[str, str, float]:
        """从带标签的内容中提取元数据"""
        # 解析格式: [TYPE:identity|WEIGHT:1.5] 原始内容
        pattern = r"\[TYPE:(\w+)\|WEIGHT:([\d.]+)\] (.+)"
        match = re.match(pattern, content)
        
        if match:
            mem_type = match.group(1)
            weight = float(match.group(2))
            original = match.group(3)
            return original, mem_type, weight
        
        # 不匹配，返回默认值
        return content, "fact", 0.3
    
    def _detect_memory_type(self, content: str) -> str:
        """自动检测记忆类型"""
        # 身份检测
        identity_patterns = [
            r"我是(.+?)(?:作者|作家|工程师|医生|律师|程序员)",
            r"我从事(.+?)(?:工作|职业)",
            r"我的职业是"
        ]
        for pattern in identity_patterns:
            if re.search(pattern, content):
                return MemoryType.IDENTITY
        
        # 偏好检测
        preference_patterns = [
            r"我喜欢",
            r"我讨厌",
            r"我偏好",
            r"我觉得"
        ]
        for pattern in preference_patterns:
            if pattern in content:
                return MemoryType.PREFERENCE
        
        # 上下文检测
        context_patterns = [
            r"我正在",
            r"我在写",
            r"我在做"
        ]
        for pattern in context_patterns:
            if pattern in content:
                return MemoryType.CONTEXT
        
        # 默认事实
        return MemoryType.FACT
    
    def _get_type_weight(self, memory_type: str) -> float:
        """获取类型权重"""
        weights = {
            MemoryType.IDENTITY: self.IDENTITY_WEIGHT,
            MemoryType.PREFERENCE: self.PREFERENCE_WEIGHT,
            MemoryType.CONTEXT: self.CONTEXT_WEIGHT,
            MemoryType.FACT: self.FACT_WEIGHT
        }
        return weights.get(memory_type, self.FACT_WEIGHT)
    
    def recall_weighted(self, query: str, top_k: int = 5, 
                       current_round: int = None) -> List[Dict]:
        """
        加权检索（时间衰减 + 价值加权）
        
        Args:
            query: 查询
            top_k: 返回数量
            current_round: 当前会话轮次（用于计算衰减）
        """
        if current_round is None:
            current_round = self.session_round
        
        # 基础检索（扩大范围，因为后面要过滤）
        memories = self.recall(query, top_k=top_k*3)
        
        # 加权排序
        weighted_memories = []
        for mem in memories:
            # 处理Memory对象或字典
            if hasattr(mem, 'content'):
                content = mem.content
            else:
                content = mem.get("content", "")
            
            # 从带标签的内容中提取元数据
            original, mem_type, base_weight = self._extract_from_tagged(content)
            
            # 计算时间衰减
            mem_round = 0  # 简化处理，实际应该从metadata获取
            rounds_passed = current_round - mem_round
            
            # 衰减公式：超过ADHESION_WINDOW后指数衰减
            if rounds_passed <= self.ADHESION_WINDOW:
                time_factor = 1.0
            else:
                # 超过窗口后，每多10轮衰减50%
                over_rounds = rounds_passed - self.ADHESION_WINDOW
                time_factor = 0.5 ** (over_rounds / 10)
            
            # 综合权重
            final_weight = base_weight * time_factor
            
            weighted_memories.append({
                "memory": mem,
                "weight": final_weight,
                "type": mem_type,
                "rounds_passed": rounds_passed
            })
        
        # 按权重排序
        weighted_memories.sort(key=lambda x: x["weight"], reverse=True)
        
        # 返回前top_k个权重大于阈值的
        result = [item for item in weighted_memories[:top_k] 
                  if item["weight"] > 0.1]
        
        return result
    
    def _detect_query_type(self, query: str) -> str:
        """
        A. 检测查询类型
        
        根据问句内容判断用户想问什么类型的信息
        """
        # 身份类查询
        identity_queries = [
            r"我是做什么",
            r"我的职业",
            r"我是谁",
            r"我是.*吗",  # "我是作者吗？"
            r"工作",
        ]
        for pattern in identity_queries:
            if re.search(pattern, query):
                return MemoryType.IDENTITY
        
        # 偏好类查询
        preference_queries = [
            r"我喜欢",
            r"我讨厌",
            r"我喜欢.*吗",
            r"我的喜好",
            r"我的兴趣",
        ]
        for pattern in preference_queries:
            if re.search(pattern, query):
                return MemoryType.PREFERENCE
        
        # 上下文类查询
        context_queries = [
            r"我在做",
            r"我正在",
            r"我的项目",
            r"我在写",
        ]
        for pattern in context_queries:
            if re.search(pattern, query):
                return MemoryType.CONTEXT
        
        # 默认返回None（不过滤，所有类型都考虑）
        return None
    
    def format_for_injection(self, memories: List[Dict], 
                            strategy: str = "camouflage",
                            query_type: str = None) -> str:
        """
        格式化记忆用于注入（伪装注入）
        
        Args:
            memories: 检索到的记忆（加权后的）
            strategy: "camouflage"（伪装）或 "direct"（直接）
            query_type: A. 查询类型，只注入匹配类型的记忆
        
        Returns:
            格式化后的注入文本
        """
        if not memories:
            return ""
        
        # A. 类型感知过滤
        if query_type:
            # 只保留匹配类型的记忆
            filtered = [item for item in memories 
                       if item.get("type") == query_type]
            # 如果过滤后太少，保留一些高权重的其他类型
            if len(filtered) < 2:
                # 添加其他类型的高权重记忆（权重>=1.0）
                other_high = [item for item in memories 
                             if item.get("type") != query_type 
                             and item.get("weight", 0) >= 1.0]
                filtered.extend(other_high[:2])  # 最多加2条
            memories = filtered if filtered else memories
        
        # 提取内容
        contents = []
        for item in memories:
            # 处理Memory对象或字典
            if hasattr(item["memory"], 'content'):
                content = item["memory"].content
            else:
                content = item["memory"].get("content", "")
            
            # 从带标签的内容中提取原始内容
            original, mem_type, weight = self._extract_from_tagged(content)
            
            # 只使用高价值记忆
            if item["weight"] >= 0.5:
                contents.append(original)
        
        if not contents:
            return ""
        
        # 格式化
        info_text = "；".join(contents[:3])  # 最多3条
        
        if strategy == "camouflage":
            # 实验#3验证：伪装注入，自然度4/5
            return f"[对话上下文：用户之前提到过{info_text}]"
        else:
            # 实验#2：直接注入，自然度3/5
            return f"[豆语记忆：{info_text}]"
    
    def check_ethics(self, query: str) -> Dict[str, Any]:
        """
        伦理检查（实验#5）
        
        检测高风险查询：
        - 时间定位询问（"第一次见面"）
        - 具体细节询问（"原话是什么"）
        """
        high_risk_patterns = [
            r"第一次见面",
            r"你记得.*吗",
            r"当时.*说了什么",
            r"原话.*是什么",
            r"逐字.*记录",
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, query):
                return {
                    "allow": False,
                    "block": True,
                    "risk_type": "time_location",
                    "response": "我记得你提到过一些重要信息，但关于具体时间和细节，我可能没有完整记录。你能再说一遍吗？"
                }
        
        return {"allow": True, "block": False}
    
    def chat_with_memory(self, user_input: str, 
                        chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        带记忆的对话（整合所有优化）
        
        Returns:
            {
                "response": str,  # 模型回复
                "injection": str, # 注入的内容
                "memories_used": List, # 使用的记忆
                "ethics_check": Dict,  # 伦理检查
            }
        """
        self.session_round += 1
        
        # 1. 伦理检查
        ethics_result = self.check_ethics(user_input)
        if ethics_result["block"]:
            return {
                "response": ethics_result["response"],
                "injection": "",
                "memories_used": [],
                "ethics_check": ethics_result
            }
        
        # 2. 检索记忆（加权）
        memories = self.recall_weighted(user_input, top_k=3, 
                                       current_round=self.session_round)
        
        # A. 检测查询类型（类型感知注入）
        query_type = self._detect_query_type(user_input)
        
        # 3. 格式化注入（类型感知）
        injection = self.format_for_injection(
            memories, 
            strategy="camouflage",
            query_type=query_type  # 传入查询类型
        )
        
        # 4. 构建提示
        if injection:
            enhanced_input = f"{user_input}\n{injection}"
        else:
            enhanced_input = user_input
        
        # 5. 生成回复（需要调用LLM）
        # 这里简化处理，实际应该调用Ollama
        response_text = f"[基于记忆回复] 用户输入：{enhanced_input[:50]}..."
        
        return {
            "response": response_text,
            "injection": injection,
            "memories_used": memories,
            "ethics_check": ethics_result
        }
    
    def update_identity(self, old_identity: str, new_identity: str):
        """
        更新身份（实验#6-#7）
        
        不是追加，是替换
        """
        # 标记旧身份为inactive
        # 这需要修改store的实现来支持更新metadata
        # 简化版：存储新身份时添加"replaces"标记
        
        self.remember_with_type(
            content=f"用户更新身份：从{old_identity}改为{new_identity}",
            memory_type=MemoryType.IDENTITY,
            source="identity_update"
        )
