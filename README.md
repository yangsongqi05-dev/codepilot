# CodePilot

一个从零手写的 **Coding Agent**：给它一个仓库和一个任务，它会自己读代码、改文件、跑测试、看报错、再改，直到测试通过。

**没有用 LangChain / LangGraph 做 Agent 循环。** 提示词、工具说明书、JSON 解析、循环、调度，全部手写。

[![tests](https://github.com/yangsongqi05-dev/codepilot/actions/workflows/test.yml/badge.svg)](https://github.com/yangsongqi05-dev/codepilot/actions/workflows/test.yml)

---

## 它能做什么

给它一个任务：

```bash
python main.py "demo_project 里的测试有一个跑不过，你去看看是哪里错了，改到测试全部通过"
```

它自己跑完这一串：

```
[1] 首先查看 demo_project 目录下的文件
      -> list_file({'rel': 'demo_project'})
[2] 运行测试以查看哪些测试失败
      -> run_tests({'rel': 'demo_project'})
[3] 查看 calc.py 文件内容，了解 average 函数的实现
      -> read_file({'rel': 'demo_project/calc.py'})
[4] 发现 average 函数计算错误，应该去掉 -1 的调整
      -> edit_file({'rel': 'demo_project/calc.py', 'old': 'return total/len(nums)-1', 'new': 'return total/len(nums)'})
[5] 再次运行测试以确认问题已解决
      -> run_tests({'rel': 'demo_project'})
[6] 完成

最终答复： 已修复 average 函数的计算错误，现在测试全部通过。
```

**改的是源代码，不是把测试改绿；改完自己又跑了一次测试才交差。**

---

## 它是怎么转起来的

```
你的任务
   |
[main.py]  从命令行拿到任务
   |
[loop.py]  messages = [系统提示词, 任务]
   |
   +---------------- 最多 15 轮 ----------------+
   |  chat(messages)      -> 模型输出一段文本      |
   |         |                                  |
   |  parse_action()      -> 从脏输出里抠出 JSON   |
   |     +-- 解析失败 -> 把原因喂回去，让它重说     |
   |     +-- final   -> 收工                    |
   |     +-- action  -> call_tool() 执行工具      |
   |                       |                    |
   |              结果 append 回 messages         |
   +--------------------------------------------+
```

**模型只会吐一段 JSON 文本，它什么都不会干；真正干活的是自己的代码。**

---

## 核心设计

### 1. 工具层分两类失败

| 失败类型 | 处理方式 | 为什么 |
|---|---|---|
| **硬边界**（路径越界） | 抛 `ValueError` | 这条线不能跨，必须炸 |
| **软失败**（原文找不到 / 匹配多次） | 返回一句说明 | 模型能看懂，自己换个方式重试 |

再由 `call_tool()` 统一把异常接住、翻译成一句话喂回模型 —— **报警要报给能处理它的人**。

```python
# 之前：越界 -> 抛异常 -> 整个程序 exit code 1
# 现在：越界 -> 「工具执行出错：ValueError: 路径越界，拒绝访问：../../config.py」
#                -> 喂回模型 -> 它知道这条路不能走，换个方式再来
```

### 2. 两层安全边界

**路径层** —— `safe_path()` 把 Agent 的所有文件操作锁在 `workspace/` 里：

```python
full = os.path.abspath(os.path.join(root, rel))
if full != root and not full.startswith(root + os.sep):
    raise ValueError(...)
```

`root + os.sep` 里那个 `os.sep` 不能省 —— 否则 `workspace_evil` 会被误判成"在工作区里"。

**执行层** —— 所有代码都在 Docker 容器里跑，工作区挂载到 `/work`：

```
能看到 E 盘吗 = False
cwd  = /work/demo_project
node = ad4a7059267e     ← 容器 ID，不是宿主机
```

### 3. 代码检索按函数切块

用 `ast` 把 Python 文件按**顶层函数/类**切开，不是按字符数切 —— 按字符切会把一个函数从中间砍断，检索出来是残骸。

```python
tree = ast.parse(source)
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        seg = ast.get_source_segment(source, node)   # 按行号精确取出这一段
```

**并且给每一块加上"文件 + 函数名"的头再嵌入**：

```python
'text': f'# {rel} · 函数 {node.name}\n{seg}'
```

实测效果（问"怎么把一堆数加起来然后除以它们的个数"）：

| | 加头之前 | 加头之后 |
|---|---|---|
| `average` | 第 2 名（0.6228） | **第 1 名**（0.5840） |
| `add` | 第 1 名（0.6587） | 第 2 名（0.5687） |

`add` 只有两行，语义特别纯粹，向量很聚焦；`average` 五行，语义被稀释。**把函数名拼进去等于给它加了一个语义锚点。**

### 4. 嵌入缓存 = 增量索引

每次重建索引都要重新调嵌入 API。3000 块的代码库改一个文件，就是 3000 次调用。

用 Redis 按文本指纹缓存向量，只对**没见过的块**调 API：

```
嵌入缓存命中 0/7      ← 全 miss
索引完成，一共 7 块
嵌入缓存命中 7/7      ← 全命中，0 次 API 调用
```

---

## 技术栈

`Python 3.11` · `DeepSeek-V3`（对话）· `BGE-M3`（嵌入）· `Chroma`（向量库）· `Redis`（缓存）· `Docker`（沙箱）· `pytest` · `GitHub Actions`

---

## 快速开始

```bash
# 1. 装依赖
pip install -r requirements.txt

# 2. 配置密钥
cp .env.example .env
#    然后把 .env 里的 API_KEY 改成你自己的硅基流动密钥

# 3. 建代码索引
python -m tools.code_index

# 4. 跑一个任务
python main.py "demo_project 里的测试有一个跑不过，你去看看是哪里错了，改到测试全部通过"
```

**需要本机开着 Docker Desktop**（沙箱执行依赖它）。

---

## 测试

```bash
python -m pytest -q
```

```
16 passed, 1 skipped in 1.07s
```

覆盖的是**最容易坏、坏了最危险**的地方：

| 测试 | 守住什么 |
|---|---|
| `safe_path` × 6 | 路径越界必须抛异常 —— 这是唯一挡在密钥文件前面的东西 |
| `parse_action` × 7 | 模型输出带围栏 / 带废话 / 根本不是 JSON 时不能崩 |
| `edit_file` × 4 | 原文找不到、匹配多次时 **文件必须一个字节都不变** |

> 有一条 `skipif` 的测试，是因为它验的是 Windows 专有行为（反斜杠是路径分隔符），CI 跑在 Linux 上会跳过 —— **这是 CI 第一天就抓出来的真问题。**

---

## 目录结构

```
codepilot/
├── agent/
│   ├── llm.py          # 系统提示词、调模型、JSON 解析
│   └── loop.py         # Agent 循环
├── tools/
│   ├── fs.py           # safe_path / list_files / read_file / write_file / edit_file / search_code
│   ├── shell.py        # run_python / run_tests / git_diff（都在容器里执行）
│   ├── code_index.py   # 按函数切块 + 嵌入 + Chroma 检索
│   ├── cache.py        # Redis 嵌入缓存
│   └── registry.py     # 工具注册表：给模型的说明书 + 调度器
├── tests/              # 17 个测试
├── workspace/          # Agent 的活动范围（沙箱靶子）
├── .github/workflows/  # CI：每次 push 自动跑测试
├── config.py / main.py / Dockerfile / pytest.ini / requirements.txt
└── .env.example
```

---

## 设计取舍（为什么这么做）

**为什么不用 LangChain？**
先用框架做过一遍（另一个项目），再手写一遍是为了确认它替我做了什么。结论：**框架把 docstring 转成 schema、把 tool_calls 解析成对象；但沙箱边界、匹配唯一性、超时截断、循环退出、异常怎么回喂，它一样都不管** —— 那些才是真正要设计的地方。

**为什么消息历史存内存，不存数据库？**
任务是一次性的，跑完就结束，没有多轮会话需求。存 SQLite 是另一个项目的做法，那里需要跨轮次持久化。

**为什么嵌入用 API 而不是本地模型？**
跟另一个 RAG 项目保持一致（同一个 `BGE-M3`），而且省掉几百 MB 的模型下载。代价是依赖网络 —— 所以加了 Redis 缓存，同一个文本只算一次。

**已知不足**
- 拦不住 Agent 去改测试文件（它可以把 `assert == 2` 改成 `== 1.0` 让测试变绿）
- 索引不是实时的，改完代码要手动重建
- 没有并发，一次只跑一个任务
