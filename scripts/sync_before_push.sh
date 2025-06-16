#!/bin/bash
# 推送前自动同步脚本

echo "🔄 推送前自动同步..."

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改，先暂存..."
    git stash push -m "Auto stash before sync $(date)"
    STASHED=true
else
    STASHED=false
fi

# 拉取远程更新
echo "📥 拉取远程更新..."
if git pull --rebase origin main; then
    echo "✅ 远程更新拉取成功"
else
    echo "❌ 拉取失败，可能有冲突"
    if [ "$STASHED" = true ]; then
        echo "🔄 恢复暂存的更改..."
        git stash pop
    fi
    exit 1
fi

# 恢复暂存的更改
if [ "$STASHED" = true ]; then
    echo "🔄 恢复暂存的更改..."
    if git stash pop; then
        echo "✅ 更改恢复成功"
    else
        echo "⚠️ 恢复更改时可能有冲突，请手动解决"
    fi
fi

echo "✅ 同步完成，现在可以安全推送了"
echo "💡 使用命令: git push origin main"
