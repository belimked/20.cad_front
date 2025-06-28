from fastapi import APIRouter, HTTPException
import json
import os
from pathlib import Path
# 导入业务规则服务
from src.service.common.business_rules import get_business_rules_service

router = APIRouter()

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RELATIONSHIP_DIR = BASE_DIR / "src" / "entity" / "relationship"

@router.get("/relationship/")
async def get_relationship_index():
    """获取关系规则索引"""
    try:
        index_file = RELATIONSHIP_DIR / "rulesIndex.json"
        if not index_file.exists():
            return {"error": "规则索引文件不存在"}
        
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取规则索引失败: {str(e)}")

@router.get("/relationship/{rule_id}")
async def get_relationship_rules(rule_id: str):
    """获取指定ID的关系规则"""
    try:
        # 先读取索引文件，找到对应的文件名
        index_file = RELATIONSHIP_DIR / "rulesIndex.json"
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="规则索引文件不存在")
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 在索引中查找对应的规则文件
        rule_file = None
        for rule_map in index_data.get("rulesMaps", []):
            if rule_map.get("id") == rule_id:
                rule_file = rule_map.get("fileName")
                break
        
        if not rule_file:
            raise HTTPException(status_code=404, detail=f"找不到ID为 '{rule_id}' 的规则")
        
        # 读取规则文件
        rule_file_path = RELATIONSHIP_DIR / rule_file
        if not rule_file_path.exists():
            raise HTTPException(status_code=404, detail=f"规则文件 '{rule_file}' 不存在")
        
        with open(rule_file_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        return {
            "id": rule_id,
            "description": next((rule_map.get("description") for rule_map in index_data.get("rulesMaps", []) if rule_map.get("id") == rule_id), ""),
            "rules": rules_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取规则文件失败: {str(e)}")

@router.post("/relationship/{rule_id}")
async def update_relationship_rules(rule_id: str, rules_data: dict):
    """更新指定ID的关系规则"""
    try:
        # 先读取索引文件，找到对应的文件名
        index_file = RELATIONSHIP_DIR / "rulesIndex.json"
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="规则索引文件不存在")
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 在索引中查找对应的规则文件
        rule_file = None
        for rule_map in index_data.get("rulesMaps", []):
            if rule_map.get("id") == rule_id:
                rule_file = rule_map.get("fileName")
                break
        
        if not rule_file:
            raise HTTPException(status_code=404, detail=f"找不到ID为 '{rule_id}' 的规则")
        
        # 更新规则文件
        rule_file_path = RELATIONSHIP_DIR / rule_file
        
        with open(rule_file_path, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, ensure_ascii=False, indent=2)
        
        # 清除业务规则缓存
        business_rules_service = get_business_rules_service()
        # 从文件名中提取业务对象名称（去掉扩展名）
        business_object = os.path.splitext(rule_file)[0]
        # 如果缓存中存在该业务对象，则删除缓存
        if business_object in business_rules_service.business_rules_cache:
            del business_rules_service.business_rules_cache[business_object]
            print(f"已清除业务规则缓存: {business_object}")
        
        return {"message": f"规则 '{rule_id}' 已成功更新，缓存已清除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新规则文件失败: {str(e)}")

@router.get("/relationship/{rule_id}/rules")
async def get_relationship_rule_details(rule_id: str):
    """获取指定ID的关系规则详情"""
    try:
        # 先读取索引文件，找到对应的文件名
        index_file = RELATIONSHIP_DIR / "rulesIndex.json"
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="规则索引文件不存在")
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 在索引中查找对应的规则文件
        rule_file = None
        rule_description = ""
        for rule_map in index_data.get("rulesMaps", []):
            if rule_map.get("id") == rule_id:
                rule_file = rule_map.get("fileName")
                rule_description = rule_map.get("description", "")
                break
        
        if not rule_file:
            raise HTTPException(status_code=404, detail=f"找不到ID为 '{rule_id}' 的规则")
        
        # 读取规则文件
        rule_file_path = RELATIONSHIP_DIR / rule_file
        if not rule_file_path.exists():
            raise HTTPException(status_code=404, detail=f"规则文件 '{rule_file}' 不存在")
        
        with open(rule_file_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        # 提取实际的规则列表
        rules = rules_data.get("rulesMap", [])
        
        return {
            "id": rule_id,
            "description": rule_description,
            "count": len(rules),
            "rules": rules
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取规则详情失败: {str(e)}") 