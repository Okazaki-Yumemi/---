# Metabolic City

《代谢之城：Cell City》是一个 React + TypeScript + Tailwind CSS 单页策略调控游戏。玩家扮演细胞代谢调度官，每回合选择 2 张行动卡，在不同生理情境下维持 ATP、葡萄糖、还原力、毒性压力和细胞健康的动态平衡。

## 运行方式

```bash
npm install
npm run dev
```

然后在浏览器打开 Vite 输出的本地地址，通常是 `http://localhost:5173`。

构建生产版本：

```bash
npm run build
```

## 内容位置

- 关卡数据：`src/data/levels.ts`
- 行动卡牌与知识解释：`src/data/cards.ts`
- 回合规则与评分：`src/gameLogic.ts`
- 界面组件：`src/components`

## 游戏机制

- 每关 10 回合。
- 每回合必须选择 2 张行动卡。
- 所有核心状态范围为 0-100。
- ROS、NH3、ATP 过低、Glucose 极端值会通过稳态压力影响 CellHealth。
- 关卡结束后根据 ATP、Glucose、ROS、NH3、CellHealth 输出评分和“生化之道”。
