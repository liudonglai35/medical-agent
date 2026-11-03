# Medical Agent 持续执行 Runner

## 目标

解决“长程任务每执行一步就停止”的根本问题：ChatGPT 对话本身不是常驻进程，因此不能依靠一次聊天回复维持数小时/数天的工程执行。

项目现在采用：

```text
10分钟 Watchdog
      ↓
执行状态判断
      ↓
Persistent Runner
      ↓
Agent Executor
      ↓
代码/测试/提交/checkpoint
      ↓
PROJECT_STATE.json
      ↓
下一次 Watchdog
```

## 已实现

- `scripts/watchdog.py`：只负责监控连续性，不强制迭代。
- `scripts/execution_runner.py`：执行器适配层，负责启动真正的工程 Agent，并维护执行状态。
- `.github/workflows/project-watchdog.yml`：每10分钟巡检。

## 还缺的唯一基础设施

需要一台持续在线的 **self-hosted GitHub Actions runner**（服务器、PC、云主机均可），并在该 runner 环境中提供一个真正能够执行工程任务的 `AGENT_COMMAND`。

例如：

```bash
export AGENT_COMMAND='your-agent-cli --continue-project'
python3 scripts/execution_runner.py
```

`AGENT_COMMAND` 必须能够：

1. 读取 `PROJECT_STATE.json`；
2. 找到最高优先级未完成任务；
3. 修改代码/文档/测试；
4. 运行测试；
5. 更新 checkpoint、heartbeat、last_progress；
6. 遇到错误自行修复并重试；
7. 只有确实需要董事长决策时才写入 `WAITING_FOR_HUMAN`。

## 安全边界

Runner 不允许绕过 `WAITING_FOR_HUMAN`，也不应自动执行真实患者数据、医院生产系统、采购付款、公开发布等高风险操作。

## 关键判断

**Watchdog ≠ Executor。**

Watchdog 负责“发现项目有没有继续运行”；Runner/Agent 负责“让项目继续运行”。两者必须分离，否则监控只能发现问题而无法真正恢复。
