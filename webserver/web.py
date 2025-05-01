from flask import Flask, render_template, request, redirect, url_for, session, flash
from VerfyEmail import *
from flask_limiter import Limiter
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = ""#设置密码

# 初始化数据库
def init_db():
    conn = sqlite3.connect("auth.db")
    cursor = conn.cursor()
    #cursor.execute("""
    #    ALTER TABLE users 
    #    ADD COLUMN minecraft_name TEXT
    #""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            email_verified BOOLEAN DEFAULT FALSE,
            minecraft_uuid TEXT UNIQUE,
            minecraft_name TEXT ,
            is_verified BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

# 注册
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form['email']
        
        token = secrets.token_urlsafe(32)
        
        conn = sqlite3.connect("auth.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """INSERT INTO users 
                (username, password, email, verification_token) 
                VALUES (?, ?, ?, ?)""",
                (username, password, email, token)
            )
            conn.commit()
            send_verification_email(email, token)
            flash("注册成功！请检查邮箱完成验证。")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("用户名已存在！")
        finally:
            conn.close()
    
    return render_template("register.html")

# 登录
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect("auth.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session["user_id"] = user[0]  # 保存登录状态
            return redirect(url_for("link_minecraft"))
        else:
            return "用户名或密码错误！"
    
    return render_template("login.html")

# 关联 Minecraft 账号（玩家需输入游戏名）
@app.route("/link-minecraft", methods=["GET", "POST"])
#def link_minecraft():
#    if "user_id" not in session:
#        return redirect(url_for("login"))
#    
#    if request.method == "POST":
#        minecraft_name = request.form["minecraft_name"]
#        
#        # 这里应该调用 Mojang API 获取 UUID（简化版示例）
#        minecraft_uuid = str(uuid.uuid4())  # 模拟生成 UUID
#        
#        conn = sqlite3.connect("auth.db")
#        cursor = conn.cursor()
#        cursor.execute(
#            "UPDATE users SET minecraft_uuid = ?, is_verified = TRUE WHERE id = ?",
#            (minecraft_uuid, session["user_id"])
#        )
#        conn.commit()
#        conn.close()
#        
#        return "账号绑定成功！现在可以进入服务器了。"
#    
#    return render_template("link-minecraft.html")
def link_minecraft():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        minecraft_name = request.form["minecraft_name"]
    # 非正版服务器无需调用 Mojang API，直接让玩家输入服务器内的准确玩家名
    # 提示玩家：请在游戏中输入 /authme 查看自己的准确用户名（避免大小写问题）
    
    # 更新数据库（假设UUID通过其他方式获取，如插件提供）
        minecraft_uuid = "非正版UUID需从插件获取"  # 这里需要调整

        conn = sqlite3.connect("auth.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET minecraft_name = ?, is_verified = TRUE WHERE id = ?",
            (minecraft_name, session["user_id"])  # 改为存储玩家名而非UUID
        )
        conn.commit()
        conn.close()

        return "绑定成功！请确保游戏名准确无误。"
        
    return render_template("link-minecraft.html")

#@app.route("/check-player")
#def check_player():
#    minecraft_uuid = request.args.get("uuid")
#    
#    conn = sqlite3.connect("auth.db")
#    cursor = conn.cursor()
#    cursor.execute(
#        "SELECT is_verified FROM users WHERE minecraft_uuid = ?",
#        (minecraft_uuid,)
#    )
#    result = cursor.fetchone()
#    conn.close()
#    
#    return "VERIFIED" if result and result[0] else "UNVERIFIED"
#    
@app.route("/check-player")
def check_player():
    player_name = request.args.get("name")
    player_uuid = request.args.get("uuid")
    
    # 优先检查玩家名（非正版服务器更依赖名称）
    conn = sqlite3.connect("auth.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_verified FROM users WHERE minecraft_name = ? OR minecraft_uuid = ?",
        (player_name, player_uuid)
    )
    result = cursor.fetchone()
    conn.close()
    
    return "VERIFIED" if result and result[0] else "UNVERIFIED"

@app.route('/verify-email')
#@Limiter.limit("5 per minute")
def verify_email():
    token = request.args.get('token')
    
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET email_verified = TRUE WHERE verification_token = ?",
        (token,)
    )
    
    if cursor.rowcount > 0:
        conn.commit()
        return """
        <h2>验证成功！</h2>
        <p>现在可以返回游戏登录了</p>
        <a href="/login">前往登录页</a>
        """
    else:
        return "无效的验证链接或已过期", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
