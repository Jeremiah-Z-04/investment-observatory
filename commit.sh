#!/bin/bash
# ============================================================
# 投资观察站 — 标准化提交脚本 (Git Bash / Linux)
# ============================================================
# 用法:
#   bash commit.sh                          交互式提交
#   bash commit.sh "feat(dashboard): 标题"   直接提交
#   bash commit.sh -a "fix(api): 标题"       自动add+提交
# ============================================================

set -e

cd "$(dirname "$0")"

AUTO_ADD=false

# 解析参数
if [ "$1" = "-a" ]; then
    AUTO_ADD=true
    shift
fi

# 检查未暂存文件
if ! git diff --quiet; then
    echo "⚠️  发现未暂存的变更:"
    git status -s
    echo ""
    if $AUTO_ADD; then
        git add .
        echo "✅ 已暂存所有变更。"
    else
        read -p "是否自动 git add . ？(Y/n): " STAGE
        if [ "$STAGE" = "n" ] || [ "$STAGE" = "N" ]; then
            echo "请手动 git add 后再运行提交。"
            exit 1
        fi
        git add .
        echo "✅ 已暂存所有变更。"
    fi
    echo ""
fi

# 如果有参数则直接提交
if [ -n "$1" ]; then
    git commit -m "$1"
    echo "✅ 提交成功！git push 推送至远程。"
    exit 0
fi

# 交互模式
echo "=========================================================="
echo " 投资观察站 — 标准化提交"
echo "=========================================================="
echo ""
echo "提交类型:"
echo "  1) feat      新功能"
echo "  2) fix       修复Bug"
echo "  3) refactor  代码重构"
echo "  4) data      数据更新"
echo "  5) config    配置变更"
echo "  6) style     样式调整"
echo "  7) docs      文档更新"
echo "  8) chore     构建/工具"
echo ""
read -p "请选择 (1-8): " TYPE_NUM

case $TYPE_NUM in
    1) TYPE="feat" ;;
    2) TYPE="fix" ;;
    3) TYPE="refactor" ;;
    4) TYPE="data" ;;
    5) TYPE="config" ;;
    6) TYPE="style" ;;
    7) TYPE="docs" ;;
    8) TYPE="chore" ;;
    *) TYPE="$TYPE_NUM" ;;
esac

echo ""
echo "影响范围:"
echo "  1) dashboard  四因子看板"
echo "  2) industry   产业逻辑"
echo "  3) review     复盘工具"
echo "  4) volume     量能监测"
echo "  5) scoring    五维打分"
echo "  6) api        数据接口"
echo "  7) data       数据层"
echo "  8) ui         用户界面"
echo "  9) hooks      Git Hooks"
echo "  0) 全局/不指定"
echo ""
read -p "请选择 (0-9): " SCOPE_NUM

case $SCOPE_NUM in
    1) SCOPE="dashboard" ;;
    2) SCOPE="industry" ;;
    3) SCOPE="review" ;;
    4) SCOPE="volume" ;;
    5) SCOPE="scoring" ;;
    6) SCOPE="api" ;;
    7) SCOPE="data" ;;
    8) SCOPE="ui" ;;
    9) SCOPE="hooks" ;;
    0) SCOPE="" ;;
    *) SCOPE="" ;;
esac

echo ""
read -p "请输入提交标题 (不超过50字): " SUBJECT

echo ""
read -p "正文说明 (可选，直接回车跳过): " BODY

if [ -z "$SCOPE" ]; then
    FULL_MSG="$TYPE: $SUBJECT"
else
    FULL_MSG="$TYPE($SCOPE): $SUBJECT"
fi

echo ""
echo "=========================================================="
echo " 提交预览:"
echo "   $FULL_MSG"
if [ -n "$BODY" ]; then
    echo "   ---"
    echo "   $BODY"
fi
echo "=========================================================="
echo ""
read -p "确认提交？(Y/n): " CONFIRM

if [ "$CONFIRM" = "n" ] || [ "$CONFIRM" = "N" ]; then
    echo "❌ 已取消提交。"
    exit 0
fi

if [ -n "$BODY" ]; then
    git commit -m "$FULL_MSG" -m "$BODY"
else
    git commit -m "$FULL_MSG"
fi

echo ""
echo "✅ 提交成功！"
echo "   运行 git push 推送到远程仓库。"
