# Task 5: 验证可运行

## Context
这是 Windows 系统优化工具项目的 Task 5。你需要安装依赖、启动 Flask 服务，并验证所有 API 端点可正常返回数据。

## 需求

### Step 1: 安装依赖
```powershell
cd C:\Users\Acer\WinOperation-New\backend
pip install -r requirements.txt
```

### Step 2: 启动服务（后台运行）
```powershell
cd C:\Users\Acer\WinOperation-New\backend
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden
Start-Sleep -Seconds 2
```

### Step 3: 测试所有 API 端点

依次运行以下命令验证每个端点：

```powershell
# 系统信息
Invoke-RestMethod -Uri "http://localhost:5000/api/system-info" -Method Get

# 系统清理
Invoke-RestMethod -Uri "http://localhost:5000/api/cleanup/temp-files" -Method Post -ContentType "application/json" -Body "{}"

# 性能 - 获取服务列表
Invoke-RestMethod -Uri "http://localhost:5000/api/performance/services" -Method Get

# 注册表读取
Invoke-RestMethod -Uri "http://localhost:5000/api/registry/read/SOFTWARE%5CMicrosoft?key=test" -Method Get

# 网络信息
Invoke-RestMethod -Uri "http://localhost:5000/api/network/info" -Method Get
```

### Step 4: 停止服务
```powershell
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
```

## 报告
完成后写入报告文件 `docs/superpowers/sdd/task-5-report.md`，包含：
- 每个 API 端点的测试结果
- 所有端点是否都返回了正确的 JSON 格式 `{"status": "ok", ...}`
- 任何错误或问题

## 注意
- 不要修改代码文件
- 只做测试和报告
- 如果发现 API 返回错误，记录具体错误信息
