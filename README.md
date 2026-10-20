# 微信消息提示 · WeChatToast

[![release](https://img.shields.io/github/v/release/PepsiColaya/wechat-notifier)](https://github.com/PepsiColaya/wechat-notifier/releases/latest)
[![license](https://img.shields.io/github/license/PepsiColaya/wechat-notifier)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://github.com/PepsiColaya/wechat-notifier)

> 微信躲在后台时，也能一眼看到**谁发的、说了什么**。

> **第三方工具声明**：本项目为个人作品，与腾讯公司无关，未获其授权或认可。「微信」仅用于说明本工具适用的软件，不构成任何官方关联。程序只读取 Windows 通知中心，不修改、不注入微信客户端。图标为原创设计（靛蓝卡片造型），未使用微信官方标识。

![预览](docs/screenshot.png)

PC 微信最小化后，来消息只有任务栏闪一下，不看一眼根本不知道是谁找。这个小工具会在屏幕角落浮出一张卡片，直接告诉你会话名、发送者和消息内容，3 秒后自动淡出，不用再点开微信确认。

## 特性

- **悬浮卡片**：圆角 + 柔和阴影，显示「会话名 · 发送者」和消息正文（两行内，超出省略）
- **真实头像**：把头像图片按「会话名.png」放进 `avatars/` 目录即可自动显示，未匹配的用渐变首字兜底
- **自动消失**：默认 3 秒淡出，鼠标移上去暂停倒计时，移开继续
- **多条堆叠**：同时来多条会依次排列，超出同屏上限的自动排队
- **点击跳转**：点卡片直接把微信唤到前台
- **可视化调参**：内置设置面板，左侧拖滑块，右侧实时预览，所见即所得
- **配置永久保存**：改完自动落盘到 `%APPDATA%\WeChatToast\config.json`，重启、换 exe 位置都不会丢
- **深色 / 浅色主题**，宽度、缩放、圆角、阴影、透明度、位置、时长全部可调
- **托盘常驻**：支持暂停监听、单实例保护

![设置面板](docs/settings.png)

## 原理

先说结论：**这个工具不读微信的界面，也不碰它的数据库，而是读 Windows 通知中心。**

微信 4.x 把界面换成了 Qt 自绘渲染（窗口类是 `Qt51514QWindowIcon`，内部是 `MMUIRenderSubWindow`）。实测它的 UI Automation 控件树是空的——整个主窗口只有 3 个节点，拿不到任何会话或消息。所以「遍历控件树读会话列表」那套方案在 4.x 上完全失效。

但微信收到新消息时，会按系统规范向 Windows 推送 Toast 通知。用 `UserNotificationListener` 把通知读出来，文本结构非常规整：

| 行 | 含义 | 示例 |
|---|---|---|
| `text[0]` | 应用名 | `微信` |
| `text[1]` | 会话名 | `产品研发群` |
| `text[2]` | 发送者 + 正文 | `张伟 : 这个版本的接口文档我下午更新一下` |

好处是：**不注入微信进程、不读数据库、不碰内存**，微信小版本升级也不容易失效。

## 环境要求

- Windows 10 1809+ 或 Windows 11
- 微信 PC 版 4.x（3.9.x 走的也是系统通知，理论上同样可用）
- Python 3.10+（仅源码运行需要）

## 使用

### 方式一：直接跑 exe

从 [Releases](https://github.com/PepsiColaya/wechat-notifier/releases/latest) 下载 `WeChatToast.exe` 双击运行。托盘出现绿色「微」图标就是启动成功了，**没有主窗口是正常的**。

首次启动单文件 exe 需要解压，会等 3～8 秒。

### 方式二：源码运行

```bash
git clone https://github.com/PepsiColaya/wechat-notifier.git
cd wechat-notifier
pip install -r requirements.txt
python main.py
```

或者双击 `run.bat`。

### 打开设置

右键托盘图标 → **设置…**（双击托盘图标也可以）。

**改完不用点保存**——停手半秒后自动写入配置并即时生效，面板底部会闪一下「已自动保存」。直接关窗口也不会丢，关闭前会再存一次。

「在桌面试一下」会用当前参数弹一条真实卡片，方便确认实际效果。

## 前提条件

两个开关都必须打开，否则读不到消息：

1. **微信** → 设置 → 通知 → 开启「新消息通知」
2. **Windows** → 设置 → 隐私和安全性 → 通知 → 允许应用访问你的通知

程序启动时会检查通知访问权限，没授权会弹提示。

## 配置项

配置自动保存在：

| 运行方式 | 位置 |
|---|---|
| exe | `%APPDATA%\WeChatToast\config.json` |
| 源码 | 项目根目录 `config.json` |

放在 `%APPDATA%` 的好处是：exe 被移动、复制、重新下载覆盖，配置都还在。旧版本留在 exe 同目录的 `config.json` 会在首次启动时自动迁移过来。

设置面板覆盖了常用项，其余可直接改 `config.json`（改完重启程序生效）：

| 键 | 默认值 | 说明 |
|---|---|---|
| `theme` | `dark` | 主题，`dark` / `light` |
| `card_width` | `340` | 卡片宽度（px），240–560 |
| `scale` | `1.0` | 字号与内边距整体缩放，0.8–1.5 |
| `radius` | `14` | 圆角（px），0–24 |
| `shadow` | `16` | 阴影扩散范围（px），0–30 |
| `opacity` | `0.96` | 背景不透明度，0.4–1.0（文字始终不透明） |
| `gap` | `8` | 卡片间距（px），0–24 |
| `position` | `top-right` | 位置：`top-right` / `top-left` / `bottom-right` / `bottom-left` |
| `margin` | `22` | 距屏幕边缘（px） |
| `duration_ms` | `3000` | 停留时长（毫秒） |
| `max_visible` | `3` | 同屏最多几张 |
| `fade_in_ms` / `fade_out_ms` | `170` / `280` | 淡入淡出时长 |
| `hover_pause` | `true` | 鼠标悬停时暂停倒计时 |
| `click_to_open_wechat` | `true` | 点击卡片唤起微信 |
| `poll_interval_ms` | `1000` | 通知轮询间隔 |
| `ignore_sources` | `[]` | 不提醒的会话名，如 `["某工作群"]` |
| `avatar_dir` | 配置目录下 `avatars` | 头像图片目录 |

数值超出范围会自动夹紧到合法区间。

## 头像

微信 4.x 的通知里**不带头像**，本地头像缓存又是哈希命名、无法对应到会话名，所以程序不会自动抓取头像。

替代方案是「按名字匹配」：把头像图片命名成会话名，放进头像目录即可（默认 `%APPDATA%\WeChatToast\avatars`，设置面板里点「打开目录」可直接跳过去）。

```
avatars/
├── 产品研发群.png
├── 李静.jpg
└── 家里群.webp
```

- 支持 `png / jpg / jpeg / webp / bmp`
- 会话名要和微信里显示的**完全一致**（群名或备注名）
- 文件名里的 `\ / : * ? " < > |` 会被替换成 `_`
- 没匹配到的会话自动用渐变首字占位，不影响使用

设置面板里点「打开目录」可以直接跳过去。头像按修改时间缓存，换图后重启程序即可生效。

## 项目结构

```
wechat-notifier/
├── main.py              # 入口：托盘、单实例、信号桥接
├── config.py            # 配置默认值、读写、范围校验、自动迁移
├── logo.py              # 应用图标绘制（托盘/窗口/exe 共用）
├── watcher.py           # 读通知中心，解析微信消息
├── toast.py             # 悬浮卡片绘制与堆叠管理
├── settings_window.py   # 可视化设置面板（自动保存）
├── wechat.py            # 唤起微信主窗口
├── render_preview.py    # 渲染展示图（开发用）
├── config.json          # 源码运行时的配置文件
├── requirements.txt
├── build.bat            # 一键打包 exe
├── run.bat              # 源码方式启动
├── avatars/             # 头像图片（按会话名命名）
├── docs/                # 截图
└── tools/               # 开发期探测脚本（可忽略）
```

## 打包

```bash
pip install pyinstaller
build.bat
```

产物在 `dist/WeChatToast.exe`，约 39 MB（PySide6 占大头）。

## 已知限制

- **只读通知**，拿不到历史消息，也不能在卡片里直接回复
- 点击只能把微信唤到主窗口，**无法定位到具体某个会话**（4.x 自绘，外部点不进去）
- 图片 / 表情 / 语音消息在通知里没有正文，卡片会显示「（新消息）」
- 微信本身会合并同一会话的连续消息，此时可能只弹一次
- 你正开着微信、且正看着那个会话时，微信不发通知，所以不会弹卡片——这是符合预期的
- 微信若关闭了系统通知，本工具收不到任何东西

## 技术备注

`tools/` 下是开发时用来确认可行性的脚本：

- `probe_windows.py`：枚举微信顶层窗口，看窗口类和标题
- `dump_uia.py`：导出微信主窗口的 UIA 控件树（结论：空的）
- `test_notify.py`：验证通知访问权限与微信 Toast 的文本结构

如果你要适配其他微信版本，建议先跑这三个脚本确认可读性。

## License

[MIT](LICENSE)
