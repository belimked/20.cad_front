"""
快速测试 MySQL 数据库连接

直接运行此脚本测试数据库连接是否正常
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print(" 测试 MySQL 数据库连接")
    print("=" * 60)
    print()

    try:
        from src.utils.database import get_db_manager

        print("[1/3] 导入数据库模块... ✅")

        # 获取数据库管理器
        print("[2/3] 初始化数据库连接...")
        db = get_db_manager()
        print("      ✅ 数据库管理器已创建")

        # 测试连接
        print("[3/3] 测试数据库连接...")
        if db.test_connection():
            print("      ✅ 数据库连接成功!")
            print()

            # 获取数据库信息
            try:
                with db.session_scope() as session:
                    result = session.execute("SELECT DATABASE(), VERSION()")
                    db_name, version = result.fetchone()
                    print("数据库信息:")
                    print(f"  - 数据库名: {db_name}")
                    print(f"  - MySQL 版本: {version}")
            except Exception as e:
                print(f"      ⚠️ 无法获取数据库信息: {e}")

            print()
            print("=" * 60)
            print(" ✅ 数据库连接测试通过!")
            print("=" * 60)
            return True
        else:
            print("      ❌ 数据库连接失败!")
            print()
            print("=" * 60)
            print(" ❌ 数据库连接测试失败")
            print("=" * 60)
            return False

    except ImportError as e:
        print()
        print(f"❌ 导入失败: {e}")
        print()
        print("可能原因:")
        print("  1. pymysql 未安装")
        print("     解决: pip install pymysql")
        print("  2. sqlalchemy 未安装")
        print("     解决: pip install sqlalchemy")
        print()
        return False

    except Exception as e:
        print()
        print(f"❌ 连接失败: {e}")
        print()
        print("可能原因:")
        print("  1. MySQL 服务器未运行")
        print("  2. 数据库配置错误 (检查 src/utils/database.py)")
        print("  3. 网络无法访问数据库服务器")
        print("  4. 用户名或密码错误")
        print("  5. 数据库不存在")
        print()
        print("数据库配置 (src/utils/database.py 第 80-92 行):")
        print("  - 服务器: 10.3.19.189:3313")
        print("  - 数据库: cad_mgt")
        print("  - 用户名: fangda")
        print()
        return False
    finally:
        # 关闭连接
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

def show_config():
    """显示当前数据库配置"""
    print()
    print("=" * 60)
    print(" 当前数据库配置")
    print("=" * 60)
    print()
    print("配置文件: src/utils/database.py (第 80-92 行)")
    print()
    print("连接信息:")
    print("  服务器地址: 10.3.19.189")
    print("  端口:       3313")
    print("  用户名:     fangda")
    print("  密码:       123456")
    print("  数据库名:   cad_mgt")
    print("  字符集:     utf8mb4")
    print()
    print("连接字符串:")
    print("  mysql+pymysql://fangda:123456@10.3.19.189:3313/cad_mgt?charset=utf8mb4")
    print()
    print("=" * 60)
    print()

if __name__ == "__main__":
    show_config()

    success = test_connection()

    print()
    if success:
        print("✅ 下一步: 运行 python scripts\\init_autocad_config.py 初始化数据库表")
    else:
        print("❌ 请先解决数据库连接问题")
        print()
        print("参考文档:")
        print("  - DATABASE_CONNECTION_CONFIG.md  (详细配置说明)")
        print("  - DB_CONFIG_QUICK.md             (快速参考)")
    print()

    input("按 Enter 键退出...")
