
# 简单的基线模型 - 基于规则的回答
def baseline_model(question, task_type):
    """基于规则的简单基线模型"""
    
    if "关联" in question or "关系" in question:
        if task_type == "basic_relationship":
            return "通过外键字段关联，关系类型为多对一。"
        elif task_type == "negative_relationship":
            return "这两个表之间没有直接关联关系。"
    
    elif "查询" in question and "数量" in question:
        return "SQL查询:\n```sql\nSELECT COUNT(*) FROM table_name\n```"
    
    return "需要更多信息来回答这个问题。"
