import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from database.ketnoi_db import ket_noi

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Dùng cho flash messages

def format_currency(value):
    return "{:,.0f} đ".format(value)
@app.route('/')
def index():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))

    conn = ket_noi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sach")
    books = cursor.fetchall()
    for book in books:
        book['gia'] = format_currency(book['gia'])
    conn.close()
    return render_template('index.html', books=books)

#Thêm sách
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        ten_sach = request.form['ten_sach']
        tac_gia = request.form['tac_gia']
        gia = request.form['gia']
        nam_xb = request.form['nam_xb']
        the_loai = request.form['the_loai']
        tom_tat = request.form['tom_tat']
        hinh_bia = request.files['hinh_bia']  # Lấy file hình bìa từ form

        # Lưu file vào thư mục static/images
        hinh_bia_filename = hinh_bia.filename
        hinh_bia.save(os.path.join('static/images', hinh_bia_filename))

        conn = ket_noi()
        cursor = conn.cursor()
        query = """INSERT INTO sach (ten_sach, tac_gia, gia, nam_xb, the_loai, tom_tat, hinh_bia) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (ten_sach, tac_gia, gia, nam_xb, the_loai, tom_tat, f'images/{hinh_bia_filename}'))
        conn.commit()
        conn.close()
        flash('Sách đã được thêm thành công!')
        return redirect(url_for('index'))
    return render_template('add_book.html')

# Sửa sản phẩm 
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    conn = ket_noi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sach WHERE id = %s", (id,))
    book = cursor.fetchone()
    
    if request.method == 'POST':
        ten_sach = request.form['ten_sach']
        tac_gia = request.form['tac_gia']
        gia = request.form['gia']
        nam_xb = request.form['nam_xb']
        the_loai = request.form['the_loai']
        tom_tat = request.form['tom_tat']
        hinh_bia = request.form['hinh_bia']
        
        cursor.execute("""
            UPDATE sach 
            SET ten_sach = %s, tac_gia = %s, gia = %s, nam_xb = %s, the_loai = %s, tom_tat = %s, hinh_bia = %s
            WHERE id = %s
        """, (ten_sach, tac_gia, gia, nam_xb, the_loai, tom_tat, hinh_bia, id))
        conn.commit()
        conn.close()
        flash('Thông tin sách đã được cập nhật!')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('update_book.html', book=book)

# Xóa sản phẩm 
@app.route('/delete/<int:id>', methods=['GET'])
def delete_book(id):
    conn = ket_noi()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sach WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash('Sách đã được xóa!')
    return redirect(url_for('index'))

# Đăng nhập 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = ket_noi()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin_logged_in'] = True
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('index'))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "danger")

    return render_template('login.html')

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Bạn đã đăng xuất!", "info")
    return redirect(url_for('login'))

@app.before_request
def require_login():
    if request.endpoint in ['index', 'add_book', 'update_book', 'delete_book'] and 'admin_logged_in' not in session:
        return redirect(url_for('login'))

# router cho nút bật/tắt tình trạng hàng
@app.route('/toggle_status/<int:id>', methods=['POST'])
def toggle_status(id):
    conn = ket_noi()
    cursor = conn.cursor()
    cursor.execute("UPDATE sach SET tinh_trang = NOT tinh_trang WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Tình trạng sách đã được cập nhật!")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
