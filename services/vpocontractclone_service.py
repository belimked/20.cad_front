from services.base_generation_service import BaseGenerationService

class VpoContractCloneService(BaseGenerationService):
    def post_process_data(self, data):
        """后处理方法，处理生成的数据"""
        # 1. 处理操作类型
        if "批量" in data["question"]:
            data["answer"]["operation"] = "批量克隆合同单价"
        else:
            data["answer"]["operation"] = "克隆合同单价"
            
        # 2. 设置默认值
        data["answer"].update({
            "object": "合同信息审核单",
            "supplierGroup": "无",
            "materialType": "常规附件"
        })
        
        # 3. 处理项目信息
        if "04" in data.get("elements", []):
            source_project = self._extract_project(data["question"], is_source=True)
            data["answer"]["sourceProject"] = source_project
            
        if "06" in data.get("elements", []):
            target_projects = self._extract_project(data["question"], is_source=False)
            data["answer"]["targetProjects"] = target_projects
        elif "07" in data.get("elements", []):
            data["answer"]["targetProjects"] = "其余所有项目"
            
        return data
        
    def _extract_project(self, question, is_source=True):
        """提取项目信息
        
        Args:
            question: 问题文本
            is_source: 是否是源项目
            
        Returns:
            str: 提取的项目名称或项目列表
        """
        # TODO: 实现项目提取逻辑
        # 1. 如果是源项目，只提取一个项目
        # 2. 如果是目标项目，可能有多个项目，用逗号分隔
        return "测试项目" 