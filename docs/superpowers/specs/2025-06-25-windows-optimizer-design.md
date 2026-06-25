# Windows 系统优化工具 — 设计规格

> 日期：2025-06-25  
> 状态：已批准  

---

## 1. 目标

搭建一个可运行的骨架，包含 Python Flask 后端 + 原生 HTML/CSS/JS 前端，覆盖 5 个 Windows 优化模块。每个模块暴露基础接口，前端提供对应面板。骨架可运行、可扩展。

---

## 2. 技术选型

| 层 | 技术 | 原因 |
|----|------|------|
| 后端 | Python + Flask + pywin32 | Windows API 原生支持，轻量，无需额外运行时 |
| 前端 | 原生 HTML/CSS/JS | 零依赖，单文件即可运行 |
| 通信 | REST JSON | 简单、浏览器原生支持 |

---

## 3. 目录结构

```
WinOperation-New/
├── backend/
│   ├── app.py                    # Flask 入口，API 路由注册，静态文件托管
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── system_info.py        # 系统信息与诊断
│   │   ├── cleanup.py            # 系统清理
│   │   ├── performance.py        # 性能调优
│   │   ├── registry.py           # 注册表操作
│   │   └── network.py            # 网络优化
│   └── utils/
│       └── __init__.py
├── frontend/
│   ├── index.html                # 单页应用入口
│   ├── css/
│   │   └── style.css             # 全局样式
│   └── js/
│       └── main.js               # 前端逻辑
└── docs/
    └── superpowers/
        └── specs/
            └── 2025-06-25-windows-optimizer-design.md   # 本文档
```

---

## 4. 模块接口

每个模块暴露以下接口，统一返回 `{"status": "ok|error", "data": ..., "error": ...}`。

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| system_info | `/api/system-info` | GET | 获取 CPU、内存、磁盘、运行时间 |
| cleanup | `/api/cleanup/temp-files` | POST | 清理临时文件，返回清理大小 |
| performance | `/api/performance/services` | GET | 获取服务列表 |
| performance | `/api/performance/services/<name>` | POST | 启/停服务 |
| registry | `/api/registry/read/<path>` | GET | 读取注册表键值 |
| registry | `/api/registry/write/<path>` | POST | 写入注册表键值（危险） |
| network | `/api/network/info` | GET | 获取网络适配器信息 |

---

## 5. 前端布局

- **左侧导航栏**：5 个模块入口 + 首页概览
- **右侧内容面板**：对应模块的操作界面
- 交互：点击导航切换面板，操作按钮触发 fetch，结果渲染到面板

---

## 6. 安全边界

- 写操作全部走 POST，前端弹确认框
- 注册表写入标注危险提示
- 需要管理员权限的操作返回中标记 `requires_admin: true`
- 骨架阶段先做接口定义和模拟数据，pywin32 实现在后续迭代填充

---

## 7. 数据流

```
浏览器 (fetch)
    ↓
Flask API Route
    ↓
module.get_*() / module.do_*()
    ↓
pywin32 → Windows API
    ↓
统一 JSON 响应
    ↓
前端渲染到面板
```

---

## 8. 实现顺序

1. 搭建目录结构
2. 实现 app.py + Flask 路由骨架
3. 填充 5 个模块的接口（先用模拟数据）
4. 编写前端单页应用
5. 联调验证可运行

---

## 9. 不在范围内（后续迭代）

- 实时监控图表
- 任务计划/定时执行
- 日志系统
- 多语言支持
