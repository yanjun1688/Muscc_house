# Music House 项目

## 项目概述
Music House 是一个集成了Spotify API的音乐应用，提供音乐播放和管理功能。项目采用Django作为后端框架，React作为前端框架。

## 功能特性
- 音乐播放功能
- Spotify API集成
- 用户友好的界面(Material-UI)
- 前后端分离架构

## 技术栈
### 后端
- Django
- Django REST framework (推断)
- SQLite数据库

### 前端
- React 17
- Webpack 5
- Material-UI 4
- React Router 5

### 第三方服务
- Spotify API集成

## 项目结构
```
Music_house_django/
├── Music_house/
│   ├── Api/ - 主API应用
│   │   ├── models.py - 数据模型
│   │   ├── views.py - 业务逻辑
│   │   ├── serializers.py - 数据序列化
│   │   └── urls.py - 路由配置
│   ├── spotify/ - Spotify集成应用
│   │   ├── credentials.py - API认证
│   │   ├── util.py - 工具函数
│   │   └── views.py - Spotify相关逻辑
│   ├── frontend/ - 前端应用
│   │   ├── src/ - React源代码
│   │   ├── static/ - 静态资源
│   │   └── templates/ - Django模板
│   └── Music_house/ - Django主配置
│       ├── settings.py - 项目配置
│       └── urls.py - 主路由
├── db.sqlite3 - 数据库文件
└── manage.py - Django管理脚本
```

## 安装与运行
### 后端
1. 创建并激活虚拟环境:
```bash
python -m venv venv_name
source venv_name/bin/activate  # Linux/Mac
venv_name\Scripts\activate     # Windows
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 运行开发服务器:
```bash
python manage.py runserver
```

### 前端
1. 进入frontend目录:
```bash
cd Music_house_django/Music_house/frontend
```

2. 安装依赖:
```bash
npm install
```

3. 开发模式:
```bash
npm run dev
```

4. 生产构建:
```bash
npm run build
```

## 配置说明
1. Spotify API:
   - 需要在spotify/credentials.py中配置Spotify API凭证
   - 获取Spotify开发者账号并创建应用

2. 数据库:
   - 默认使用SQLite
   - 如需更改，修改settings.py中的DATABASES配置

## 贡献指南
欢迎提交Pull Request。请确保:
1. 代码风格一致
2. 包含必要的测试
3. 更新相关文档