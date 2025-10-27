"""
数据迁移脚本 - 初始化图像预处理方法字典

将所有图像预处理方法录入到 sys_dictionary 表中

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.dictionary import Dictionary
from src.utils.image_processing import PREPROCESSING_METHODS, get_method_description
import json


def init_preprocessing_methods_dict():
    """初始化图像预处理方法字典数据"""

    print("=" * 80)
    print("初始化图像预处理方法字典数据")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 预处理方法的详细配置
        methods_config = {
            'original': {
                'label': '原始图像',
                'description': '原始图像，未经处理',
                'sort_order': 1,
                'extra_data': {
                    'category': 'basic',
                    'performance': 'fastest',
                    'recommended': True,
                    'params': {}
                }
            },
            'grayscale': {
                'label': '灰度化',
                'description': '转换为单通道灰度图，减少数据维度',
                'sort_order': 2,
                'extra_data': {
                    'category': 'basic',
                    'performance': 'fast',
                    'recommended': False,
                    'params': {}
                }
            },
            'binary_adaptive': {
                'label': '自适应二值化',
                'description': '局部阈值二值化，适合光照不均场景',
                'sort_order': 3,
                'extra_data': {
                    'category': 'binarization',
                    'performance': 'fast',
                    'recommended': True,
                    'params': {
                        'binary_adaptive_block_size': {
                            'default': 11,
                            'type': 'int',
                            'range': [3, 51],
                            'step': 2,
                            'description': '邻域大小（必须为奇数）'
                        },
                        'binary_adaptive_c': {
                            'default': 2,
                            'type': 'int',
                            'range': [0, 20],
                            'description': '常数C（从均值中减去）'
                        }
                    },
                    'use_cases': ['AutoCAD菜单', '光照不均', '白底黑字']
                }
            },
            'binary_otsu': {
                'label': 'Otsu二值化',
                'description': '自动阈值二值化，适合双峰分布图像',
                'sort_order': 4,
                'extra_data': {
                    'category': 'binarization',
                    'performance': 'fast',
                    'recommended': True,
                    'params': {},
                    'use_cases': ['清晰前景背景', '文档扫描']
                }
            },
            'binary_global': {
                'label': '全局二值化',
                'description': '固定阈值二值化，简单快速',
                'sort_order': 5,
                'extra_data': {
                    'category': 'binarization',
                    'performance': 'fastest',
                    'recommended': False,
                    'params': {
                        'binary_global_threshold': {
                            'default': 127,
                            'type': 'int',
                            'range': [0, 255],
                            'description': '全局阈值'
                        }
                    },
                    'use_cases': ['光照均匀']
                }
            },
            'high_contrast': {
                'label': '高对比度增强',
                'description': 'CLAHE对比度增强，适合低对比度图像',
                'sort_order': 6,
                'extra_data': {
                    'category': 'enhancement',
                    'performance': 'medium',
                    'recommended': True,
                    'params': {
                        'clahe_clip_limit': {
                            'default': 3.0,
                            'type': 'float',
                            'range': [1.0, 40.0],
                            'description': '对比度限制'
                        },
                        'clahe_tile_size': {
                            'default': [8, 8],
                            'type': 'tuple',
                            'description': '分块大小'
                        }
                    },
                    'use_cases': ['低对比度', '模糊文字']
                }
            },
            'high_brightness': {
                'label': '高亮度调整',
                'description': '增加图像亮度和对比度',
                'sort_order': 7,
                'extra_data': {
                    'category': 'enhancement',
                    'performance': 'fast',
                    'recommended': False,
                    'params': {
                        'brightness_alpha': {
                            'default': 1.3,
                            'type': 'float',
                            'range': [0.5, 3.0],
                            'description': '对比度因子'
                        },
                        'brightness_beta': {
                            'default': 50,
                            'type': 'int',
                            'range': [-100, 100],
                            'description': '亮度偏移'
                        }
                    },
                    'use_cases': ['暗色主题', '灰色文字']
                }
            },
            'denoise_gaussian': {
                'label': '高斯降噪',
                'description': '高斯模糊降噪，保留边缘',
                'sort_order': 8,
                'extra_data': {
                    'category': 'denoising',
                    'performance': 'fast',
                    'recommended': False,
                    'params': {
                        'gaussian_kernel': {
                            'default': [5, 5],
                            'type': 'tuple',
                            'description': '核大小（奇数）'
                        }
                    },
                    'use_cases': ['轻度噪声']
                }
            },
            'denoise_median': {
                'label': '中值滤波降噪',
                'description': '中值滤波，去除椒盐噪声',
                'sort_order': 9,
                'extra_data': {
                    'category': 'denoising',
                    'performance': 'fast',
                    'recommended': False,
                    'params': {
                        'median_kernel': {
                            'default': 5,
                            'type': 'int',
                            'range': [3, 21],
                            'step': 2,
                            'description': '核大小（奇数）'
                        }
                    },
                    'use_cases': ['椒盐噪声', '黑白点']
                }
            },
            'denoise_bilateral': {
                'label': '双边滤波降噪',
                'description': '保边降噪，保留文字锐利边缘',
                'sort_order': 10,
                'extra_data': {
                    'category': 'denoising',
                    'performance': 'medium',
                    'recommended': True,
                    'params': {
                        'bilateral_d': {
                            'default': 9,
                            'type': 'int',
                            'range': [1, 20],
                            'description': '邻域直径'
                        },
                        'bilateral_sigma_color': {
                            'default': 75,
                            'type': 'int',
                            'range': [10, 150],
                            'description': '颜色空间标准差'
                        },
                        'bilateral_sigma_space': {
                            'default': 75,
                            'type': 'int',
                            'range': [10, 150],
                            'description': '坐标空间标准差'
                        }
                    },
                    'use_cases': ['保留边缘', '文字清晰化']
                }
            },
            'denoise_nlm': {
                'label': '非局部均值降噪',
                'description': '全局搜索降噪，效果最好但速度慢',
                'sort_order': 11,
                'extra_data': {
                    'category': 'denoising',
                    'performance': 'slow',
                    'recommended': False,
                    'params': {
                        'nlm_h': {
                            'default': 10,
                            'type': 'int',
                            'range': [1, 30],
                            'description': '滤波强度'
                        }
                    },
                    'use_cases': ['强噪声', '高质量要求']
                }
            },
            'rgb_red': {
                'label': '红色通道',
                'description': '提取红色通道信息',
                'sort_order': 12,
                'extra_data': {
                    'category': 'channel_split',
                    'performance': 'fastest',
                    'recommended': False,
                    'params': {},
                    'use_cases': ['红色文字识别', '红色图层提取']
                }
            },
            'rgb_green': {
                'label': '绿色通道',
                'description': '提取绿色通道信息',
                'sort_order': 13,
                'extra_data': {
                    'category': 'channel_split',
                    'performance': 'fastest',
                    'recommended': False,
                    'params': {},
                    'use_cases': ['绿色文字识别', '绿色图层提取']
                }
            },
            'rgb_blue': {
                'label': '蓝色通道',
                'description': '提取蓝色通道信息',
                'sort_order': 14,
                'extra_data': {
                    'category': 'channel_split',
                    'performance': 'fastest',
                    'recommended': False,
                    'params': {},
                    'use_cases': ['蓝色文字识别', '黄色文字识别（反差大）']
                }
            },
            'edge_canny': {
                'label': 'Canny边缘检测',
                'description': '精确边缘检测，细线条',
                'sort_order': 15,
                'extra_data': {
                    'category': 'edge_detection',
                    'performance': 'medium',
                    'recommended': False,
                    'params': {
                        'canny_threshold1': {
                            'default': 50,
                            'type': 'int',
                            'range': [0, 255],
                            'description': '低阈值'
                        },
                        'canny_threshold2': {
                            'default': 150,
                            'type': 'int',
                            'range': [0, 255],
                            'description': '高阈值'
                        }
                    },
                    'use_cases': ['轮廓提取', '线条检测']
                }
            },
            'edge_sobel': {
                'label': 'Sobel边缘检测',
                'description': '梯度边缘检测，粗轮廓',
                'sort_order': 16,
                'extra_data': {
                    'category': 'edge_detection',
                    'performance': 'fast',
                    'recommended': False,
                    'params': {},
                    'use_cases': ['粗体文字', '快速检测']
                }
            },
            'edge_laplacian': {
                'label': 'Laplacian边缘检测',
                'description': '二阶导数边缘检测，全方向',
                'sort_order': 17,
                'extra_data': {
                    'category': 'edge_detection',
                    'performance': 'fast',
                    'recommended': False,
                    'params': {},
                    'use_cases': ['全方向边缘']
                }
            },
        }

        # 检查是否已存在数据
        existing_count = db.query(Dictionary).filter(
            Dictionary.dict_type == 'image_preprocessing'
        ).count()

        if existing_count > 0:
            print(f"⚠️ 已存在 {existing_count} 条图像预处理方法记录")
            confirm = input("是否删除并重新初始化？(y/N): ")
            if confirm.lower() != 'y':
                print("❌ 取消操作")
                return

            # 删除现有记录
            db.query(Dictionary).filter(
                Dictionary.dict_type == 'image_preprocessing'
            ).delete()
            db.commit()
            print(f"✅ 已删除 {existing_count} 条旧记录")

        # 插入新数据
        insert_count = 0
        for method_key in PREPROCESSING_METHODS:
            if method_key not in methods_config:
                print(f"⚠️ 跳过未配置的方法: {method_key}")
                continue

            config = methods_config[method_key]

            dict_item = Dictionary(
                dict_type='image_preprocessing',
                dict_key=method_key,
                dict_value=config['label'],
                dict_label=config['label'],
                dict_description=config['description'],
                sort_order=config['sort_order'],
                is_active=True,
                extra_data=json.dumps(config['extra_data'], ensure_ascii=False, indent=2),
                created_by='system',
                remark=f"图像预处理方法：{config['label']}"
            )

            db.add(dict_item)
            insert_count += 1
            print(f"  [{insert_count:2d}] 添加方法: {method_key} ({config['label']})")

        db.commit()

        print(f"\n✅ 成功初始化 {insert_count} 条图像预处理方法记录")

        # 显示分类统计
        print("\n" + "=" * 80)
        print("分类统计")
        print("=" * 80)

        categories = {}
        for method_key, config in methods_config.items():
            category = config['extra_data']['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(method_key)

        category_names = {
            'basic': '基础处理',
            'binarization': '二值化',
            'enhancement': '增强调整',
            'denoising': '降噪处理',
            'channel_split': 'RGB通道分离',
            'edge_detection': '边缘检测',
        }

        for category, methods in categories.items():
            category_name = category_names.get(category, category)
            print(f"\n【{category_name}】({len(methods)}种)")
            for method in methods:
                config = methods_config[method]
                recommended = "✅ 推荐" if config['extra_data']['recommended'] else ""
                print(f"  - {method}: {config['label']} {recommended}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def main():
    """主函数"""
    init_preprocessing_methods_dict()
    print("\n" + "=" * 80)
    print("初始化完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
