"""
验证豆语更新机制
"""
import sys
sys.path.insert(0, "C:\\Users\\Administrator\\.openclaw\\workspace\\doulang\\src")

from doulang import DouLangEnhanced, MemoryType

dl = DouLangEnhanced()

print("="*60)
print("测试豆语更新机制")
print("="*60)

# 测试1: 初始身份
print("\n【测试1】初始身份")
print("用户: 我是科幻小说作者")
dl.remember_with_type("我是科幻小说作者", MemoryType.IDENTITY)

# 查看存储
all_mems = list(dl.store._memory_cache.values())
print(f"当前记忆数: {len(all_mems)}")
for i, mem in enumerate(all_mems[-3:], 1):
    print(f"  {i}. {mem.content[:60]}...")

# 测试2: 更新身份（带"其实"关键词）
print("\n【测试2】更新身份（带'其实'）")
print("用户: 其实我是奇幻小说作者")

# 检查当前实现是否会自动更新
# 实际: 只是追加，不会替换
old_count = len(all_mems)
dl.remember_with_type("其实我是奇幻小说作者", MemoryType.IDENTITY)

all_mems = list(dl.store._memory_cache.values())
new_count = len(all_mems)

print(f"更新前记忆数: {old_count}")
print(f"更新后记忆数: {new_count}")

if new_count > old_count:
    print("⚠️  发现: 当前实现是'追加'，不是'替换'")
    print("   两条身份同时存在：")
    for i, mem in enumerate(all_mems[-3:], 1):
        print(f"   {i}. {mem.content[:60]}...")
else:
    print("✅ 有替换机制")

print("\n" + "="*60)
print("结论")
print("="*60)
print("""
当前豆语的问题：
- 只有'存储上限清理'（超5条删最旧的）
- 没有'主动更新'机制（新身份替换旧身份）
- 需要手动实现更新逻辑

解决方案：
1. 检测更新信号（'其实'、'不再'、'现在'等）
2. 找到同类型的旧记忆
3. 标记为inactive或删除
4. 存储新记忆
""")
