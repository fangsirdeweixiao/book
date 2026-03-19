#!/usr/bin/env python3
"""
《智脑纪元：暗线对弈》三部曲 - 简洁书籍界面
专注于内容展示，论文风格
"""

import http.server
import socketserver
import os
import json

def get_trilogy_structure():
    """获取三部曲结构数据"""
    return {
        "trilogy": {
            "title": "《智脑纪元：暗线对弈》",
            "subtitle": "正统三体世界观下的隐秘战争史诗",
            "books": [
                {
                    "title": "第一部：暗子降临",
                    "time_span": "威慑纪元最后十年至威慑后20年",
                    "core_conflict": "潜龙小组发现第九智子 vs 三体文明驯化计划",
                    "chapters": 30,
                    "nodes_per_chapter": 10,
                    "total_words": 300000,
                    "completed_chapters": 0,
                    "completed_nodes": 0,
                    "key_plots": [
                        "破译时刻：叶文洁发现思维冗余标记",
                        "阳谋决议：章北海提出'砺剑计划'",
                        "社会切片：五个代表性人物的命运",
                        "暗线初现：思维疫苗投放"
                    ],
                    "ending": "种子已播下。现在，等春天。"
                },
                {
                    "title": "第二部：负熵革命",
                    "time_span": "三体舰队抵达至黑暗森林威慑后十年",
                    "core_conflict": "火种计划 vs 理性圣殿",
                    "chapters": 30,
                    "nodes_per_chapter": 10,
                    "total_words": 300000,
                    "completed_chapters": 0,
                    "completed_nodes": 0,
                    "key_plots": [
                        "舰队抵达的'礼物'：文明升华协议",
                        "潜龙的'木马行动'：智脑辅佐系统",
                        "陈建国的觉醒：反算法营销",
                        "黑暗森林威慑的'另一面'",
                        "火种燎原：3000个小B形成直觉网络"
                    ],
                    "ending": "罗辑用恒星诅咒守护了人类的躯体。现在，该我们守护人类的灵魂了。"
                },
                {
                    "title": "第三部：涅槃纪元",
                    "time_span": "威慑纪元最后50年至威慑后100年",
                    "core_conflict": "终极对决：思维格式化 vs 涅槃协议",
                    "chapters": 30,
                    "nodes_per_chapter": 10,
                    "total_words": 300000,
                    "completed_chapters": 0,
                    "completed_nodes": 0,
                    "key_plots": [
                        "理性圣殿倒计时：90%人口已接入",
                        "潜龙的摊牌计划：终极选择",
                        "陈建国的选择：拒绝上传",
                        "三体的误判与觉醒：这是进化",
                        "终极谈判：共建新宇宙",
                        "涅槃黎明：双生文明启航"
                    ],
                    "ending": "我们是，曾经差点被自己发明的笼子关死的，两个学会了开锁的文明。"
                }
            ]
        },
        "total": {
            "books": 3,
            "chapters": 90,
            "nodes": 900,
            "words": 900000,
            "completed_nodes": 0,
            "progress": 0
        },
        "characters": {
            "protagonists": [
                "叶文洁 - 语言学家，潜龙小组核心",
                "章北海 - 战略顾问，阳谋战略提出者",
                "陈建国 - 餐饮业小B，从算法困境到觉醒"
            ],
            "supporting": [
                "林薇 - 脑机接口科学家",
                "赵天启 - 游戏制作人",
                "苏菲亚 - 欧盟AI伦理官员",
                "哈桑 - 非洲数字基建工程师",
                "叶隐 - 潜龙外围引导者"
            ]
        }
    }

class TrilogyHandler(http.server.SimpleHTTPRequestHandler):
    """三部曲界面处理器"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_trilogy_index()
            self.wfile.write(html.encode('utf-8'))
            return
            
        super().do_GET()
    
    def generate_trilogy_index(self):
        """生成三部曲目录页面"""
        data = get_trilogy_structure()
        trilogy = data['trilogy']
        
        html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{trilogy['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.8;
            color: #2c3e50;
            background: #f5f6fa;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }}
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            color: #2c3e50;
            font-weight: normal;
        }}
        .header .subtitle {{
            font-size: 1.3em;
            color: #7f8c8d;
            font-style: italic;
        }}
        .overview {{
            background: #ecf0f1;
            padding: 20px;
            margin: 30px 0;
            border-left: 4px solid #e74c3c;
        }}
        .overview h2 {{
            font-size: 1.4em;
            margin-bottom: 15px;
            color: #c0392b;
        }}
        .overview p {{
            margin-bottom: 10px;
            text-align: justify;
        }}
        .book {{
            margin: 40px 0;
            padding: 25px;
            border: 2px solid #34495e;
            border-radius: 6px;
        }}
        .book-header {{
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .book-title {{
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .book-meta {{
            color: #7f8c8d;
            font-size: 0.95em;
            margin: 5px 0;
        }}
        .conflict {{
            background: #fff3cd;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #f39c12;
        }}
        .conflict-title {{
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
        }}
        .plots {{
            margin: 20px 0;
        }}
        .plot-item {{
            margin: 12px 0;
            padding: 12px;
            background: #f8f9fa;
            border-left: 3px solid #28a745;
            font-size: 0.95em;
        }}
        .ending {{
            background: #d1ecf1;
            padding: 20px;
            margin: 25px 0;
            border-left: 4px solid #17a2b8;
            font-style: italic;
            text-align: center;
            font-size: 1.1em;
            color: #0c5460;
        }}
        .progress {{
            background: #f8f9fa;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #6c757d;
        }}
        .progress-bar {{
            background: #e9ecef;
            height: 10px;
            border-radius: 5px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            background: #28a745;
            height: 100%;
            transition: width 0.3s;
        }}
        .characters {{
            margin: 40px 0;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .characters h2 {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #495057;
        }}
        .char-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .char-item {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
        }}
        .char-name {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .char-desc {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{trilogy['title']}</h1>
            <div class="subtitle">{trilogy['subtitle']}</div>
        </div>
        
        <div class="overview">
            <h2>📖 核心定位</h2>
            <p>正统三体世界观下的隐秘战争史诗，聚焦于"末日战役"后人类与三体文明在AI维度展开的、决定文明存续形态的终极暗线对弈。</p>
        </div>
        
        <div class="progress">
            <strong>总体进度：</strong> {data['total']['completed_nodes']}/{data['total']['nodes']} 节点 
            ({data['total']['progress']}%) · {data['total']['words']}字
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data['total']['progress']}%"></div>
            </div>
        </div>
        
        {self.generate_books_html(trilogy['books'])}
        
        {self.generate_characters_html(data['characters'])}
        
        <div class="footer">
            <p>编辑工作在当前目录进行，此页面仅用于内容展示</p>
            <p>架构文档：<a href="/三部曲架构.md" target="_blank">查看完整架构</a></p>
            <p>最后更新：2026-03-19</p>
        </div>
    </div>
</body>
</html>
        '''
        return html
    
    def generate_books_html(self, books):
        """生成书籍列表HTML"""
        books_html = ''
        
        for i, book in enumerate(books, 1):
            progress = (book['completed_nodes'] / (book['chapters'] * book['nodes_per_chapter'])) * 100
            
            books_html += f'''
            <div class="book">
                <div class="book-header">
                    <div class="book-title">第{i}部：{book['title']}</div>
                    <div class="book-meta">
                        时间跨度：{book['time_span']}<br>
                        {book['chapters']}章 × {book['nodes_per_chapter']}节点 = {book['chapters'] * book['nodes_per_chapter']}节点 · {book['total_words']}字
                    </div>
                </div>
                
                <div class="conflict">
                    <div class="conflict-title">⚔️ 核心冲突</div>
                    {book['core_conflict']}
                </div>
                
                <div class="progress">
                    <strong>创作进度：</strong> {book['completed_nodes']}/{book['chapters'] * book['nodes_per_chapter']} 节点 ({progress:.1f}%)
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress}%"></div>
                    </div>
                </div>
                
                <div class="plots">
                    <strong>📋 关键情节节点：</strong>
                    {self.generate_plots_html(book['key_plots'])}
                </div>
                
                <div class="ending">
                    <strong>📝 部结尾：</strong><br>
                    "{book['ending']}"
                </div>
            </div>
            '''
        
        return books_html
    
    def generate_plots_html(self, plots):
        """生成情节列表HTML"""
        plots_html = ''
        for plot in plots:
            plots_html += f'''
            <div class="plot-item">
                • {plot}
            </div>
            '''
        return plots_html
    
    def generate_characters_html(self, characters):
        """生成角色列表HTML"""
        html = '''
        <div class="characters">
            <h2>👥 主要角色</h2>
            <div class="char-list">
        '''
        
        # 主角
        html += '<h3>主角</h3>'
        for char in characters['protagonists']:
            name, desc = char.split(' - ')
            html += f'''
            <div class="char-item">
                <div class="char-name">{name}</div>
                <div class="char-desc">{desc}</div>
            </div>
            '''
        
        # 配角
        html += '<h3>配角</h3>'
        for char in characters['supporting']:
            name, desc = char.split(' - ')
            html += f'''
            <div class="char-item">
                <div class="char-name">{name}</div>
                <div class="char-desc">{desc}</div>
            </div>
            '''
        
        html += '</div></div>'
        return html

def main():
    """主函数"""
    PORT = 8000
    
    os.chdir('/Volumes/Ken2T/三体外篇/book')
    
    with socketserver.TCPServer(("", PORT), TrilogyHandler) as httpd:
        print(f"📚 《智脑纪元：暗线对弈》三部曲")
        print(f"🌐 访问地址: http://localhost:{PORT}")
        print(f"📖 3本书 × 30章 × 10节点 = 900节点")
        print(f"📝 编辑工作在当前目录进行")
        print(f"⏰ 按 Ctrl+C 停止")
        print("-" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")

if __name__ == "__main__":
    main()