# 代谢之城 Cell City

这是一个 Python 3 + pygame 实现的 Windows 桌面小游戏。游戏采用回合制资源管理机制表达代谢生物化学思想，玩家扮演细胞代谢调度官，在不同生理情境下调控糖代谢、脂质代谢、氨基酸代谢和生物氧化，使细胞维持稳态。

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

- `main.py`：完整 pygame 游戏代码，包含关卡、卡牌、状态、地图、交互和结算。
- `requirements.txt`：pygame 与 PyInstaller 依赖。
- `build_exe.bat`：一键打包脚本。
