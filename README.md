# 代谢之城 Cell City

这是一个 Python 3 + pygame 实现的 Windows 桌面小游戏。玩家扮演细胞代谢调度官，在不同生理情境下调控糖代谢、脂质代谢、氨基酸代谢和生物氧化，使细胞维持稳态。

## 本机运行

```bat
pip install -r requirements.txt
python main.py
```

## 打包为 Windows exe

双击运行：

```text
build_exe.bat
```

或在命令行执行：

```bat
python -m PyInstaller --onefile --windowed --name "代谢之城 Cell City" main.py
```

打包完成后，exe 会生成在 `dist` 目录中。老师电脑不需要安装 Python、Node.js、npm、VSCode，直接双击 exe 即可运行。

## 文件说明

- `main.py`：完整 pygame 游戏代码，包含界面状态机、关卡、卡牌、事件、激素模式、状态、地图、交互和结算。
- `requirements.txt`：pygame 与 PyInstaller 依赖。
- `build_exe.bat`：一键打包脚本。

## 作者信息

作者：刘培锐  
学号：525714910036

## 界面流程

- `TITLE`：开始界面。
- `MAIN_MENU`：主菜单。
- `TUTORIAL`：三页教程。
- `SCENARIO_SELECT`：五个生理情境关卡选择。
- `GAME`：回合制代谢调度主界面。
- `RESULT`：关卡结算。
- `ENCYCLOPEDIA`：生化图鉴。
- `FINAL_SUMMARY`：最终总结。
- `ABOUT`：关于作品与作者信息。
- `CHALLENGE_SETUP`：挑战模式设置。
- `CHALLENGE_RESULT`：挑战模式结算。

## 动效参数

主要动效集中在 `main.py` 的 `Game` 类顶部：

- `STATUS_SMOOTH_SPEED`：状态条数值平滑逼近速度。
- `CARD_ANIM_SPEED`：卡牌 hover、选中、点击反馈的过渡速度。
- `LOG_FADE_SPEED`：事件日志淡入速度。
- `PATH_DURATION`：代谢地图路径高亮和粒子动画持续时间。
- `INPUT_LOCK_SECONDS`：执行回合后的临时输入锁定时间。
