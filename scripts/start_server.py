#!/usr/bin/env python3
"""
三体AI教育版创作系统 - 本地Web服务器
提供GitBook风格的阅读和创作界面
"""

import http.server
import socketserver
import os
import json
from datetime import datetime

class SantiAIRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器，提供创作系统界面"""
    
    def do_GET(self):
        """处理GET请求"""
        # 如果是根路径，显示创作系统主页
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # 生成动态主页
            html_content = self.generate_dashboard()
            self.wfile.write(html_content.encode('utf-8'))
            return
            
        # 如果是API请求，返回JSON数据
        elif self.path.startswith('/api/'):
            self.handle_api_request()
            return
            
        # 其他情况使用默认文件服务
        super().do_GET()
    
    def generate_dashboard(self):
        """生成创作系统控制面板"""
        
        # 读取项目进度
        progress_data = self.get_progress_data()
        
        html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>三体AI教育版创作系统</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.8;
        }}
        .dashboard {{
            padding: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        .stat-card h3 {{
            margin: 0 0 10px;
            color: #2c3e50;
        }}
        .progress-bar {{
            background: #ecf0f1;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #3498db, #2ecc71);
            height: 100%;
            transition: width 0.3s ease;
        }}
        .books-section {{
            margin: 40px 0;
        }}
        .book-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            transition: transform 0.2s ease;
        }}
        .book-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .controls {{
            text-align: center;
            margin: 30px 0;
        }}
        .btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 0 10px;
            transition: background 0.3s ease;
        }}
        .btn:hover {{
            background: #2980b9;
        }}
        .ai-team {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }}
        .ai-role {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 三体AI教育版创作系统</h1>
            <p>基于GitBook风格的AI协作创作平台 - 实时进度追踪</p>
        </div>
        
        <div class="dashboard">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>📊 总体进度</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress_data['overall_progress']}%"></div>
                    </div>
                    <p>{progress_data['completed_nodes']}/900 节点 ({progress_data['overall_progress']}%)</p>
                </div>
                
                <div class="stat-card">
                    <h3>⭐ 平均质量</h3>
                    <div style="font-size: 2em; color: #f39c12; text-align: center;">
                        {progress_data['avg_quality']}/10
                    </div>
                    <p>基于多维度评估系统</p>
                </div>
                
                <div class="stat-card">
                    <h3>👥 AI团队状态</h3>
                    <p>活跃角色: {progress_data['active_roles']}/6</p>
                    <p>今日完成: {progress_data['today_completed']} 节点</p>
                </div>
                
                <div class="stat-card">
                    <h3>⏰ 预计完成</h3>
                    <p>{progress_data['estimated_completion']}</p>
                    <p>已运行: {progress_data['days_running']} 天</p>
                </div>
            </div>
            
            <div class="books-section">
                <h2>📚 三部曲创作进度</h2>
                
                <div class="book-card">
                    <h3>第一部：潜龙计划：思维格式化战争</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress_data['book1_progress']}%"></div>
                    </div>
                    <p>{progress_data['book1_completed']}/300 节点 • 质量: {progress_data['book1_quality']}/10</p>
                    <a href="/book1/introduction.md" class="btn">开始阅读</a>
                </div>
                
                <div class="book-card">
                    <h3>第二部：黑暗森林：AI时代的文明博弈</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress_data['book2_progress']}%"></div>
                    </div>
                    <p>{progress_data['book2_completed']}/300 节点 • 准备中</p>
                </div>
                
                <div class="book-card">
                    <h3>第三部：死神永生：数字永生的哲学困境</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress_data['book3_progress']}%"></div>
                    </div>
                    <p>{progress_data['book3_completed']}/300 节点 • 准备中</p>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="startCreation()">🎬 开始创作</button>
                <button class="btn" onclick="viewProgress()">📈 查看详细进度</button>
                <button class="btn" onclick="readBook()">📖 阅读已完成内容</button>
            </div>
            
            <div class="ai-team">
                <div class="ai-role">
                    <h4>🎨 创意总监</h4>
                    <p>故事架构 • 主题把控</p>
                    <p>状态: 🟢 活跃</p>
                </div>
                <div class="ai-role">
                    <h4>📖 情节架构师</h4>
                    <p>情节设计 • 节奏控制</p>
                    <p>状态: 🟢 活跃</p>
                </div>
                <div class="ai-role">
                    <h4>👤 角色设计师</h4>
                    <p>角色塑造 • 成长弧线</p>
                    <p>状态: 🟡 待命</p>
                </div>
                <div class="ai-role">
                    <h4>🔬 技术顾问</h4>
                    <p>科学准确 • 技术细节</p>
                    <p>状态: 🟡 待命</p>
                </div>
                <div class="ai-role">
                    <h4>🧠 哲学顾问</h4>
                    <p>思想深度 • 哲学融入</p>
                    <p>状态: 🟡 待命</p>
                </div>
                <div class="ai-role">
                    <h4>✏️ 风格编辑</h4>
                    <p>语言统一 • 质量把控</p>
                    <p>状态: 🟡 待命</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function startCreation() {{
            alert('🚀 启动AI协作创作流程！\n\n将自动分配6个AI角色开始并行创作。');
        }}
        
        function viewProgress() {{
            window.open('/api/progress', '_blank');
        }}
        
        function readBook() {{
            window.open('/book1/introduction.md', '_blank');
        }}
        
        // 实时更新进度
        setInterval(() => {{
            fetch('/api/progress')
                .then(response => response.json())
                .then(data => {{
                    // 更新进度条和数据
                    document.querySelectorAll('.progress-fill').forEach((bar, index) => {{
                        const progresses = [
                            data.overall_progress,
                            data.book1_progress,
                            data.book2_progress,
                            data.book3_progress
                        ];
                        if (progresses[index]) {{
                            bar.style.width = progresses[index] + '%';
                        }}
                    }});
                }});
        }}, 5000);
    </script>
</body>
</html>
        '''
        return html
    
    def get_progress_data(self):
        """获取项目进度数据"""
        # 这里应该是从数据库或文件读取实时数据
        # 暂时返回模拟数据
        return {
            'overall_progress': 0.3,  # 0.3%
            'completed_nodes': 3,
            'avg_quality': 8.5,
            'active_roles': 2,
            'today_completed': 1,
            'estimated_completion': '2027-03-31',
            'days_running': 1,
            'book1_progress': 1.0,  # 1%
            'book1_completed': 3,
            'book1_quality': 8.5,
            'book2_progress': 0,
            'book2_completed': 0,
            'book3_progress': 0,
            'book3_completed': 0
        }
    
    def handle_api_request(self):
        """处理API请求"""
        if self.path == '/api/progress':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            progress_data = self.get_progress_data()
            self.wfile.write(json.dumps(progress_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    """主函数"""
    PORT = 8000
    
    # 切换到项目根目录
    os.chdir('/Volumes/Ken2T/三体外篇/book')
    
    with socketserver.TCPServer(("", PORT), SantiAIRequestHandler) as httpd:
        print(f"🚀 三体AI创作系统已启动!")
        print(f"📖 访问地址: http://localhost:{PORT}")
        print(f"📚 GitBook风格界面已就绪")
        print(f"👥 6角色AI协作系统待命")
        print(f"⏰ 按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")

if __name__ == "__main__":
    main()