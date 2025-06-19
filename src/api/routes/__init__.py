#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API路由模块
"""

from src.api.routes.answer import router as answer_router
from src.api.routes.base_dict import router as base_dict_router
from src.api.routes.relationship import router as relationship_router
from src.api.routes.generate import router as generate_router
from src.api.routes.evaluation_analysis import router as evaluation_analysis_router

# 继续在app.py中导入其他路由模块 