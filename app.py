from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import smtplib
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
app.secret_key = "my_secret_key"


paralist = {}

def add_urun(username, password,email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO users(username,password,email) VALUES("{username}","{password}","{email}")')
    conn.close()

def get_products():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urunler")
    products = cursor.fetchall()
    conn.close()
    return products

def send_mail2(send_to, code):
    my_mail_address = "alayiburada0@gmail.com"
    my_password = "okex mhcs czhb pqez"
    subject = "Hepsiburada Üyelik Tamamlama"

    message = f"""
E-posta adresinizi doğrulayın
Değerli müşterimiz,
Üye olmaya devam edebilmek için, lütfen aşağıdaki kodu giriniz:
**{code}**

Bu kodu kimseyle paylaşmayın. Müşteri hizmetlerimiz sizden asla parolanızı, kodu, kredi kartı veya banka bilgilerinizi istemez.
    """

    msg = MIMEMultipart()
    msg["From"] = my_mail_address
    msg["To"] = send_to
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(my_mail_address, my_password)
            server.sendmail(my_mail_address, send_to, msg.as_string())
            print("E-posta başarıyla gönderildi.")
    except Exception as e:
        print(f"E-posta gönderilirken bir hata oluştu: {e}")

def reset_password2(send_to, username ,code):
    my_mail_address = "alayiburada0@gmail.com"
    my_password = "okex mhcs czhb pqez"
    subject = "Şifre yenileme talebi"

    # Mesaj içeriği
    message = f"""

Merhaba {username},

Şifrenizi unuttuysanız üzülmeyin, aşağıdaki linke basarak yeni şifre oluşturabilirsiniz.
Yeni Şifre Oluştur

http://127.0.0.1:5000/reset-password/{code}

Eğer bu e-postayı görüntüleyemiyorsanız, buradan ilerleyebilirsiniz.
	Önemli Hatırlatma:

Eğer şifre yenileme talebinin size ait olmadığını düşünüyorsanız lütfen bu e-postayı dikkate almayın. Mevcut şifreniz ile giriş yapmaya devam edebilirsiniz.


—

Teşekkür ederiz,
Hepsiburada
    """

    # MIME tipinde e-posta oluştur
    msg = MIMEMultipart()
    msg["From"] = my_mail_address
    msg["To"] = send_to
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(my_mail_address, my_password)
            server.sendmail(my_mail_address, send_to, msg.as_string())
            print("E-posta başarıyla gönderildi.")
    except Exception as e:
        print(f"E-posta gönderilirken bir hata oluştu: {e}")

@app.route('/urun/<urunid>', methods = ['GET','POST'])
def urun(urunid):

    username = session.get('username')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM urunler WHERE urunid = {urunid}")
    urun = cursor.fetchone()
    conn.close()

    return render_template('urunler.html', urun=urun, username=username)


@app.route('/panel/', methods = ['POST','GET'])
def panel():

    if request.method == 'POST':
        creator = request.form['creator']
        urunad = request.form['urunad']
        urunprice = request.form['urunprice']
        urunoldprice = request.form['urunoldprice']
        urunimg = request.form['urunimg']
        urunrating = request.form['urunrating']
        urundegerlendirme = request.form['urundegerlendirme']

        cleaned_value = urunprice.replace('.', '').replace(',', '.')
        cleaned_value2 = urunoldprice.replace('.', '').replace(',', '.')
        float_value = float(cleaned_value)
        float_value2 = float(cleaned_value2)
        new = int(float_value)
        old = int(float_value2)
        old2 = old - new
        indirim = old2 * 100 / new
        if indirim < 0:
            indirim = 1

        indirim2 = str(indirim).split(".")
        elinidirim = int(indirim2[0])
        elinidirim += 1

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO urunler(uruncreator,urunad,urunprice,urunoldprice,urunimg,urunrating,urundegerlendirme,urunindirim) VALUES ('{creator}','{urunad}','{urunprice}','{urunoldprice}','{urunimg}','{urunrating}','{urundegerlendirme}',{elinidirim})")
        conn.commit()
        conn.close()        

    return render_template('panel.html')

@app.route("/home", methods=["GET", "POST"])
def home():

    products = get_products()

    if request.method == "POST":
        button_pressed = request.form.get("addcart")
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM users WHERE username = "{session.get("username")}"')
        user = cursor.fetchone()
        if user[4] != None:
            liste = str(user[4])
            add = " " + str(button_pressed)
        else:
            liste = ""
            add = str(button_pressed)
        
        liste2 = liste + add
        cursor.execute(f'UPDATE users SET cart = "{liste2}" WHERE username = "{session.get("username")}"')
        conn.commit()
        conn.close()

    if session.get("username") != "":
        return render_template("home.html", products=products, username=session.get("username"))

    
    return render_template("home.html", products=products)


@app.route("/login", methods=["GET", "POST"])
def login():

    status = ""

    if request.method == "POST":
        if "loginbtn" in request.form:
            return redirect("login")
        elif "registerbtn" in request.form:
            return redirect("register")

        if "logbtn" in request.form:
            mail = request.form["mail"]
            password = request.form["pasword"]

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM users WHERE email = "{mail}" AND password = "{password}"')
            user = cursor.fetchone()
            conn.close()

            if user:
                session["username"] = user[0]
                return redirect(url_for("home"))

    return render_template("login.html", status=status)

@app.route("/register", methods=["POST","GET"])
def register():

    if request.method == "POST":
        if "loginbtn" in request.form:
            return redirect("login")
        elif "registerbtn" in request.form:
            return redirect("register")
        
        if "regbtn" in request.form:

            register_input = request.form["registermail"]
            session["mailadress"] = register_input
            splited_input = register_input.split("@")
            if len(splited_input) == 2:
                session["email"] = register_input
                v_code = random.randint(100000,999999)
                s_code = str(v_code)
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users(email, code) VALUES(?, ?)', (register_input, s_code))
                conn.commit()
                conn.close()
                send_mail2(register_input, s_code)
                return redirect(url_for("create_account"))
            else:
                phone = register_input
                # Sms yollama sistemi buraya gelecek fakat herhangi bir sms sunucum olmadığı için şimdilik boş.

    return render_template("register.html")


@app.route("/create/account/compalate", methods=["POST","GET"])
def complateaccount():

    if request.method == "POST":
        if "regnow" in request.form:
            mail = session.get("email")
            username = request.form["name"]
            surname = request.form["surname"]
            password = request.form["password"]
            fullname = username + " " + surname
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f'UPDATE users SET username = "{fullname}", password = "{password}" WHERE email = "{mail}"')
            conn.commit()
            conn.close()   
            session["username"] = fullname
            return redirect(url_for("home"))

    return render_template("complateacc.html")


@app.route("/create/account", methods=["POST","GET"])
def create_account():
    mail = session.get("email")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE email = "{mail}"')
    user = cursor.fetchone()
    conn.close()
    if request.method == "POST":
        if "continue" in request.form:
            code = request.form["code"]
            if code == user[3]:
                return redirect(url_for("complateaccount"))
            else:
                print("Hatalı Kod")

    return render_template("createacc.html")


@app.route("/logout")
def logout():
    session["username"] = None
    return redirect(url_for("home"))

@app.route("/forget-password", methods=["POST","GET"])
def forget_password():

    if request.method == "POST":
            mail = request.form["eposta"]
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM users WHERE email = "{mail}"')
            user = cursor.fetchone()
            conn.close()
            reset_password2(mail,user[0],user[3])

    return render_template("forgetpassword.html")

@app.route("/reset-password/<code>", methods=["POST","GET"])
def reset_password(code):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE code = "{code}"')
    user = cursor.fetchone()
    mail = user[2]

    if request.method == 'POST':
            newpass = request.form["newpass"]
            cursor.execute(f'UPDATE users SET password = "{newpass}" WHERE code = "{code}"')
            conn.commit()
            conn.close()
            return redirect(url_for("login"))

    return render_template("resetpassword.html", mail=mail)

@app.route("/getcode" , methods=["GET","POST"])
def getcode():
    email = session.get("mailadress")
    v_code = random.randint(100000,999999)
    s_code = str(v_code)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET code = "{s_code}" WHERE email = "{email}"')
    conn.commit()
    conn.close()
    send_mail2(email, s_code)

    return redirect(url_for("create_account"))

@app.route("/mycart", methods=["POST", "GET"])
def mycart():
    myList = []
    price = 0
    urun_sayisi = 0
    
    username = session.get('username')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE username = "{username}"')
    user = cursor.fetchone()

    if user[4] != None:
        # Sepet varsa, boş değilse ürünleri ayırıyoruz
        if user[4]:
            b = str(user[4]).strip().split(" ")
        else:
            b = []  # Sepet boş

        # Ürün sayısını takip etmek için bir sözlük
        urun_sayilari = {}

        # Veritabanı bağlantısı
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        

        # Ürünleri sepetteki ID'ler ile alıyoruz
        urunler = []
        for i in b:
            if i.strip():  # Boşluk olmayan öğeleri kontrol et
                cursor.execute('SELECT * FROM urunler WHERE urunid = ?', (i,))
                urun = cursor.fetchone()
                
               

                    # Ürün adı ve sayısını tutuyoruz
                if i in urun_sayilari:
                    urun_sayilari[i] += 1
                else:
                    urun_sayilari[i] = 1
                    
        for i in urun_sayilari:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM urunler WHERE urunid = "{i}"')
            urun1 = cursor.fetchone()
            myList.append(urun1)

        conn.close()
        adet = []
        for a in urun_sayilari:
            adet.append(urun_sayilari[a]) 

        

        if request.method == "POST":
            print(request.form)
            if "add1" in request.form:
                value = request.form["add1"]  # Sepete eklenecek ürünün ID'si
                
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                cursor.execute(f'SELECT * FROM users WHERE username = "{username}"')
                user1 = cursor.fetchone()
                carpan = urun_sayilari[value]
                cursor.execute(f'SELECT * FROM urunler WHERE urunid = "{value}"')
                urun_1 = cursor.fetchone()
                cleaned_value = urun_1[3].replace('.', '').replace(',', '.')
                floated_value = float(cleaned_value)
                integar_value = int(floated_value)
                para = int(integar_value) * int(carpan + 1)
                print("Para: " + str(para))
                paralist[value] = para
                print(paralist)
                if user1:
                    # Kullanıcı bulundu ve cart verisi mevcut
                    cart = user1[4]  # cart verisini çekiyoruz
                    if cart:
                        cart_list = cart.split(" ")  # Sepeti listeye çeviriyoruz
                        
                        # Sepetteki ürünü bulalım
                        updated = False  # Güncelleme yapılmadıysa False olarak başlatıyoruz
                        for i in range(len(cart_list)):
                            try:
                                product_id, quantity = cart_list[i].split("-")  # "ID-quantity" formatını ayırıyoruz
                                if product_id == value:
                                    # Eğer ürün zaten sepette varsa, miktarını artırıyoruz
                                    new_quantity = int(quantity) + 1  # Sayıyı bir artır
                                    cart_list[i] = f"{product_id}-{new_quantity}"  # Güncellenmiş değeri listeye yaz
                                    updated = True
                                    break
                            except ValueError:
                                # Eğer format yanlışsa veya eksikse, bu öğeyi geçiyoruz
                                continue
                        
                        if not updated:
                            # Eğer ürün sepette yoksa, yeni ürün ekliyoruz
                            cart_list.append(f"{value}")
                        
                        # Yeni cart verisini güncelliyoruz
                        updated_cart = " ".join(cart_list)
                        
                        # Güncellenen cart verisini veritabanına kaydediyoruz
                        cursor.execute(f'UPDATE users SET cart = ? WHERE username = ?', (updated_cart, username))
                        conn.commit()
                        
                        print(f"Güncellenmiş Sepet: {updated_cart}")
                
                conn.close()
                return redirect(url_for('mycart'))  # Sepet sayfasına yönlendirme
            elif "minus1" in request.form:
                value = request.form["minus1"]  # Sepete eklenecek ürünün ID'si
                
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute(f'SELECT * FROM users WHERE username = "{username}"')
                user2 = cursor.fetchone()
                cursor.execute(f'SELECT * FROM urunler WHERE urunid = "{value}"')
                urun_2 = cursor.fetchone()
                carpan = urun_sayilari[value]
                son_fiyat = paralist[value]
                cleaned_value = urun_2[3].replace('.', '').replace(',', '.')
                floated_value = float(cleaned_value)
                integar_value = int(floated_value)
                print("Çarpan: " +str(carpan))
                para = son_fiyat - int(integar_value) 
                print("Para: " + str(para))
                paralist[value] = para
                if user2:
                    # Kullanıcı bulundu ve cart verisi mevcut
                    cart = user2[4]  # cart verisini çekiyoruz
                    if cart:
                        cart_list = cart.split(" ")  # Sepeti listeye çeviriyoruz
                        print(f"Sepet Başlangıcı: {cart_list}")
                        
                        if value in cart_list:
                            cart_list.remove(value)  # Value değerini sadece bir kere sil
                            print(f"Yeni Sepet: {cart_list}")
                        
                        # Yeni cart verisini güncelliyoruz
                        updated_cart = " ".join(cart_list)
                        
                        # Güncellenen cart verisini veritabanına kaydediyoruz
                        cursor.execute(f'UPDATE users SET cart = ? WHERE username = ?', (updated_cart, username))
                        conn.commit()
                        
                        print(f"Güncellenmiş Sepet: {updated_cart}")
                
                conn.close()
                return redirect(url_for('mycart'))
            elif "delete" in request.form:
                value = request.form["delete"]
                
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                cursor.execute(f'SELECT * FROM users WHERE username = "{username}"')
                user3 = cursor.fetchone()
                
                if user3:
                    allprod = (user3[4]).split(" ")  # Sepeti listeye ayırıyoruz
                    print("Orijinal Sepet:", allprod)
                    
                    # Boş öğeleri temizliyoruz
                    allprod = [item for item in allprod if item != ""]

                    # value'yu listeden çıkarıyoruz
                    allprod = [item for item in allprod if item != value]
                    
                    print("Güncellenmiş Sepet:", allprod)

                    # Güncellenmiş sepete geri yazıyoruz
                    updated_cart = " ".join(allprod)
                    
                    cursor.execute(f'UPDATE users SET cart = ? WHERE username = ?', (updated_cart, username))
                    conn.commit()

                conn.close()
                if allprod == []:
                    return redirect(url_for('emptyCart'))  # Sepet sayfasına yönlendirme
                else:
                    return redirect(url_for('mycart'))
        print(paralist)
        return render_template('mycart.html', urunler=myList, urun_sayisi=len(urunler), urun_sayilari=urun_sayilari, adet=adet, paralist=paralist)
        
    else:
        return redirect(url_for("emptyCart"))

@app.route("/emptycart", methods=["GET", "POST"])
def emptyCart():
    return render_template("emptycart.html")

if __name__ == '__main__':
    app.run(debug=True)