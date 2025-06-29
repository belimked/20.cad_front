import pytest
from services.vpocontractclone_service import VpoContractCloneService

def test_vpocontractclone_basic():
    """测试基本克隆功能"""
    service = VpoContractCloneService()
    test_data = {
        "question": "将盛和湾区大厦项目的合同材料单价克隆到实验80、实验83项目",
        "elements": ["03", "04", "05", "06"],
        "answer": {}
    }
    result = service.post_process_data(test_data)
    assert result["answer"]["operation"] == "克隆合同单价"
    assert result["answer"]["object"] == "合同信息审核单"
    assert result["answer"]["supplierGroup"] == "无"
    assert result["answer"]["materialType"] == "常规附件"

def test_vpocontractclone_batch():
    """测试批量克隆功能"""
    service = VpoContractCloneService()
    test_data = {
        "question": "批量克隆合同信息，将盛和湾区大厦项目的合同材料单价克隆到其余所有项目合同中",
        "elements": ["01", "03", "04", "05", "07"],
        "answer": {}
    }
    result = service.post_process_data(test_data)
    assert result["answer"]["operation"] == "批量克隆合同单价"
    assert result["answer"]["object"] == "合同信息审核单"
    assert result["answer"]["targetProjects"] == "其余所有项目"
    assert result["answer"]["supplierGroup"] == "无"
    assert result["answer"]["materialType"] == "常规附件" 