#!/usr/bin/env python3
"""proxy_test.py — 检查当前代理和镜像状态。

当网络相关操作（API调用、下载、搜索）异常时运行此脚本排查。
"""
import os
import sys
import socket

try:
    import requests
except ImportError:
    print("ERROR: requests not installed")
    print("pip install -i https://mirrors.aliyun.com/pypi/simple/ requests")
    sys.exit(1)

def check_proxy():
    """检查代理是否可用。"""
    proxies = {
        'http': os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy'),
        'https': os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'),
    }
    
    local_port = None
    for port in [7890, 7897, 7891, 8118, 1080]:
        try:
            s = socket.create_connection(('127.0.0.1', port), timeout=2)
            s.close()
            local_port = port
            break
        except:
            continue
    
    if local_port:
        print(f"[OK] Local proxy found on port {local_port}")
        # Try through local proxy
        test_proxies = {
            'http': f'http://127.0.0.1:{local_port}',
            'https': f'http://127.0.0.1:{local_port}'
        }
    else:
        print("[WARN] No local proxy detected on common ports (7890/7897/7891/8118/1080)")
        if not proxies['http'] and not proxies['https']:
            print("[INFO] No HTTP_PROXY/HTTPS_PROXY env vars set either")
        test_proxies = proxies if any(proxies.values()) else {}
    
    return local_port, test_proxies

def test_connectivity(proxies):
    """测试各关键服务的可达性。"""
    tests = [
        ("GitHub", "https://api.github.com", "需要代理"),
        ("npmjs", "https://registry.npmjs.org", "需要代理"),
        ("npmmirror", "https://registry.npmmirror.com", "国内直连"),
        ("HuggingFace", "https://huggingface.co", "需要代理"),
        ("OpenAI", "https://api.openai.com", "需要代理"),
        ("DashScope", "https://dashscope.aliyuncs.com", "国内直连"),
        ("Bing CN", "https://cn.bing.com", "国内直连"),
    ]
    
    results = []
    for name, url, note in tests:
        try:
            kwargs = {'timeout': 10}
            if proxies:
                kwargs['proxies'] = proxies
            resp = requests.get(url, **kwargs)
            status = f"OK ({resp.status_code})"
        except requests.exceptions.ProxyError:
            status = "PROXY ERROR"
        except requests.exceptions.Timeout:
            status = "TIMEOUT"
        except ConnectionError as e:
            status = f"CONNECTION FAILED: {str(e)[:60]}"
        except Exception as e:
            status = f"ERROR: {type(e).__name__}"
        
        marker = "✅" if "(OK)" in status and resp.status_code == 200 else "❌"
        print(f"  {marker} {name}: {status} ({note})")
        results.append((name, status))
    
    return results

if __name__ == '__main__':
    print("=" * 50)
    print("China Network Diagnostics")
    print("=" * 50)
    
    print("\n--- Proxy Check ---")
    local_port, proxies = check_proxy()
    
    print("\n--- Connectivity Tests ---")
    test_connectivity(proxies)
    
    print("\n--- Environment Variables ---")
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']:
        val = os.environ.get(key, '(not set)')
        if val != '(not set)':
            print(f"  {key}={val[:80]}...")
        else:
            print(f"  {key}=(not set)")
    
    print("\nDone.")
