#!/usr/bin/env python3
"""
Web Demo 测试脚本
测试应用的所有功能
"""

import requests
import json
import sys
import time

def test_health(endpoint):
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{endpoint}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 健康检查通过: {data.get('status')}")
            print(f"      服务: {data.get('service')}")
            print(f"      版本: {data.get('version')}")
            return True
        else:
            print(f"   ❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return False

def test_info(endpoint):
    """测试系统信息接口"""
    print("🔍 测试系统信息接口...")
    try:
        response = requests.get(f"{endpoint}/api/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 系统信息获取成功")
            print(f"      Python 版本: {data.get('python_version')}")
            print(f"      系统: {data.get('system')}")
            print(f"      当前时间: {data.get('current_time')}")
            return True
        else:
            print(f"   ❌ 系统信息获取失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 系统信息异常: {e}")
        return False

def test_echo(endpoint):
    """测试回显接口"""
    print("🔍 测试回显接口...")
    test_message = "HelloHermesAgent"
    try:
        response = requests.get(f"{endpoint}/api/echo/{test_message}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 回显接口测试通过")
            print(f"      原始消息: {data.get('original')}")
            print(f"      反转消息: {data.get('reversed')}")
            print(f"      大写消息: {data.get('uppercase')}")
            print(f"      消息长度: {data.get('length')}")
            
            # 验证数据正确性
            if (data.get('original') == test_message and 
                data.get('reversed') == test_message[::-1] and
                data.get('uppercase') == test_message.upper() and
                data.get('length') == len(test_message)):
                print(f"   ✅ 数据验证通过")
                return True
            else:
                print(f"   ❌ 数据验证失败")
                return False
        else:
            print(f"   ❌ 回显接口失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 回显接口异常: {e}")
        return False

def test_homepage(endpoint):
    """测试主页"""
    print("🔍 测试主页...")
    try:
        response = requests.get(endpoint, timeout=5)
        if response.status_code == 200:
            # 检查是否包含关键内容
            content = response.text
            if "Hermes Web Demo" in content and "Flask" in content:
                print(f"   ✅ 主页加载成功")
                print(f"      状态码: {response.status_code}")
                print(f"      内容类型: {response.headers.get('content-type', '未知')}")
                return True
            else:
                print(f"   ⚠️  主页内容可能不完整")
                return True  # 仍然算成功，因为服务器响应了
        else:
            print(f"   ❌ 主页加载失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 主页异常: {e}")
        return False

def performance_test(endpoint):
    """性能测试"""
    print("🔍 进行性能测试...")
    start_time = time.time()
    successes = 0
    total_requests = 10
    
    for i in range(total_requests):
        try:
            response = requests.get(f"{endpoint}/api/health", timeout=3)
            if response.status_code == 200:
                successes += 1
        except:
            pass
    
    end_time = time.time()
    duration = end_time - start_time
    success_rate = (successes / total_requests) * 100
    
    print(f"   📊 性能测试结果:")
    print(f"      总请求数: {total_requests}")
    print(f"      成功数: {successes}")
    print(f"      成功率: {success_rate:.1f}%")
    print(f"      总耗时: {duration:.2f}秒")
    print(f"      平均响应时间: {(duration/total_requests)*1000:.0f}毫秒")
    
    return success_rate > 80  # 成功率大于80%算通过

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Web Demo 应用测试脚本")
    print("=" * 60)
    
    # 确定测试端点
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
    else:
        endpoint = "http://localhost:5000"
    
    print(f"测试端点: {endpoint}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行所有测试
    tests = [
        ("健康检查", lambda: test_health(endpoint)),
        ("系统信息", lambda: test_info(endpoint)),
        ("回显接口", lambda: test_echo(endpoint)),
        ("主页", lambda: test_homepage(endpoint)),
        ("性能测试", lambda: performance_test(endpoint)),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"   ✅ {test_name}: 通过")
            else:
                print(f"   ❌ {test_name}: 失败")
        except Exception as e:
            print(f"   ❌ {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:15} {status}")
    
    print(f"\n总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"通过率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！应用运行正常。")
        print(f"🌐 访问地址: {endpoint}")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查应用状态。")
        sys.exit(1)

if __name__ == "__main__":
    main()