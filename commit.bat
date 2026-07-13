@echo off
REM ============================================================
REM 投资观察站 — 标准化提交脚本 (Windows)
REM ============================================================
REM 用法:
REM   commit                   交互式提交
REM   commit "feat(dashboard): 新增功能"
REM   commit -a "fix(api): 修复bug"
REM ============================================================
setlocal enabledelayedexpansion

cd /d "E:\投资工具自用"

REM 检查是否有未暂存的变更
git diff --quiet
if errorlevel 1 (
    echo ⚠️  发现未暂存的变更，先展示状态：
    git status -s
    echo.
    set /p STAGE="是否自动 git add . ？(Y/n): "
    if /i "!STAGE!"=="n" (
        echo 请手动 git add 后再运行提交。
        exit /b 1
    )
    git add .
    echo ✅ 已暂存所有变更。
    echo.
)

REM 如果没有提供提交信息，进入交互模式
if "%~1"=="" goto interactive

REM 直接提交模式
set MSG=%~1
if "%~2"=="-b" (
    REM 带正文的提交
    set BODY=%~3
    git commit -m "!MSG!" -m "!BODY!"
) else (
    git commit -m "!MSG!"
)
goto end

:interactive
echo ==========================================================
echo  投资观察站 — 标准化提交
echo ==========================================================
echo.
echo 请选择提交类型：
echo   [1] feat     新功能
echo   [2] fix      修复Bug
echo   [3] refactor 代码重构
echo   [4] data     数据更新
echo   [5] config   配置变更
echo   [6] style    样式调整
echo   [7] docs     文档更新
echo   [8] chore    构建/工具
echo   [9] 自定义
echo.
set /p TYPE_NUM="请选择 (1-9): "

if "!TYPE_NUM!"=="1" set TYPE=feat
if "!TYPE_NUM!"=="2" set TYPE=fix
if "!TYPE_NUM!"=="3" set TYPE=refactor
if "!TYPE_NUM!"=="4" set TYPE=data
if "!TYPE_NUM!"=="5" set TYPE=config
if "!TYPE_NUM!"=="6" set TYPE=style
if "!TYPE_NUM!"=="7" set TYPE=docs
if "!TYPE_NUM!"=="8" set TYPE=chore
if "!TYPE_NUM!"=="9" set /p TYPE="输入自定义类型: "

echo.
echo 请选择影响范围：
echo   [1] dashboard  四因子看板
echo   [2] industry   产业逻辑
echo   [3] review     复盘工具
echo   [4] volume     量能监测
echo   [5] scoring    五维打分
echo   [6] api        数据接口
echo   [7] data       数据层
echo   [8] ui         用户界面
echo   [9] hooks      Git Hooks
echo   [0] 全局/其他
echo.
set /p SCOPE_NUM="请选择 (0-9): "

if "!SCOPE_NUM!"=="1" set SCOPE=dashboard
if "!SCOPE_NUM!"=="2" set SCOPE=industry
if "!SCOPE_NUM!"=="3" set SCOPE=review
if "!SCOPE_NUM!"=="4" set SCOPE=volume
if "!SCOPE_NUM!"=="5" set SCOPE=scoring
if "!SCOPE_NUM!"=="6" set SCOPE=api
if "!SCOPE_NUM!"=="7" set SCOPE=data
if "!SCOPE_NUM!"=="8" set SCOPE=ui
if "!SCOPE_NUM!"=="9" set SCOPE=hooks
if "!SCOPE_NUM!"=="0" set SCOPE=

echo.
set /p SUBJECT="请输入提交标题 (不超过50字): "

echo.
echo 是否需要添加正文说明？(直接回车跳过)
set /p BODY="正文: "

if "!SCOPE!"=="" (
    set FULL_MSG=!TYPE!: !SUBJECT!
) else (
    set FULL_MSG=!TYPE!(!SCOPE!): !SUBJECT!
)

echo.
echo ==========================================================
echo  提交预览:
echo    !FULL_MSG!
if not "!BODY!"=="" (
    echo    ---
    echo    !BODY!
)
echo ==========================================================
echo.
set /p CONFIRM="确认提交？(Y/n): "

if /i "!CONFIRM!"=="n" (
    echo ❌ 已取消提交。
    exit /b 0
)

if "!BODY!"=="" (
    git commit -m "!FULL_MSG!"
) else (
    git commit -m "!FULL_MSG!" -m "!BODY!"
)

:end
if errorlevel 1 (
    echo ❌ 提交失败，请检查错误信息。
) else (
    echo ✅ 提交成功！
    echo.
    echo 提示：运行 git push 推送到远程仓库。
)
