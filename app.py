from flask import Flask, render_template, url_for, request, redirect, session
import random,string,os
import db,mail
from hashids import Hashids

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters,k=256))

# ログイン画面
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/')
def back_index(mail):
    input_data={'mail':mail}
    return render_template('index.html',data=input_data,error=True)

@app.route('/', methods=['POST'])
def login():
    mail = request.form.get('mail')
    password = request.form.get('password')
    if db.login(mail,password):
        session['user_info'] = mail
        return render_template('mypage.html')
    else:
        return back_index(mail)

#新規登録
@app.route('/register_accounts')
def register_accounts():
    return render_template('register_accounts.html')

@app.route('/register_accounts_set', methods=['POST'])
def register_set():
    name = request.form.get('name')
    mail = request.form.get('mail')
    session['name'] = name
    session['mail'] = mail
    password = request.form.get('password')
    salt = db.get_salt()
    hashed_password = db.get_hash(password, salt)
    session['salt'] = salt
    session['password'] = hashed_password
    return render_template('register_account_set.html',name=session['name'],mail=session['mail'])

@app.route('/register_account')
def back_register():
    input_data={
        'name':session['name'],
        'mail':session['mail']
    }
    return render_template('register_accounts.html',data=input_data)

@app.route('/register_account', methods=['POST'])
def send():
    if db.address_check_first(session['mail']) and db.address_check_second(mail):
        name = session['name']
        code = db.create_code()
        to = session['mail']
        subject = "「Oshi More!」認証コード"
        message = ('''
    {} 様 Oshi More! からの認証メールです。 
    以下のURLから認証を完了してください。 

    http://127.0.0.1:5000/certification
    認証コード : {} 
    ''').format(name,code)
        
        mail.send_mail(to,subject,message)
        
        db.temporary_register(session['mail'], session['name'], session['password'], session['salt'], code)
        session.pop('name',None)
        session.pop('mail',None)
        session.pop('password',None)
        session.pop('salt',None)
        
        return redirect(url_for('navigateSend'))
    else:
        input_data={
        'name':session['name'],
        'mail':session['mail']
        }
        error = True
    return render_template('register_accounts.html',data=input_data,error=error)

@app.route('/send',methods=['GET'])
def navigateSend():
    return render_template('send.html')

#認証
@app.route('/certification')
def certification():
    return render_template('certification.html')

@app.route('/certification', methods=['POST'])
def certification_mail():
    mail = request.form.get('mail')
    code = request.form.get('code')
    if db.certification_mail(mail,code):
        use = db.select_temporary(mail)
        
        hashids = Hashids(
        min_length=16,  # 短すぎると分かりにくいので8文字以上にする
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' 
    )
        id = hashids.encode(use[0])
        mail = use[1]
        name = use[2]
        password = use[3]
        salt = use[4]
        db.insert_user(id,mail,name,password,salt)
        db.delete_certification(mail)
        return index()
    else:
        return certification()

# だいじ
if __name__ == '__main__':
    app.run(debug=True)