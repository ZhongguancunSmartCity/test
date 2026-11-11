# GitHub 分支保护与 PR 合并流程 —— 手动测试手册

本手册用于在**单账号**条件下，手动验证仓库的主分支保护规则、Pull Request 提交流程与合并流程。

仓库地址：<https://github.com/ZhongguancunSmartCity/test>

## 一、测试环境

| 项目 | 说明 |
| --- | --- |
| 保护机制 | Repository Ruleset（仓库规则集），非经典分支保护 |
| 规则集名称 | `protect-main-branch` |
| 作用分支 | 默认分支 `main`（`~DEFAULT_BRANCH`） |
| 执行状态 | `active`（生效中） |
| 本地仓库 | `D:\GEMFiles\Work\13.航天世纪\15.开源项目\具身智能\开源项目代码\test-repo` |
| 运行环境 | Windows + PowerShell，Python 3.8.1，Git 2.55.0 |

### 当前规则明细

规则集启用了三条规则：

1. **Restrict deletions** —— 禁止删除分支
2. **Require a pull request before merging** —— 合并前必须通过 PR
3. **Block force pushes** —— 禁止强制推送

其中「Require a pull request before merging」的关键参数：

| 参数 | 取值 | 含义 |
| --- | --- | --- |
| `required_approving_review_count` | `0` | 不强制要求审批人数 |
| `require_last_push_approval` | `true` | 最近一次推送必须由**推送者以外的人**批准 |
| `require_extra_approval_for_unattributed_changes` | `true` | Copilot 生成的 PR 需额外审批（默认开启，审批数为 0 时不生效） |
| `required_review_thread_resolution` | `true` | 合并前须解决所有会话 |
| `allowed_merge_methods` | merge / squash / rebase | 三种合并方式均允许 |

### 绕过列表（Bypass list）

规则集的 **Bypass list** 中已配置：

| 角色 | 绕过模式 |
| --- | --- |
| Organization Admin | For pull requests only |

**这一项是单账号能跑通合并流程的关键。** 因为 `require_last_push_approval` 为 `true`，而组织内只有你一个成员，无法自己批准自己的 PR；配置绕过列表后，管理员身份可以在 PR 页面上直接完成合并，无需第二个人参与审批。

> 绕过只对 **Pull Request** 生效，对直接推送不生效 —— 也就是说直推 `main` 依然会被拦截。

## 二、配置入口

设置两个参数的位置：

```
仓库首页 → Settings
         → Code, planning, and automation
         → Rulesets
         → Rulesets 标签
         → 点击 protect-main-branch
         → 右上角 Edit
         → Branch protections 区域
         → Require a pull request before merging
         → Additional settings（展开）
```

两个参数与界面文案的对应关系：

| API 字段 | 界面文案 |
| --- | --- |
| `require_last_push_approval` | Require approval of the most recent reviewable push |
| `require_extra_approval_for_unattributed_changes` | Require an additional approval for unattributed Copilot pull requests |

绕过列表在同一页面向下滚动，**Bypass list** 区块 → **Add people or teams** → 选择 **Repository admin** → 右侧下拉由 "Always allow" 改为 **For pull requests only** → 保存。

## 三、手动测试流程

### 阶段 0　确认起点干净

```powershell
cd "D:\GEMFiles\Work\13.航天世纪\15.开源项目\具身智能\开源项目代码\test-repo"
git status
git log --oneline -3
```

**预期**：`working tree clean`，最新一条提交为 `e7098c2 chore: 移除 bypass 链路验证用的临时说明文件`。

若换用新机器或新目录，则先克隆：

```powershell
git clone https://github.com/ZhongguancunSmartCity/test.git
cd test
```

克隆后本地默认分支即为 `main`，无需额外配置。

### 阶段 1　验证主分支保护生效（直推必须失败）

这一步是验收「主分支权限保护」，**必须先看到失败**。

```powershell
git checkout main
echo "probe" > probe.txt
git add probe.txt
git commit -m "test: 直推探针"
git push origin main
```

**预期输出（失败才对）**：

```text
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Changes must be made through a pull request.
 ! [remote rejected] main -> main (push declined due to repository rule violations)
```

清理现场：

```powershell
git reset --hard HEAD~1
Remove-Item probe.txt
```

> 若此处推送**成功**，说明规则未生效，应立即停止后续步骤并排查。

### 阶段 2　拉取代码并创建分支

```powershell
git checkout main
git pull origin main
git checkout -b feature/manual-test
```

**预期**：`Switched to a new branch 'feature/manual-test'`，`git branch` 中 `*` 指向该分支。

### 阶段 3　修改代码、提交并推送分支

以新增一个限幅工具函数为例：

```powershell
notepad embodied_utils\geometry.py
```

在文件末尾追加：

```python
def clamp(value, lower, upper):
    """将数值限制在 [lower, upper] 区间内。"""
    return max(lower, min(upper, value))
```

保存后提交并推送：

```powershell
git add embodied_utils\geometry.py
git commit -m "feat: 新增数值区间限幅工具函数"
git push -u origin feature/manual-test
```

**预期**：

```text
[new branch]      feature/manual-test -> feature/manual-test
branch 'feature/manual-test' set up to track 'origin/feature/manual-test'.
```

> 推送**特性分支**不受规则限制，只有推送 `main` 才会被拦截。

### 阶段 4　创建 Pull Request

**网页方式**：推送成功后终端会打印创建链接，直接打开最省事：

```text
https://github.com/ZhongguancunSmartCity/test/pull/new/feature/manual-test
```

确认 base 为 `main`、compare 为 `feature/manual-test`，填写标题与描述后点击 **Create pull request**。

**命令行方式**（需已安装并登录 GitHub CLI）：

```powershell
gh pr create --base main --head feature/manual-test --title "feat: 新增数值区间限幅工具函数" --body "手动测试 PR 流程"
```

**预期**：返回 PR 编号与链接，形如 `https://github.com/ZhongguancunSmartCity/test/pull/4`。

### 阶段 5　确认 CI 执行

PR 页面可见 **Checks** 区域，`CI / 单元测试` 应由黄色运行中转为绿色对勾。

本地也可先跑一遍确认代码本身无问题：

```powershell
python -m unittest discover -v
```

**预期**：`Ran 30 tests ... OK`。

> 本地环境为 Python 3.8.1，CI 使用 Python 3.11。现有代码两者均可运行，但后续新增语法时需留意 3.8 的兼容性。

### 阶段 6　合并 PR（关键步骤）

在 PR 页面点击绿色 **Merge pull request** → 确认 → **Confirm merge**。

因 `require_last_push_approval` 为 `true` 且组织内仅一个成员，页面通常提供两个按钮：

| 按钮 | 说明 |
| --- | --- |
| **Merge pull request** | 走绕过通道（管理员身份 + For pull requests only），无需第二人审批 ✅ **用这个** |
| **Merge without approval** | 绕过通道的另一种表述，同样可用 |

> 如果未配置绕过列表，此处会以 405 报错：
> `New changes require approval from someone other than the last pusher.`

**兜底方案**：若网页按钮不可用，可用 API 合并：

```powershell
$cred = cmd /c "git credential fill" 2>$null
$token = (($cred | Select-String '^password=') -replace '^password=','').Trim()
$h = @{ Authorization="Bearer $token"; Accept="application/vnd.github+json"; 'X-GitHub-Api-Version'='2022-11-28' }
$body = @{ merge_method='squash'; commit_title='feat: 新增数值区间限幅工具函数' } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/ZhongguancunSmartCity/test/pulls/4/merge" -Headers $h -Body ([Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json"
```

**预期**：`merged=True`，PR 页面状态变为紫色 **Merged**。

### 阶段 7　验证合并结果并清理分支

```powershell
git checkout main
git pull origin main
git log --oneline -3
```

**预期**：本地 `main` 出现新的 squash 提交（形如 `abc1234 feat: 新增数值区间限幅工具函数`），说明改动已落到主分支。

删除特性分支（本地与远程）：

```powershell
git branch -d feature/manual-test
git push origin --delete feature/manual-test
```

> `-d` 为安全删除，若提示未合并可改用 `-D` 强制删除。远程分支删除后，GitHub 通常会同步移除同名 PR 的分支引用。

## 四、验收清单

| 序号 | 验证项 | 预期结果 |
| --- | --- | --- |
| 1 | 直接推送 `main` | ❌ 被拒绝，报 `GH013` |
| 2 | 推送特性分支 | ✅ 成功 |
| 3 | 创建 PR | ✅ 返回编号与链接 |
| 4 | CI 单元测试 | ✅ 30 个用例通过 |
| 5 | 合并 PR | ✅ 走绕过通道，无需第二人 |
| 6 | `main` 分支更新 | ✅ 出现新提交 |
| 7 | 清理特性分支 | ✅ 本地与远程均删除 |

## 五、关于双人审批的补充

上述流程验证的是**单账号**跑通全链路。当前规则为 `required_approving_review_count: 0`（不强制审批人数）+ `require_last_push_approval: true`（由绕过列表兜底）。

若要额外验证「**必须两人**」的效果，需调整参数：

**界面**：Settings → Code, planning, and automation → Rulesets → `protect-main-branch` → Edit → Require a pull request before merging → **Required approving reviews** 改为 `1`。

**命令行**：

```powershell
$cred = cmd /c "git credential fill" 2>$null
$token = (($cred | Select-String '^password=') -replace '^password=','').Trim()
$h = @{ Authorization="Bearer $token"; Accept="application/vnd.github+json"; 'X-GitHub-Api-Version'='2022-11-28' }
$rs = Invoke-RestMethod "https://api.github.com/repos/ZhongguancunSmartCity/test/rulesets/27001188" -Headers $h
$rs.rules | Where-Object { $_.type -eq 'pull_request' } | ForEach-Object { $_.parameters.required_approving_review_count = 1 }
$payload = @{ name=$rs.name; target=$rs.target; enforcement=$rs.enforcement; conditions=$rs.conditions; rules=$rs.rules; bypass_actors=$rs.bypass_actors } | ConvertTo-Json -Depth 20
Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/ZhongguancunSmartCity/test/rulesets/27001188" -Headers $h -Body ([Text.Encoding]::UTF8.GetBytes($payload)) -ContentType "application/json"
```

改完后单账号将无法完成合并（绕过列表也无法豁免「自己批准自己」），此时必须引入第二个账号：

- 注册一个新的 GitHub 账号，在仓库 **Settings → Collaborators** 中邀请它，用该账号执行 Approve；
- 或邀请同事作为 reviewer。

测试完成后记得将 `required_approving_review_count` 改回 `0`。

## 六、常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 直推 `main` 报 `GH013` | 规则生效，符合预期 | 属正常保护行为，改走 PR 流程 |
| 合并报 405 `New changes require approval from someone other than the last pusher` | 缺少绕过配置 | 在 Bypass list 中添加 Repository Admin + For pull requests only |
| 合并时页面提示需要 review | 审批人数大于 0 | 调低 `required_approving_review_count`，或由第二个账号批准 |
| 合并接口返回 404 且 `mergeable_state` 为 `blocked` | GitHub 尚未刷新可合并状态 | 等待数十秒后重试 |
| `git push` 连接超时 | 网络未走代理 | 执行 `git config --global http.proxy http://127.0.0.1:7890` 与同值的 `https.proxy` |
| PowerShell 中文显示乱码 | 控制台编码不匹配 | 执行 `chcp 65001` 并设置 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` |

## 七、已执行的验证记录

| 日期 | PR | 内容 | 结果 |
| --- | --- | --- | --- |
| 2026-11-11 | #1 | 新增轨迹安全性检查与碰撞检测模块 | CI 通过，squash 合并成功 |
| 2026-11-11 | #2 | 验证绕过通道下 PR 合并链路 | 合并成功（`5707e2b`） |
| 2026-11-11 | #3 | 清理验证用临时文件 | CI 通过，合并成功（`e7098c2`） |

直推 `main` 的拦截行为亦已多次复现验证，均返回 `GH013`。
