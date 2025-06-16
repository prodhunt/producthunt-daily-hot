#!/bin/bash
# 智能推送脚本 - 自动处理同步问题

set -e  # 遇到错误立即退出

echo "🚀 智能推送脚本启动..."
echo "================================"

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 当前分支: $CURRENT_BRANCH"

# 检查是否有未提交的更改
if [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️ 没有未提交的更改"
    echo "💡 建议: 先做一些更改再运行此脚本"
    exit 0
fi

echo "📝 检测到未提交的更改:"
git status --short

# 询问用户是否继续
read -p "🤔 是否继续推送这些更改? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 用户取消操作"
    exit 0
fi

# 提交消息
read -p "📝 请输入提交消息 (默认: Update code): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Update code"}

echo ""
echo "🔄 开始智能同步流程..."
echo "================================"

# 1. 暂存当前更改
echo "📦 暂存当前更改..."
git add .
git commit -m "$COMMIT_MSG"
echo "✅ 更改已提交到本地"

# 2. 获取远程信息
echo "📡 获取远程仓库信息..."
git fetch origin

# 3. 检查是否有远程更新
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ 本地和远程已同步，直接推送..."
    git push origin $CURRENT_BRANCH
    echo "🎉 推送成功！"
    exit 0
fi

echo "⚠️ 检测到远程有新提交，需要同步..."

# 4. 显示远程新提交
echo "📋 远程新提交:"
git log HEAD..origin/$CURRENT_BRANCH --oneline

# 5. 检查是否有冲突的文件
echo "🔍 检查潜在冲突..."
CONFLICT_FILES=$(git diff --name-only HEAD origin/$CURRENT_BRANCH)

if [ -n "$CONFLICT_FILES" ]; then
    echo "⚠️ 以下文件可能有冲突:"
    echo "$CONFLICT_FILES"
    
    # 检查是否都是自动生成的文件
    AUTO_FILES_ONLY=true
    while IFS= read -r file; do
        if [[ ! "$file" =~ ^data/.*\.md$ ]]; then
            AUTO_FILES_ONLY=false
            break
        fi
    done <<< "$CONFLICT_FILES"
    
    if [ "$AUTO_FILES_ONLY" = true ]; then
        echo "✅ 冲突文件都是自动生成的内容，可以安全合并"
    else
        echo "⚠️ 检测到代码文件冲突，需要手动处理"
        read -p "🤔 是否继续自动合并? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ 用户选择手动处理"
            echo "💡 建议执行: git pull --rebase origin $CURRENT_BRANCH"
            exit 1
        fi
    fi
fi

# 6. 执行 rebase
echo "🔄 执行 rebase 合并..."
if git pull --rebase origin $CURRENT_BRANCH; then
    echo "✅ Rebase 成功"
else
    echo "❌ Rebase 失败，可能有冲突"
    echo "💡 请手动解决冲突后执行:"
    echo "   git add ."
    echo "   git rebase --continue"
    echo "   git push origin $CURRENT_BRANCH"
    exit 1
fi

# 7. 推送到远程
echo "🚀 推送到远程仓库..."
if git push origin $CURRENT_BRANCH; then
    echo "🎉 推送成功！"
    
    # 显示最终状态
    echo ""
    echo "📊 推送完成状态:"
    echo "- 本地提交: $(git log -1 --oneline)"
    echo "- 远程同步: ✅"
    echo "- 分支: $CURRENT_BRANCH"
else
    echo "❌ 推送失败"
    exit 1
fi

echo ""
echo "✨ 智能推送完成！"
