# PowerShell 分支管理脚本 (Windows 兼容)

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# 颜色函数
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# 显示帮助信息
function Show-Help {
    Write-Host "🔧 分支管理脚本 (PowerShell 版本)" -ForegroundColor Cyan
    Write-Host "================================"
    Write-Host "用法: .\scripts\branch_management.ps1 [命令]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  status    - 查看分支状态"
    Write-Host "  sync      - 同步代码到内容分支"
    Write-Host "  switch    - 切换分支"
    Write-Host "  test      - 测试推送（无冲突验证）"
    Write-Host "  help      - 显示此帮助信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\scripts\branch_management.ps1 status"
    Write-Host "  .\scripts\branch_management.ps1 sync"
    Write-Host "  .\scripts\branch_management.ps1 test"
}

# 检查 Git 仓库
function Test-GitRepo {
    try {
        git rev-parse --git-dir | Out-Null
        return $true
    }
    catch {
        Write-Error "当前目录不是 Git 仓库"
        return $false
    }
}

# 查看分支状态
function Show-Status {
    Write-Info "分支状态概览"
    Write-Host "================================"
    
    $currentBranch = git branch --show-current
    Write-Host "📍 当前分支: $currentBranch"
    
    # 检查分支是否存在
    $branches = git branch -a
    
    if ($branches -match "main") {
        Write-Success "main 分支: 存在"
        $mainCommit = git rev-parse main
        Write-Host "   最新提交: $($mainCommit.Substring(0,8))"
    }
    else {
        Write-Error "main 分支: 不存在"
    }
    
    if ($branches -match "auto-content") {
        Write-Success "auto-content 分支: 存在"
        $contentCommit = git rev-parse auto-content
        Write-Host "   最新提交: $($contentCommit.Substring(0,8))"
    }
    else {
        Write-Warning "auto-content 分支: 不存在"
    }
    
    # 检查远程分支
    Write-Host ""
    Write-Info "远程分支状态:"
    
    $remoteBranches = git ls-remote --heads origin
    if ($remoteBranches -match "refs/heads/main") {
        Write-Success "远程 main 分支: 存在"
    }
    else {
        Write-Warning "远程 main 分支: 不存在"
    }
    
    if ($remoteBranches -match "refs/heads/auto-content") {
        Write-Success "远程 auto-content 分支: 存在"
    }
    else {
        Write-Warning "远程 auto-content 分支: 不存在"
    }
    
    # 检查工作目录状态
    Write-Host ""
    Write-Info "工作目录状态:"
    $status = git status --porcelain
    if ([string]::IsNullOrEmpty($status)) {
        Write-Success "工作目录干净"
    }
    else {
        Write-Warning "有未提交的更改:"
        git status --short
    }
}

# 同步代码到内容分支
function Sync-Code {
    Write-Info "同步代码到内容分支..."
    
    $currentBranch = git branch --show-current
    
    # 确保 auto-content 分支存在
    $branches = git branch -a
    if (-not ($branches -match "auto-content")) {
        Write-Error "auto-content 分支不存在"
        Write-Info "请先确保分支已创建，或联系管理员"
        return
    }
    
    # 如果有未提交的更改，询问是否提交
    $status = git status --porcelain
    if (-not [string]::IsNullOrEmpty($status)) {
        Write-Warning "检测到未提交的更改"
        $response = Read-Host "是否先提交这些更改? (Y/n)"
        if ($response -ne "n" -and $response -ne "N") {
            $commitMsg = Read-Host "请输入提交消息"
            git add .
            git commit -m $commitMsg
            Write-Success "更改已提交"
        }
    }
    
    # 推送当前分支
    if ($currentBranch -eq "main") {
        Write-Info "推送 main 分支..."
        git push origin main
    }
    
    # 切换到 auto-content 分支并合并代码
    Write-Info "切换到 auto-content 分支..."
    git checkout auto-content
    
    Write-Info "合并 main 分支的代码更改..."
    
    # 同步代码文件
    try {
        git checkout main -- scripts/ 2>$null
        git checkout main -- .github/ 2>$null
        git checkout main -- requirements.txt 2>$null
        git checkout main -- *.py 2>$null
        git checkout main -- *.md 2>$null
    }
    catch {
        Write-Info "某些文件可能不存在，继续..."
    }
    
    # 检查是否有更改
    $syncStatus = git status --porcelain
    if (-not [string]::IsNullOrEmpty($syncStatus)) {
        git add .
        $syncCommitMsg = "🔄 Sync code from main branch $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $syncCommitMsg
        git push origin auto-content
        Write-Success "代码同步完成"
    }
    else {
        Write-Info "没有代码更改需要同步"
    }
    
    # 回到原分支
    git checkout $currentBranch
}

# 切换分支
function Switch-Branch {
    Write-Host "选择要切换的分支:"
    Write-Host "1) main (代码开发)"
    Write-Host "2) auto-content (查看生成的内容)"
    
    $choice = Read-Host "请选择 (1-2)"
    
    switch ($choice) {
        "1" {
            git checkout main
            Write-Success "已切换到 main 分支"
        }
        "2" {
            $branches = git branch -a
            if ($branches -match "auto-content") {
                git checkout auto-content
                Write-Success "已切换到 auto-content 分支"
            }
            else {
                Write-Error "auto-content 分支不存在"
            }
        }
        default {
            Write-Error "无效选择"
        }
    }
}

# 测试推送（验证无冲突）
function Test-Push {
    Write-Info "测试推送功能（验证分支分离效果）..."
    
    $currentBranch = git branch --show-current
    Write-Info "当前分支: $currentBranch"
    
    if ($currentBranch -ne "main") {
        Write-Warning "建议在 main 分支进行测试"
        $response = Read-Host "是否切换到 main 分支? (Y/n)"
        if ($response -ne "n" -and $response -ne "N") {
            git checkout main
        }
    }
    
    # 创建测试文件
    $testFile = "test-branch-separation-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    
    $testContent = @"
# 分支分离测试文件

## 测试信息
- **创建时间**: $(Get-Date)
- **分支**: $(git branch --show-current)
- **目的**: 验证分支分离策略是否有效

## 测试结果
如果您能成功推送此文件而没有遇到冲突，说明分支分离策略工作正常！

---
*此文件可以安全删除*
"@
    
    $testContent | Out-File -FilePath $testFile -Encoding UTF8
    Write-Success "测试文件已创建: $testFile"
    
    # 提交测试文件
    git add $testFile
    git commit -m "🧪 Test branch separation strategy"
    
    # 尝试推送
    Write-Info "尝试推送到 main 分支..."
    try {
        git push origin main
        Write-Success "🎉 推送成功！分支分离策略工作正常！"
        Write-Info "现在您可以安全地在 main 分支进行开发，不会再有冲突问题。"
    }
    catch {
        Write-Error "推送失败，可能仍有同步问题"
        Write-Info "建议检查远程仓库状态"
    }
    
    # 询问是否删除测试文件
    $response = Read-Host "是否删除测试文件? (Y/n)"
    if ($response -ne "n" -and $response -ne "N") {
        Remove-Item $testFile
        git add .
        git commit -m "🧹 Clean up test file"
        git push origin main
        Write-Success "测试文件已清理"
    }
}

# 主函数
function Main {
    if (-not (Test-GitRepo)) {
        return
    }
    
    switch ($Command.ToLower()) {
        "status" { Show-Status }
        "sync" { Sync-Code }
        "switch" { Switch-Branch }
        "test" { Test-Push }
        "help" { Show-Help }
        default {
            Write-Error "未知命令: $Command"
            Show-Help
        }
    }
}

# 运行主函数
Main
