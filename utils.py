import sqlite3
import re
import html

def get_db():
    conn = sqlite3.connect('db.db', check_same_thread=False)  
    conn.row_factory = sqlite3.Row  
    try:
        yield conn
    finally:
        conn.close()

def format_note_content(content):
    """
    Форматирует контент заметки, поддерживая HTML теги и Markdown-подобный синтаксис
    """
    formatted_content = html.escape(content)
    formatting_rules = [
        # Ссылки
        (r'&lt;a href=&quot;([^&quot;]+)&quot;&gt;([^&lt;]+)&lt;/a&gt;', r'<a href="\1" target="_blank" rel="noopener noreferrer">\2</a>'),
        
        # Заголовки
        (r'&lt;h1&gt;([^&lt;]+)&lt;/h1&gt;', r'<h1>\1</h1>'),
        (r'&lt;h2&gt;([^&lt;]+)&lt;/h2&gt;', r'<h2>\1</h2>'),
        (r'&lt;h3&gt;([^&lt;]+)&lt;/h3&gt;', r'<h3>\1</h3>'),
        (r'&lt;h4&gt;([^&lt;]+)&lt;/h4&gt;', r'<h4>\1</h4>'),
        (r'&lt;h5&gt;([^&lt;]+)&lt;/h5&gt;', r'<h5>\1</h5>'),
        (r'&lt;h6&gt;([^&lt;]+)&lt;/h6&gt;', r'<h6>\1</h6>'),
        
        # Параграфы
        (r'&lt;lp&gt;([^&lt;]+)&lt;/p&gt;', r'<p style="text-align: left;">\1</p>'),
        (r'&lt;rp&gt;([^&lt;]+)&lt;/p&gt;', r'<p style="text-align: right;">\1</p>'),
        (r'&lt;p&gt;([^&lt;]+)&lt;/p&gt;', r'<p>\1</p>'),
        
        # Текстовое форматирование
        (r'&lt;b&gt;([^&lt;]+)&lt;/b&gt;', r'<strong>\1</strong>'),
        (r'&lt;u&gt;([^&lt;]+)&lt;/u&gt;', r'<u>\1</u>'),
        (r'&lt;i&gt;([^&lt;]+)&lt;/i&gt;', r'<em>\1</em>'),
        
        # Цветные спаны
        (r'&lt;rspan&gt;([^&lt;]+)&lt;/span&gt;', r'<span style="color: #ff4444;">\1</span>'),
        (r'&lt;gspan&gt;([^&lt;]+)&lt;/span&gt;', r'<span style="color: #44ff44;">\1</span>'),
        (r'&lt;bspan&gt;([^&lt;]+)&lt;/span&gt;', r'<span style="color: #4444ff;">\1</span>'),
        
        # Малый текст
        (r'&lt;ms&gt;([^&lt;]+)&lt;/ms&gt;', r'<small>\1</small>'),
        
        # Разделители и переносы
        (r'&lt;hr&gt;', r'<hr>'),
        (r'&lt;br&gt;', r'<br>'),
    ]
    
    for pattern, replacement in formatting_rules:
        formatted_content = re.sub(pattern, replacement, formatted_content, flags=re.IGNORECASE)
    
    markdown_rules = [
        # Жирный текст **текст**
        (r'\*\*([^*]+)\*\*', r'<strong>\1</strong>'),
        # Курсив *текст*
        (r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>'),
        # Подчеркнутый __текст__
        (r'__([^_]+)__', r'<u>\1</u>'),
    ]
    
    for pattern, replacement in markdown_rules:
        formatted_content = re.sub(pattern, replacement, formatted_content)
    
    formatted_content = formatted_content.replace('\n', '<br>')
    
    return formatted_content