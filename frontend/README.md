# Frontend - AI 模拟面试系统

基于 Vue 3 + Vite + Pinia + Vue Router 的前端应用。

## 开发

```bash
npm install
npm run dev
```

## 构建

```bash
npm run build
```

## 技术栈

| 依赖 | 用途 |
|------|------|
| Vue 3 | UI 框架 |
| Vite 8 | 构建工具 |
| Vue Router 4 | 路由管理 |
| Pinia 3 | 状态管理 |
| ECharts 6 | 数据可视化（雷达图、评分图） |

## 设计系统

- 无外部 UI 框架依赖，纯 CSS 变量 Design Token 系统
- 主色：Indigo-600 (#4f46e5)
- 字体：Inter
- 8px 网格间距系统
- 详细 Token 定义见 `src/style.css`
