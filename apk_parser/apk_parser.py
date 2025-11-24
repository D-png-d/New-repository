import os
import sys
import zipfile
from typing import Dict, List, Optional
import apkutils2


def parse_apk_permissions(apk_path: str) -> Dict[str, Optional[List[str]]]:
    result = {"success": False, "apk_path": apk_path, "permissions": None, "error": ""}
    try:
        # 基础文件检查
        if not os.path.exists(apk_path):
            result["error"] = f"文件不存在：{apk_path}"
            return result
        if not os.path.isfile(apk_path):
            result["error"] = f"路径不是文件：{apk_path}"
            return result
        if not apk_path.lower().endswith(".apk"):
            result["error"] = f"文件不是APK格式：{apk_path}"
            return result

        # 核心解析（适配库特性）
        apk = apkutils2.APK(apk_path)
        manifest = apk.get_manifest()  # 返回字典类型
        if not manifest:
            result["error"] = "APK中未找到AndroidManifest.xml"
            return result

        # 从字典提取权限
        permissions = []
        perm_list1 = manifest.get("uses-permission", [])
        perm_list2 = manifest.get("uses-permission-sdk-23", [])
        for perm in perm_list1 + perm_list2:
            perm_name = perm.get("android:name")
            if perm_name and perm_name.startswith("android.permission."):
                permissions.append(perm_name)

        result["success"] = True
        result["permissions"] = sorted(list(set(permissions)))
    except zipfile.BadZipFile:
        result["error"] = f"APK文件损坏：{apk_path}"
    except PermissionError:
        result["error"] = f"无读取权限：{apk_path}"
    except UnicodeDecodeError:
        result["error"] = f"编码解析失败：{apk_path}"
    except Exception as e:
        import traceback
        result["error"] = f"未知错误：{str(e)}\n{traceback.format_exc()}"
    return result


def print_parse_result(result: Dict[str, Optional[List[str]]]) -> None:
    """
    格式化打印解析结果（友好输出）

    Args:
        result (Dict): parse_apk_permissions函数的返回结果
    """
    print("=" * 60)
    print(f"APK文件路径：{result['apk_path']}")
    print("=" * 60)

    if result["success"]:
        print("✅ 解析成功！")
        print(f"\n📋 提取到的权限列表（共{len(result['permissions'])}个）：")
        if result["permissions"]:
            for idx, perm in enumerate(result["permissions"], 1):
                print(f"  {idx}. {perm}")
        else:
            print("  📌 该APK未声明任何android.permission权限")
    else:
        print("❌ 解析失败！")
        print(f"❓ 错误原因：{result['error']}")
    print("=" * 60)


if __name__ == "__main__":
    # 命令行参数校验：确保传入APK路径参数
    if len(sys.argv) != 2:
        print("🚫 使用方式错误！正确格式：")
        print("  Windows: python apk_parser.py <APK文件路径>")
        print("  Mac/Linux: python3 apk_parser.py <APK文件路径>")
        print("\n📌 示例：")
        print("  python apk_parser.py ./ApiDemos-debug.apk")
        print("  python apk_parser.py C:/apps/com.tencent.mm.apk")
        sys.exit(1)

    # 获取传入的APK路径
    target_apk_path = sys.argv[1]

    # 调用解析函数并打印结果
    parse_result = parse_apk_permissions(target_apk_path)
    print_parse_result(parse_result)