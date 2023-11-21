from flask import Flask, render_template,redirect,url_for,request,session
import random,string,db,datetime,os,mail
from hashids import Hashids
from admin import admin_bp
from user import user_bp

app = Flask(__name__)
app.secret_key=''.join(random.choices(string.ascii_letters,k=256))

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    session['msg']=''
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
        session['user_info'] = db.get_accountInfo_toMail(mail)
        return redirect(url_for('top',checkcal=0))
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
    if db.address_check_first(session['mail']) and db.address_check_second(session['mail']):
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

""" 
マイページ画面・現在日時
"""

@app.route('/top/<int:checkcal>')
def top(checkcal):
    if (checkcal!=1):
        print('test')
        dt=datetime.datetime.now()
        session['month']=dt.month
        session['year']=dt.year
    searchDay=datetime.date(session['year'],session['month'],1)
    msg=session['msg']
    session['msg']=''
    datas=[]
    invitations=[]
    eventList=[]
    
    comIdList=db.getcomId_to_accId(session['user_info'][0])
    comIdList2=db.getcomId_to_accId_joined(session['user_info'][0])
    comIdList3=db.getcomId_to_accId_invit(session['user_info'][0])
    if(len(comIdList)!=0):
        for comId in comIdList:
            eventList.append(db.getevent_to_comId(comId,searchDay))
    if(len(comIdList2)!=0):
        for comId in comIdList2:
            datas.append(db.getcomInfo_to_comId(comId))
    if(len(comIdList3)!=0):
        for comId in comIdList3:
            invitations.append(db.getcomInfo_to_comId(comId))
    searchDay=f"{session['year']}-{session['month']}-"
    return render_template('user/menu.html', month=session['month'], year=session['year'], datas=datas, invitations=invitations, eventList=eventList, num1=len(comIdList), searchDay=searchDay, msg=msg)

""" 
マイページ画面・前の月へ
"""
@app.route('/monthback')
def monthback():
    session['month']-=1
    if(session['month']==0):
        session['month']=12
        session['year']-=1
    
    return redirect(url_for('top',checkcal=1))
""" 
マイページ画面・次の月へ
"""
@app.route('/monthnext')
def monthnext():
    session['month']+=1
    if(session['month']==13):
        session['month']=1
        session['year']+=1
    
    return redirect(url_for('top',checkcal=1))
    
@app.route('/register_community',methods=['POST'])
def register_community():
    com_name=request.form.get('com_name')
    fav_name=request.form.get('fav_name')
    com_pub=request.form.get('com_public')
    com_explanation=request.form.get('com_explanation')
    data=[com_name,fav_name,com_explanation,com_pub]
    count=db.register_community(data)
    if (count==1):
        com_id=db.get_community_id()
        hidden_flag=db.get_hidden_flag(com_id)
        data=[session['user_info'][0],com_id[0],1,1,hidden_flag[0],0,0]
        count=db.join_community_master(data)
        msg='コミュニティを作成しました！'
    else:
        msg='コミュニティを作成できませんでした。'
    session['msg']=msg
    return redirect(url_for('top',checkcal=0))


@app.route('/community/<int:id>/<int:checkcal>')
def community(id,checkcal):
    if (checkcal!=1):
        dt=datetime.datetime.now()
        session['month']=dt.month
        session['year']=dt.year
    searchDay=datetime.date(session['year'],session['month'],1)
    datas=[]
    invitations=[]
    eventList=[]
    community_thread_list=[]
    community_thread_list_all=[]
    cnt=0
    
    comIdList=db.getcomId_to_accId_joined(session['user_info'][0])
    comIdList2=db.getcomId_to_accId_invit(session['user_info'][0])
    if(len(comIdList)!=0):
        for comId in comIdList:
            datas.append(db.getcomInfo_to_comId(comId))
    if(len(comIdList2)!=0):
            for comId in comIdList2:
                invitations.append(db.getcomInfo_to_comId(comId))
    session['comId']=id
    eventList.append(db.getevent_to_comId(id,searchDay))
    searchDay=f"{session['year']}-{session['month']}-"
    community_thread_list=db.getcomtThread_list_tocomId(id)
    
    for data in community_thread_list:
        goodcheck=db.getcomThread_good(data[0],data[4])
        good_num=db.getcomThread_goodnum(data[0])
        community_thread_list_all.append([data[0],data[1],data[2],data[3],data[4],data[5],data[6],goodcheck[0],good_num[0]])
        cnt+=1
    return render_template('user/community.html', month=session['month'], year=session['year'], datas=datas, invitations=invitations, eventList=eventList, num1=1, searchDay=searchDay,thread_list=community_thread_list_all)

@app.route('/community_set')
def community_set():
    if 'user_info' in session:
        accId=session['user_info'][0]
        comId=session['comId']
        comAuth=db.get_comAuth(accId,comId)
        print(comAuth)
        if (comAuth[0]==0):
            return render_template('user/community_set_user.html',comId=comId,checkcal=0)
        elif (comAuth[0]==1):
            return render_template('user/community_set_master.html',comId=comId,checkcal=0)
        elif (comAuth[0]==2):
            return render_template('user/community_set_sub.html',comId=comId,checkcal=0)
        return redirect(url_for('community',id=session['comId'],checkcal=0))
    else:
        return redirect(url_for('index'))


""" 
コミュニティ画面・前の月へ
"""
@app.route('/com_monthback')
def com_monthback():
    session['month']-=1
    if(session['month']==0):
        session['month']=12
        session['year']-=1
    
    return redirect(url_for('community',id=session['comId'],checkcal=1))

""" 
コミュニティ画面・次の月へ
"""

@app.route('/com_monthnext')
def com_monthnext():
    session['month']+=1
    if(session['month']==13):
        session['month']=1
        session['year']+=1
    
    return redirect(url_for('community',id=session['comId'],checkcal=1))

"""
コミュニティ参加処理
"""
@app.route('/join_community/<int:community_id>', methods=['GET', 'POST'])
def join_community(community_id):
    # コミュニティへの参加処理
    return redirect(url_for('community_page', community_id=community_id))
"""
コミュニティ拒否処理
"""
@app.route('/reject_invitation/<int:community_id>', methods=['GET', 'POST'])
def reject_invitation(community_id):
    # 招待の拒否処理
    return redirect(url_for('home'))

@app.route('/community_edit')
def community_edit():
    comId = session['comId']
    community_detail = db.getcommunity_select(comId)
    public = community_detail[4]
    print(public)
    return render_template('user/community_edit.html',community_detail=community_detail,public=public)


@app.route('/community_edit_result',methods=['POST'])
def community_edit_result():
    com_id = request.form.get('com_id')
    com_name = request.form.get('com_name')
    fav_name = request.form.get('fav_name')
    com_public = request.form.get('com_public')
    com_explanation = request.form.get('com_explanation')
    
    count = db.community_update(com_id,com_name,fav_name,com_public,com_explanation)
    
    if count == 1:
        return redirect(url_for('community_edit_end'))
    else:
        return redirect(url_for('community_edit'))
    
@app.route('/community_edit_end')
def community_edit_end():
    msg = 'コミュニティ編集しました。'
    com_auth=db.get_comAuth(session['user_info'][0],session['comId'])
    if (com_auth==1):
        return render_template('user/community_set_master.html',comId=session['comId'],checkcal=0,msg=msg)
    else:
        return render_template('user/community_set_sub.html',comId=session['comId'],checkcal=0,msg=msg)

if __name__ == "__main__":
    app.run(debug=True)