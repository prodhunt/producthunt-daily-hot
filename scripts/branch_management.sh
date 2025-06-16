#!/bin/bash
# 分支管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示帮助信息
show_help() {
    echo "🔧 分支管理脚本"
    echo "================================"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  setup     - 初始化分支分离设置"
    echo "  status    - 查看分支状态"
    echo "  sync      - 同步代码到内容分支"
    echo "  switch    - 切换分支"
    echo "  clean     - 清理和重置"
    echo "  help      - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 setup    # 初始化设置"
    echo "  $0 status   # 查看状态"
    echo "  $0 sync     # 同步代码"
}

# 检查 Git 仓库
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "当前目录不是 Git 仓库"
        exit 1
    fi
}

# 初始化分支分离设置
setup_branches() {
    print_info "开始初始化分支分离设置..."
    
    # 确保在 main 分支
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_warning "当前不在 main 分支，切换到 main..."
        git checkout main
    fi
    
    # 拉取最新代码
    print_info "拉取最新代码..."
    git pull origin main
    
    # 检查是否已存在 auto-content 分支
    if git show-ref --verify --quiet refs/heads/auto-content; then
        print_warning "auto-content 分支已存在"
        read -p "是否重新创建? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git branch -D auto-content
            print_info "已删除旧的 auto-content 分支"
        else
            print_info "保留现有分支"
            return 0
        fi
    fi
    
    # 创建 auto-content 分支
    print_info "创建 auto-content 分支..."
    git checkout -b auto-content
    
    # 推送到远程
    print_info "推送 auto-content 分支到远程..."
    git push -u origin auto-content
    
    # 回到 main 分支
    git checkout main
    
    print_success "分支分离设置完成！"
    print_info "现在您可以："
    echo "  - 在 main 分支进行代码开发"
    echo "  - GitHub Actions 会在 auto-content 分支生成内容"
    echo "  - 两个分支互不干扰"
}

# 查看分支状态
show_status() {
    print_info "分支状态概览"
    echo "================================"
    
    current_branch=$(git branch --show-current)
    echo "📍 当前分支: $current_branch"
    
    # 检查分支是否存在
    if git show-ref --verify --quiet refs/heads/main; then
        print_success "main 分支: 存在"
        main_commit=$(git rev-parse main)
        echo "   最新提交: ${main_commit:0:8}"
    else
        print_error "main 分支: 不存在"
    fi
    
    if git show-ref --verify --quiet refs/heads/auto-content; then
        print_success "auto-content 分支: 存在"
        content_commit=$(git rev-parse auto-content)
        echo "   最新提交: ${content_commit:0:8}"
    else
        print_warning "auto-content 分支: 不存在"
    fi
    
    # 检查远程分支
    echo ""
    print_info "远程分支状态:"
    if git ls-remote --heads origin main > /dev/null 2>&1; then
        print_success "远程 main 分支: 存在"
    else
        print_warning "远程 main 分支: 不存在"
    fi
    
    if git ls-remote --heads origin auto-content > /dev/null 2>&1; then
        print_success "远程 auto-content 分支: 存在"
    else
        print_warning "远程 auto-content 分支: 不存在"
    fi
    
    # 检查工作目录状态
    echo ""
    print_info "工作目录状态:"
    if [ -z "$(git status --porcelain)" ]; then
        print_success "工作目录干净"
    else
        print_warning "有未提交的更改:"
        git status --short
    fi
}

# 同步代码到内容分支
sync_code() {
    print_info "同步代码到内容分支..."
    
    current_branch=$(git branch --show-current)
    
    # 确保 auto-content 分支存在
    if ! git show-ref --verify --quiet refs/heads/auto-content; then
        print_error "auto-content 分支不存在，请先运行 setup"
        exit 1
    fi
    
    # 如果有未提交的更改，先提交
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "检测到未提交的更改"
        read -p "是否先提交这些更改? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            read -p "请输入提交消息: " commit_msg
            git add .
            git commit -m "$commit_msg"
            print_success "更改已提交"
        fi
    fi
    
    # 推送当前分支
    if [ "$current_branch" = "main" ]; then
        print_info "推送 main 分支..."
        git push origin main
    fi
    
    # 切换到 auto-content 分支并合并 main 的代码更改
    print_info "切换到 auto-content 分支..."
    git checkout auto-content
    
    print_info "合并 main 分支的代码更改..."
    # 只合并代码文件，不合并 data 目录
    git checkout main -- scripts/
    git checkout main -- .github/
    git checkout main -- requirements.txt
    git checkout main -- *.md
    git checkout main -- *.py
    
    # 检查是否有更改
    if [ -n "$(git status --porcelain)" ]; then
        git add .
        git commit -m "🔄 Sync code from main branch $(date '+%Y-%m-%d %H:%M:%S')"
        git push origin auto-content
        print_success "代码同步完成"
    else
        print_info "没有代码更改需要同步"
    fi
    
    # 回到原分支
    git checkout "$current_branch"
}

# 切换分支
switch_branch() {
    echo "选择要切换的分支:"
    echo "1) main (代码开发)"
    echo "2) auto-content (查看生成的内容)"
    read -p "请选择 (1-2): " choice
    
    case $choice in
        1)
            git checkout main
            print_success "已切换到 main 分支"
            ;;
        2)
            if git show-ref --verify --quiet refs/heads/auto-content; then
                git checkout auto-content
                print_success "已切换到 auto-content 分支"
            else
                print_error "auto-content 分支不存在，请先运行 setup"
            fi
            ;;
        *)
            print_error "无效选择"
            ;;
    esac
}

# 清理和重置
clean_reset() {
    print_warning "这将重置分支设置，请谨慎操作！"
    read -p "确定要继续吗? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "操作已取消"
        return 0
    fi
    
    # 切换到 main 分支
    git checkout main
    
    # 删除本地 auto-content 分支
    if git show-ref --verify --quiet refs/heads/auto-content; then
        git branch -D auto-content
        print_info "已删除本地 auto-content 分支"
    fi
    
    # 删除远程 auto-content 分支
    if git ls-remote --heads origin auto-content > /dev/null 2>&1; then
        git push origin --delete auto-content
        print_info "已删除远程 auto-content 分支"
    fi
    
    print_success "清理完成"
}

# 主函数
main() {
    check_git_repo
    
    case "${1:-help}" in
        setup)
            setup_branches
            ;;
        status)
            show_status
            ;;
        sync)
            sync_code
            ;;
        switch)
            switch_branch
            ;;
        clean)
            clean_reset
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
