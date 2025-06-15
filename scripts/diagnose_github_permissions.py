#!/usr/bin/env python3
"""
诊断 GitHub Actions 权限问题
"""

import os
import requests
import json

def check_pat_permissions():
    """检查 PAT 权限"""
    print("🔑 检查 PAT 权限...")
    
    pat = os.getenv("PAT")
    if not pat:
        print("❌ 未找到 PAT 环境变量")
        return False
    
    # 检查 PAT 格式
    if not pat.startswith('ghp_'):
        print("⚠️ PAT 格式可能不正确（应该以 ghp_ 开头）")
    
    # 测试 PAT 权限
    headers = {
        'Authorization': f'token {pat}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # 测试基本权限
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ PAT 有效，用户: {user_info.get('login')}")
        else:
            print(f"❌ PAT 无效，状态码: {response.status_code}")
            return False
        
        # 检查仓库权限
        repo = os.getenv("GITHUB_REPOSITORY", "prodhunt/producthunt-daily-hot")
        response = requests.get(f'https://api.github.com/repos/{repo}', headers=headers)
        
        if response.status_code == 200:
            repo_info = response.json()
            permissions = repo_info.get('permissions', {})
            print(f"✅ 仓库访问权限:")
            print(f"  - 读取: {permissions.get('pull', False)}")
            print(f"  - 写入: {permissions.get('push', False)}")
            print(f"  - 管理: {permissions.get('admin', False)}")
            
            if not permissions.get('push', False):
                print("❌ PAT 没有推送权限！")
                return False
        else:
            print(f"❌ 无法访问仓库，状态码: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查 PAT 权限时出错: {e}")
        return False

def check_github_token():
    """检查 GITHUB_TOKEN"""
    print("\n🔑 检查 GITHUB_TOKEN...")
    
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ 未找到 GITHUB_TOKEN 环境变量")
        return False
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # 检查 token 权限
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            print("✅ GITHUB_TOKEN 有效")
        else:
            print(f"❌ GITHUB_TOKEN 无效，状态码: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查 GITHUB_TOKEN 时出错: {e}")
        return False

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("=" * 50)
    
    print("1. **检查 PAT 配置**:")
    print("   - 访问: https://github.com/settings/tokens")
    print("   - 确保 PAT 有 'repo' 权限")
    print("   - 确保 PAT 没有过期")
    
    print("\n2. **检查仓库 Secrets**:")
    print("   - 进入仓库 Settings > Secrets and variables > Actions")
    print("   - 确认 'PAT' secret 存在且值正确")
    
    print("\n3. **检查工作流权限**:")
    print("   - 确保工作流文件中有 'permissions: contents: write'")
    print("   - 检查仓库设置中的 Actions 权限")
    
    print("\n4. **使用 GITHUB_TOKEN（备选方案）**:")
    print("   - 如果 PAT 有问题，可以使用内置的 GITHUB_TOKEN")
    print("   - 需要确保仓库设置允许 Actions 写入")

def check_repository_settings():
    """检查仓库设置"""
    print("\n⚙️ 检查仓库设置...")
    
    repo = os.getenv("GITHUB_REPOSITORY", "prodhunt/producthunt-daily-hot")
    pat = os.getenv("PAT")
    
    if not pat:
        print("❌ 无法检查仓库设置（缺少 PAT）")
        return
    
    headers = {
        'Authorization': f'token {pat}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # 检查仓库的 Actions 设置
        response = requests.get(f'https://api.github.com/repos/{repo}/actions/permissions', headers=headers)
        
        if response.status_code == 200:
            actions_permissions = response.json()
            print(f"✅ Actions 权限设置:")
            print(f"  - 启用状态: {actions_permissions.get('enabled', 'unknown')}")
            print(f"  - 允许的操作: {actions_permissions.get('allowed_actions', 'unknown')}")
        else:
            print(f"⚠️ 无法获取 Actions 权限设置，状态码: {response.status_code}")
        
        # 检查默认工作流权限
        response = requests.get(f'https://api.github.com/repos/{repo}/actions/permissions/workflow', headers=headers)
        
        if response.status_code == 200:
            workflow_permissions = response.json()
            print(f"✅ 工作流默认权限:")
            print(f"  - 默认权限: {workflow_permissions.get('default_workflow_permissions', 'unknown')}")
            print(f"  - 可以批准 PR: {workflow_permissions.get('can_approve_pull_request_reviews', 'unknown')}")
        else:
            print(f"⚠️ 无法获取工作流权限设置")
            
    except Exception as e:
        print(f"❌ 检查仓库设置时出错: {e}")

def main():
    """主诊断函数"""
    print("🔍 GitHub Actions 权限诊断")
    print("=" * 50)
    
    # 显示环境信息
    print(f"📍 仓库: {os.getenv('GITHUB_REPOSITORY', '未设置')}")
    print(f"📍 分支: {os.getenv('GITHUB_REF', '未设置')}")
    print(f"📍 Actor: {os.getenv('GITHUB_ACTOR', '未设置')}")
    
    # 检查权限
    pat_ok = check_pat_permissions()
    github_token_ok = check_github_token()
    
    # 检查仓库设置
    check_repository_settings()
    
    # 总结和建议
    print(f"\n📊 诊断结果:")
    print(f"- PAT 权限: {'✅ 正常' if pat_ok else '❌ 有问题'}")
    print(f"- GITHUB_TOKEN: {'✅ 正常' if github_token_ok else '❌ 有问题'}")
    
    if not pat_ok and not github_token_ok:
        print("\n❌ 两种 Token 都有问题，需要修复权限配置")
    elif pat_ok:
        print("\n✅ 建议使用 PAT 进行推送")
    elif github_token_ok:
        print("\n✅ 建议使用 GITHUB_TOKEN 进行推送")
    
    suggest_solutions()

if __name__ == "__main__":
    main()
