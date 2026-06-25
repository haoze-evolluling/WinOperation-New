# Task 1: 搭建目录结构 + requirements.txt

## Context
这是 Windows 系统优化工具项目的第一个任务。你需要搭建项目的目录骨架，为后续的 Flask 后端和前端文件准备好位置。

## 需求

### 1. 创建 requirements.txt
路径：`backend/requirements.txt`
内容：
```
Flask>=2.0
pywin32>=305
```

### 2. 创建目录结构
使用 PowerShell 命令：
```powershell
New-Item -ItemType Directory -Path "backend\modules" -Force
New-Item -ItemType Directory -Path "backend\utils" -Force
New-Item -ItemType Directory -Path "frontend\css" -Force
New-Item -ItemType Directory -Path "frontend\js" -Force
```

### 3. 创建空 `__init__.py` 文件
- `backend/modules/__init__.py`（内容：`# modules 包初始化`）
- `backend/utils/__init__.py`（内容：`# utils 包初始化`）

## 报告
完成后写入报告文件 `docs/superpowers/sdd/task-1-report.md`，包含：
- 创建的文件列表
- 是否成功
- 任何问题或备注
