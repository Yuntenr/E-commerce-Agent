🛒 NL2SQL 电商数据分析智能体 (E-commerce Data Analysis Agent)

基于 LLM + Agent + RAG + NL2SQL 构建的智能数据分析助手，用户可以通过自然语言提问，系统能够自动理解业务需求、检索数据库知识、生成 SQL 查询，并返回可解释的数据分析结果。
在企业的日常运营中，产品经理、运营人员、业务负责人等常常需要回答诸如：
- 我想知道华北地区的销售总额是多少。
- 我想看各品牌销量最高的商品有哪些。
- 我想统计男性用户的订单总额。
这些问题本质上都不是“聊天问题”，而是结构化数据查询问题。传统流程下，这些问题需要通过写 SQL 或提需求给数据分析师来完成，沟通成本高、响应周期长；而E-commerce-Agent要做的，就是把“自然语言提问”自动转换成“可执行的 SQL 查询”，再把查询结果返回给用户。
一句话概括，这个项目就是一个典型的 NL2SQL 智能体项目。NL2SQL 的意思是：Natural Language to SQL，也就是“自然语言转 SQL”。用户只负责提问，系统借助大模型理解问题并生成 SQL，再到数据库或数据仓库中执行查询，最后把结果返回给用户。
项目重点解决传统 BI（Business Intelligence） 系统中 查询门槛高、业务人员无法直接访问数据库、多轮分析上下文丢失 等问题。


---

✨ 项目演示

用户无需学习 SQL，只需要使用自然语言：

用户：
2026年销量最高的商品是什么？
Agent：
2026年销量最高的商品为三只松鼠坚果礼盒，共销售 XXX 件。

用户：
那它的单价是多少？
Agent：
三只松鼠坚果礼盒当前单价为 XX 元。

系统能够理解上下文，实现连续业务分析。


---

🚀 核心功能

1. 自然语言转 SQL (NL2SQL)

支持用户通过自然语言查询业务数据：
例如：
查询2026年各品牌销售额排名
自动生成：
SELECT
    brand_name,
    SUM(amount) AS sales_amount
FROM
    orders
WHERE
    year = 2026
GROUP BY
    brand_name
ORDER BY
    sales_amount DESC;
并执行 SQL 返回结果。



---

2. Agent 智能工作流
基于 LangGraph 构建状态化 Agent Workflow：

                 User Query
                     |
                     v
          Query Understanding
                     |
                     v
          Query Rewrite
          (上下文消解)
                     |
                     v
          Metadata Retrieval
          (RAG)
                     |
                     v
          SQL Generation
                     |
                     v
          SQL Validation
                     |
                     v
          Database Execute
                     |
                     v
          Result Explanation
                     |
                     v
              Memory Update



---

🧠 Agent 核心设计

1. Query Rewrite（多轮上下文理解）

针对传统 LLM 无法理解指代问题：

例如：

用户：
交易额最高的用户是谁？

Agent：
张三。

用户：
那他的电话是多少？

通过 Redis 保存历史上下文，并结合 Query Rewrite 节点：
原问题：

那他的电话是多少？
转换为：
用户张三的联系电话是多少？
提升多轮分析体验。


---

2. RAG 元数据检索

为了提高 SQL 生成准确率，引入数据库 Metadata RAG。
存储：
- 数据表信息
- 字段定义
- 指标定义
- 字段值信息
流程：
User Query --> Embedding --> Qdrant Vector Search --> Relevant Metadata --> SQL Generation
解决：
- 表选择错误
- 字段理解错误
- 业务指标歧义

---

3. Conversation Memory

使用 Redis 实现会话记忆：
保存：
{
    "session_id": "xxx",
    "history": [
        {
            "question":"销量最高的是谁",
            "answer":"三只松鼠"
        }
    ],
    "active_entities":[
        {
            "type":"product",
            "name":"三只松鼠"
        }
    ]
}

支持：
- 多轮问答
- 实体追踪
- 指代消解

---

🏗️ 系统架构

                    Frontend
              React + TypeScript
                       |
                       |
                    SSE Stream
                       |
                       |
                 FastAPI Backend
                       |
              -------------------
              |                 |
          LangGraph Agent       Redis
              |
   ----------------------------
   |            |              |
 Query      RAG Retrieval    SQL Agent
 Rewrite        |
               |
          Qdrant / Elasticsearch

               |
               |
             MySQL
          Data Warehouse



---

🛠️ 技术栈

Backend
技术
用途
Python
后端开发
FastAPI
API 服务
LangChain
LLM 应用框架
LangGraph
Agent 工作流编排
Redis
会话记忆
MySQL
数据存储
Docker
服务部署
AI
技术
用途
LLM
SQL生成、语义理解
RAG
元数据增强
Embedding
文本向量化
Qdrant
向量数据库
Elasticsearch
关键词检索
Frontend
技术
用途
React
前端框架
TypeScript
类型安全
Vite
构建工具
TailwindCSS
UI开发
SSE
流式响应


---

⚙️ 环境部署

1. Clone项目

git clone https://github.com/yourname/E-commerce-Agent.git

cd E-commerce-Agent



---

2. 创建Python环境
conda create -n agent_env python=3.14

conda activate agent_env
安装依赖：
pip install -r requirements.txt
  

---

3. 启动基础服务
使用 Docker：
docker compose up -d
启动：
- MySQL
- Redis
- Qdrant
- Elasticsearch

---

4. 启动后端
uvicorn app.main:app --reload

---
5. 启动前端
cd frontend

npm run dev


---
📌 项目亮点

⭐ 1. 基于 LangGraph 构建状态化 Agent
相比传统 Chain：
- 支持复杂任务拆解
- 支持节点条件跳转
- 支持状态共享

---

⭐ 2. RAG增强 NL2SQL
通过数据库知识检索：
- 降低 SQL 幻觉
- 提升字段匹配准确率
- 支持业务指标理解

---

⭐ 3. 多轮 Memory 机制
结合：
- Redis Session
- Entity Extraction
- Query Rewrite
实现类似 ChatGPT 的连续数据分析体验。

---

📄 License

MIT License