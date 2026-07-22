from app.agent.state import HistoryQA, ContextEntity

# 指代词
REFERENCE_WORDS = ["他", "她", "它", "这个", "那个", "该", "上述", "刚才", "之前", "上面"]
# 典型追问
FOLLOW_UP_WORDS = ["呢","怎么样","电话","地址","价格","销量","利润"]


def need_query_rewrite(query: str, history: list[HistoryQA], entities: list[ContextEntity]) -> bool:
    """
    判断是否需要query rewrite
    """

    # 没有历史上下文
    if not history and not entities:
        return False
    
    # 1. 明确指代
    for word in REFERENCE_WORDS:
        if word in query:
            return True
    
    # 2. 短追问
    # 有上下文，并且问题较短
    # 例如:
    # 电话呢？
    # 价格多少？
    # 销量怎么样？
    if entities and len(query) <= 8:
        for word in FOLLOW_UP_WORDS:
            if word in query:
                return True
            
    return False
