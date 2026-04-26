# 🌱 Social Board

一个轻量级的团队社交看板，让大家可以分享自己的研究方向、兴趣爱好、技能标签和联系方式，方便互相认识和交流。

![Flask](https://img.shields.io/badge/Flask-3.x-blue)
![SQLite](https://img.shields.io/badge/SQLite-3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 功能

- **📝 发布信息**：填写姓名、研究方向、兴趣爱好、联系方式、MBTI、技能标签等
- **📷 头像上传**：支持 PNG/JPG/GIF/WebP，自动生成头像或上传照片
- **👤 个人详情页**：每个人都有自己的独立页面，可以写详细介绍
- **✏️ 编辑 & 删除**：发布后可以随时修改自己的信息（基于浏览器本地 token 验证）
- **🏷️ 技能标签**：用逗号分隔的技能会自动渲染为彩色标签
- **🔮 MBTI 展示**：可选填 16 型人格，在卡片和详情页显示

## 技术栈

- **后端**：Python + Flask + SQLite
- **前端**：纯 HTML/CSS/JS（无框架依赖）
- **部署**：单文件 Flask 应用，开箱即用

## 快速开始

### 安装依赖

```bash
pip install flask
```

### 启动服务

```bash
python app.py
```

默认运行在 `http://127.0.0.1:5001`，浏览器打开即可使用。

### 生产部署

开发服务器仅用于本地测试。生产环境建议使用 Gunicorn：

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5001 app:app
```

## 项目结构

```
social/
├── app.py                 # Flask 后端主文件
├── requirements.txt       # Python 依赖
├── social.db              # SQLite 数据库（自动创建）
├── static/
│   ├── style.css          # 样式文件
│   └── uploads/           # 头像上传目录
├── templates/
│   ├── index.html         # 首页（看板 + 发布表单）
│   └── person.html        # 个人详情页
└── README.md
```

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| 姓名/昵称 | ✅ | 展示名称 |
| 研究方向 | ❌ | 工作/学习领域 |
| 兴趣爱好 | ❌ | 任意描述 |
| 联系方式 | ❌ | 微信/邮箱/飞书等 |
| 详细介绍 | ❌ | 长文本，支持换行 |
| 头像 | ❌ | 图片文件 |
| MBTI | ❌ | 16 型人格下拉选择 |
| 公司/学校 | ❌ | 所在机构 |
| 所在城市 | ❌ | 地理位置 |
| 个人网站 | ❌ | 外链，自动识别 |
| GitHub | ❌ | 用户名或完整链接 |
| 技能标签 | ❌ | 逗号分隔，渲染为标签 |

## 编辑与删除机制

发布信息时，后端会生成一个随机的 `edit_token`，前端将其存入浏览器的 `localStorage`。只有发布该信息的浏览器才能看到编辑/删除按钮，无需账号系统即可实现数据归属控制。

## License

MIT
