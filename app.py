from flask import Flask, render_template,redirect,url_for,request,session,jsonify,flash
import random,string,db,datetime,os,mail,urllib.parse,re,boto3

from hashids import Hashids
from admin import admin_bp
from user import user_bp

app = Flask(__name__)
app.secret_key=os.environ['sec_key']

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
        user = session['user_info']
        if(user[9]==1 or user[10]==1 ):
            return render_template('index.html')
        elif(user[8]==1):
            return redirect('/admin_menu')
        else:
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

    https://oshimore-90d6b34a7fa6.herokuapp.com/certification
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

@app.route('/certification1', methods=['POST'])
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
        return redirect(url_for('index'))
    else:
        return redirect(url_for('certification'))
    
@app.route('/password_reset')
def password_reset():
    return render_template('password_reset.html')

@app.route('/password_set', methods=['POST'])
def password_set():
    email = request.form.get('mail')
    if db.address_check_first(email):
        error = True
        return render_template('password_reset.html',error=error)
    else:
        code = db.create_code()
        to = email
        subject = "「Oshi More!」パスワード再設定メール"
        message = ('''
    Oshi More! からのパスワード再設定のメールです。 
    以下のURLからパスワードを再設定してください。 

    http://oshimore-90d6b34a7fa6.herokuapp.com/pass_certification
    認証コード : {} 
    ''').format(code)
        
        mail.send_mail(to,subject,message)
        db.pass_reset_register(email,code)
        return render_template('password_reset_mail.html')
    
@app.route('/pass_certification')
def pass_certification():
    return render_template('pass_certification.html')

@app.route('/pass_certification_exe', methods=['POST'])
def pass_certification_mail():
    mail = request.form.get('mail')
    code = request.form.get('code')
    session['email'] = mail
    if db.pass_certification_exe(mail,code):
        return render_template('password_update.html')
    else:
        return redirect(url_for('pass_certification'))
    
@app.route('/pass_certification_success', methods=['POST'])
def password_update_success():
    b_password = request.form.get('password')
    mail = session['email']
    salt = db.get_salt()
    print(salt)
    password = db.get_hash(b_password,salt)
    print(password)
    db.update_password(password,salt,mail)
    db.delete_reset_password(mail)
    return render_template('user/update_success.html')
    
""" 
マイページ画面・現在日時
"""

@app.route('/top/<int:checkcal>')
def top(checkcal):
    if 'user_info' in session:
        session['checkcal']=checkcal
        return redirect(url_for('mypage'))
    else:
        return redirect(url_for('index'))

@app.route('/admin_menu')
def admin_menu():
    if 'user_info' in session:
        return render_template('admin/menu.html')
    else:
        return redirect(url_for('index'))

@app.route('/mypage')
def mypage():
    if 'user_info' in session:
        if (session['checkcal']!=1):
            dt=datetime.datetime.now()
            session['month']=dt.month
            session['year']=dt.year
        searchDay=datetime.date(session['year'],session['month'],1)

        msg=session['msg']
        session['msg']=''
        datas=[]
        invitations=[]
        eventList=[]

        accId = session['user_info'][0]
        comIdList=db.getcomId_to_accId(session['user_info'][0])
        comIdList.append((0,))
        comIdList2=db.getcomId_to_accId_joined(session['user_info'][0])
        comIdList3=db.getcomId_to_accId_invit(session['user_info'][0])
        if(len(comIdList)!=0):
            for comId in comIdList:
                if (comId != 0):
                    eventList.append(db.getevent_to_comId(comId,searchDay))
                else:
                    eventList.append(db.getevent_to_accId(accId,comId,searchDay))
        if(len(comIdList2)!=0):
            for comId in comIdList2:
                datas.append(db.getcomInfo_to_comId(comId))
        if(len(comIdList3)!=0):
            for comId in comIdList3:
                invitations.append(db.getcomInfo_to_comId(comId))
        searchDay=f"{session['year']}-{session['month']}-"
        return render_template('user/menu.html', month=session['month'], year=session['year'], datas=datas, invitations=invitations, eventList=eventList, num1=len(comIdList), searchDay=searchDay, msg=msg)
    else:
        return redirect(url_for('index'))

""" 
マイページ画面・前の月へ
"""
@app.route('/monthback')
def monthback():
    if 'user_info' in session:
        session['month']-=1
        if(session['month']==0):
            session['month']=12
            session['year']-=1
        
        return redirect(url_for('top',checkcal=1))
    else:
        return redirect(url_for('index'))
""" 
マイページ画面・次の月へ
"""
@app.route('/monthnext')
def monthnext():
    if 'user_info' in session:
        session['month']+=1
        if(session['month']==13):
            session['month']=1
            session['year']+=1
        
        return redirect(url_for('top',checkcal=1))
    else:
        return redirect(url_for('index'))

@app.route('/event_thread_check/<int:id>')
def event_thread_check(id):
    if 'user_info' in session:
        session['event_threadId']=id
        return redirect(url_for('event_thread'))
    else:
        return redirect(url_for('index'))
    
@app.route('/event_thread',methods=['GET','POST'])
def event_thread():
    if 'user_info' in session:
        if request.method=='POST':
            postgood=request.form['post_good']
            postId=int(request.form['postId'])
            accId=int(request.form['accId'])
            if (postgood=="0"):
                cnt=db.event_post_good_del(postId,accId)
            elif (postgood=="1"):
                cnt=db.event_post_good(postId,accId)
            return jsonify({'msg' : 'success'})
        
        id=session['event_threadId']
        event_thread_list=[]
        event_thread_list_all=[]
        
        info_list=db.event_thread_info_search(id)
        event_thread_list=db.geteventThread_list_toeventId(id)
        
        for data in event_thread_list:
            goodcheck=db.geteventThread_good(data[0],data[3])
            event_thread_list_all.append([data[0],data[1],data[2],data[3],data[4],goodcheck[0]])
        URL=info_list[0][1]
        pattern='https?://'
        res = re.match(pattern, URL)
        if res!=None:
            data_list=[]
            for data in info_list[0]:
                data_list.append(data)
            return render_template('user/event_thread.html',info=data_list,thread_list=event_thread_list_all)
        else:
            data_list=[]
            for data in info_list[0]:
                data_list.append(data)
            data_list[1]='notUrl'
            return render_template('user/event_thread.html',info=data_list,thread_list=event_thread_list_all)
    else:
        return redirect(url_for('index'))

@app.route('/event_thread_report_check/<int:id>')
def event_thread_report_check(id):
    if 'user_info' in session:
        session['event_post_id']=id
        return redirect(url_for('event_thread_report'))
    else:
        return redirect(url_for('index'))

@app.route('/event_thread_report')
def event_thread_report():
    if 'user_info' in session:
        return render_template('user/event_post_report.html')
    else:
        return redirect(url_for('index'))

@app.route('/event_thread_report_exe',methods=['POST'])
def event_thread_report_exe():
    if 'user_info' in session:
        num = request.form.get('chiba')
        flg = False
        if num == "4":
            flg = True
        reason = "スパム" if num == "0" else "攻撃またはハラスメント" if num == "1" else "有害な誤情報または暴力の是認" if num == "2" else "個人を特定できる情報を晒している" if num == "3" else "その他"
        return render_template('user/event_post_report_exe.html',flg=flg,reason=reason,num=num)
    else:
        return redirect(url_for('index'))

@app.route('/event_report_success/<int:num>', methods=['POST'])
def event_report_success(num):
    if 'user_info' in session:
        postid=session['event_post_id']
        user_id = session['user_info'][0]
        reason = request.form.get('reason')
        if reason==None:
            reason = "None"
        db.report_event(postid,user_id,num,reason)
        msg = "通報完了しました"
        session['msg']=msg
        return redirect(url_for('top',checkcal=0))
    else:
        return redirect(url_for('index'))
    
@app.route('/register_community',methods=['POST'])
def register_community():
    if 'user_info' in session:
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
    else:
        return redirect(url_for('index'))


@app.route('/community/<int:id>/<int:checkcal>',methods=['GET','POST'])
def community(id,checkcal):
    if 'user_info' in session:
        if request.method=='POST':
            postgood=request.form['post_good']
            postId=int(request.form['postId'])
            accId=int(request.form['accId'])
            if (postgood=="0"):
                cnt=db.community_post_good_del(postId,accId)
            elif (postgood=="1"):
                cnt=db.community_post_good(postId,accId)
            return jsonify({'msg' : 'success'})
        
        session['checkcal']=checkcal
        session['comId']=id
        return redirect(url_for('community_page'))
    else:
        return redirect(url_for('index'))

@app.route('/community_page')
def community_page():
    if 'user_info' in session:
        if (session['checkcal']!=1):
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
        
        comname=db.getcomname_tocomId(session['comId'])
        eventList.append(db.getevent_to_comId(session['comId'],searchDay))
        searchDay=f"{session['year']}-{session['month']}-"
        community_thread_list=db.getcomtThread_list_tocomId(session['comId'])
        for data in community_thread_list:
            goodcheck=db.getcomThread_good(data[0],data[4])
            good_num=db.getcomThread_goodnum(data[0])
            community_thread_list_all.append([data[0],data[1],data[2],data[3],data[4],data[5],data[6],goodcheck[0],good_num[0]])
            cnt+=1
        return render_template('user/community.html', month=session['month'], year=session['year'], datas=datas, invitations=invitations, eventList=eventList, searchDay=searchDay,thread_list=community_thread_list_all,comId=session['comId'],checkcal=session['checkcal'],comname=comname)
    else:
        return redirect(url_for('index'))

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
    if 'user_info' in session:
        session['month']-=1
        if(session['month']==0):
            session['month']=12
            session['year']-=1
        
        return redirect(url_for('community',id=session['comId'],checkcal=1))
    else:
        return redirect(url_for('index'))

""" 
コミュニティ画面・次の月へ
"""

@app.route('/com_monthnext')
def com_monthnext():
    if 'user_info' in session:
        session['month']+=1
        if(session['month']==13):
            session['month']=1
            session['year']+=1
        
        return redirect(url_for('community',id=session['comId'],checkcal=1))
    else:
        return redirect(url_for('index'))

@app.route('/join_community/<int:community_id>', methods=['GET', 'POST'])
def join_community(community_id):
    if 'user_info' in session:
        account_id = session.get('user_info')[0]  # ユーザーのアカウントIDをセッションから取得
        if db.join_community(account_id, community_id):
            db.delete_invitation(account_id, community_id)  # 招待テーブルから削除
        return redirect(url_for('top', checkcal=0))
    else:
        return redirect(url_for('index'))

@app.route('/reject_invitation/<int:community_id>', methods=['GET', 'POST'])
def reject_invitation(community_id):
    if 'user_info' in session:
        account_id = session.get('user_info')[0]  # ユーザーのアカウントIDをセッションから取得
        db.delete_invitation(account_id, community_id)
        return redirect(url_for('top', checkcal=0))
    else:
        return redirect(url_for('index'))

@app.route('/community_edit')
def community_edit():
    if 'user_info' in session:
        comId = session['comId']
        community_detail = db.getcommunity_select(comId)
        public = community_detail[4]

        return render_template('user/community_edit.html',community_detail=community_detail,public=public)
    else:
        return redirect(url_for('index'))

@app.route('/community_edit_result',methods=['POST'])
def community_edit_result():
    if 'user_info' in session:
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
    else:
        return redirect(url_for('index'))

@app.route('/community_edit_end')
def community_edit_end():
    if 'user_info' in session:
        msg = 'コミュニティ編集しました。'
        com_auth=db.get_comAuth(session['user_info'][0],session['comId'])
        if (com_auth[0]==1):
            return render_template('user/community_set_master.html',comId=session['comId'],checkcal=0,msg=msg)
        else:
            return render_template('user/community_set_sub.html',comId=session['comId'],checkcal=0,msg=msg)
    else:
        return redirect(url_for('index'))
        
"""
アカウント退会
"""
@app.route('/account_withdraw')
def account_withdraw1():
    if 'user_info' in session:
        return render_template('user/account_withdraw.html')
    else:
        return redirect(url_for('index'))


@app.route('/account_withdraw2')
def account_withdraw2():
    if 'user_info' in session:
        return render_template('user/account_withdraw2.html',accId=session['user_info'][0])
    else:
        return redirect(url_for('index'))

@app.route('/account_withdraw3',methods=['POST'])
def account_withdraw3():
    if 'user_info' in session:
        accId = request.form.get('accId')
        count = db.account_withdraw(accId)
        return redirect(url_for('ac_withdraw_result'))
    else:
        return redirect(url_for('index'))

@app.route('/account_withdraw4')
def ac_withdraw_result():
    if 'user_info' in session:
        session.clear()
        return render_template('user/account_withdraw3.html')
    else:
        return redirect('index')

@app.route('/community_delete_check')
def community_delete_check():
    if 'user_info' in session:
        comname=db.getcommunity_select(session['comId'])
        return render_template('user/community_delete_check.html',comname=comname[1])
    else:
        return redirect('index')

@app.route('/community_delete',methods=['POST'])
def community_delete():
    if 'user_info' in session:
        count=db.community_delete(session['comId'])
        count2=db.register_community_delete(session['comId'])
        if (count==1 and count2>0):
            msg='コミュニティを削除しました!'
        else:
            msg='コミュニティを削除できませんでした...'
        session['msg']=msg
        return redirect(url_for('top',checkcal=0))
    else:
        return redirect(url_for('index'))
    
@app.route('/community_withdrawal_check')
def community_withdrawal_check():
    if 'user_info' in session:
        return render_template('user/withdrawl_check.html')
    else:
        return redirect(url_for('index'))

@app.route('/community_withdrawal_result')
def community_withdrawal_result():
    if 'user_info' in session:
        com_auth=db.get_comAuth(session['user_info'][0],session['comId'])
        if (com_auth[0]==1):
            db.remove_register_community(session['user_info'][0],session['comId'])
            count=db.count_community_member_num(session['comId'])
            if (count==0):
                db.community_delete(session['comId'])
            else:
                accId=db.get_nextReader_num(session['comId'])
                db.change_community_reader(accId[0],session['comId'])
        else:
            print(com_auth)
            db.remove_register_community(session['user_info'][0],session['comId'])
        return render_template('user/withdrawl_result.html')
    else:
        return redirect(url_for('index'))

@app.route('/community_search')
def community_search():
    if 'user_info' in session:
        return render_template('user/community_search.html')
    else:
        return redirect(url_for('index'))

@app.route('/community_search_exe', methods=['POST'])
def community_search_exe():
    if 'user_info' in session:
        keyword = request.form.get('keyword')
        result = db.community_search(keyword)
        cnt=len(result)
        return render_template('user/community_search_result.html',result=result,keyword=keyword,cnt=cnt)
    else:
        return redirect(url_for('index'))
    
@app.route('/search_join_community_set/<int:cnt>')
def search_join_community_set(cnt):
    session['cnt'] = cnt
    return redirect(url_for('search_join_community'))

@app.route('/search_join_community')
def search_join_community():
    if 'user_info' in session:
        community = db.select_community(session['cnt'])
        community={
            'id':community[0],
            'name':community[1],
            'oshiname':community[2],
            'overview':community[3]
        }
        text = "参加する"
        cls = 'invitation-btn'
        flg = db.community_join_check(session['user_info'][0],session['cnt'])
        if flg:
            text = "参加済み"
            cls = 'gain'
        session['community_id'] = session['cnt']
        return render_template('user/search_join_community.html',community=community,text=text,cls=cls)
    else:
        return redirect(url_for('index'))

@app.route('/join_commuinty_exe')
def join_community_exe():
    if 'user_info' in session:
        user = session['user_info']
        db.join_community(user[0],session['community_id'])
        return redirect(url_for('top',checkcal=1))
    else:
        return redirect(url_for('index'))

@app.route('/community_report_set/<int:id>')
def community_report_set(id):
    session['id'] = id
    return redirect(url_for('community_report'))

@app.route('/community_report')
def community_report():
    if 'user_info' in session:
        community = db.select_community(session['id'])
        community={
            'id':community[0],
            'name':community[1],
            'oshiname':community[2],
            'overview':community[3]
        }
        return render_template('user/community_report.html',community=community)
    else:
        return redirect(url_for('index'))


@app.route('/community_report_exe_set/<int:id>', methods=['POST'])
def community_report_exe_set(id):
    session['report_id'] = id
    num = request.form.get('chiba')
    session['num'] = num
    return redirect(url_for('community_report_exe'))

@app.route('/community_report_exe')
def community_report_exe():
    if 'user_info' in session:
        id = session['report_id']
        num = session['num']
        community = db.select_community(id)
        flg = False
        community={
            'id':community[0],
            'name':community[1],
            'oshiname':community[2],
            'overview':community[3]
        }
        if num == "4":
            flg = True
        reason = "スパム" if num == "0" else "攻撃またはハラスメント" if num == "1" else "有害な誤情報または暴力の是認" if num == "2" else "個人を特定できる情報を晒している" if num == "3" else "その他"
        return render_template('user/community_report_exe.html',flg=flg,reason=reason,community=community,num=num)
    else:
        return redirect(url_for('index'))

@app.route('/community_report_success/<int:id><int:num>', methods=['POST'])
def community_report_success(id,num):
    if 'user_info' in session:
        community = db.select_community(id)
        user_id = session['user_info'][0]
        reason = request.form.get('reason')
        if reason==None:
            reason = "None"
        db.report_community(community[0],user_id,num,reason)
        msg = "通報完了しました"
        session['msg']=msg
        return redirect(url_for('top',checkcal=0))
    else:
        return redirect(url_for('index'))

@app.route('/community_post',methods=['POST'])
def community_post():
    if 'user_info' in session:
        accId=session['user_info'][0]
        comId = session['comId']
        post = request.form.get('post')
        post_day = datetime.datetime.now()
        
        count = db.community_post(accId,comId,post,post_day)
        
        return redirect(url_for('community',id=comId,checkcal=0))
    else:
        return redirect(url_for('index'))

@app.route('/event_thread_post',methods=['POST'])
def event_thread_post():
    if 'user_info' in session:
        accId=session['user_info'][0]
        eventId = session['event_threadId']
        post = request.form.get('post')
        post_day = datetime.datetime.now()
        
        db.event_thread_post(accId,eventId,post,post_day)
        
        return redirect(url_for('event_thread'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if 'user_info' in session:
        session.pop('user_info',None)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

#コミュニティ招待表示
@app.route('/community/invitation/<int:community_id>')
def community_invitation(community_id):
    if 'user_info' in session:
        community_details = db.get_community_data(community_id)
        if community_details:
            # データを辞書形式でテンプレートに渡す
            community = {
                'id': community_details[0],
                'name': community_details[1],
                'oshiname': community_details[2],
                'overview': community_details[3]
            }
            current_user_id = session.get('user_info')[0]
            # user_detail 関数を使用してユーザーデータを取得
            user = db.user_detail(current_user_id)
            return render_template('user/community_invitation.html', community=community)
        else:
            return redirect(url_for('error_404'))
    else:
        return redirect(url_for('index'))
    
#ユーザー検索
@app.route('/community_user_search', methods=['GET', 'POST'])
def community_user_search():
    if 'user_info' in session:
        community_id = session.get('comId')
        account_id = session['user_info'][0]
        if request.method == 'POST':
            search_query = request.json['search_query']  # Ajax リクエストからデータを取得
            search_results = db.search_users(search_query,account_id,comId=community_id)
            return jsonify(search_results)  # 検索結果を JSON で返す
        return render_template('user/community_user_search.html')
    else:
        return redirect(url_for('index'))

@app.route('/user_detail/<user_id>')
def user_detail_route(user_id):
    if 'user_info' in session:
        community_id = session.get('comId')
        user_info = db.user_detail(user_id)
        if user_info:
            return render_template('user/user_detail.html', user=user_info, community_id=community_id)
        else:
            return 'ユーザーが見つかりません', 404
    else:
        return redirect(url_for('index'))


@app.route('/invite_user/<int:community_id>/<int:account_id>', methods=['POST'])
def invite_user(community_id, account_id):
    if 'user_info' in session:
        success = db.insert_invitation(community_id, account_id)
        if success:
            flash('招待が成功しました。', 'success')
        else:
            flash('招待に失敗しました。', 'error')
        return redirect(url_for('community_user_search'))
    else:
        return redirect(url_for('index'))

@app.route('/event_register')
def event_register():
    return render_template('user/event_register.html',comId=session['comId'],checkcal=0)

@app.route('/event_register_exe',methods=['POST'])
def event_register_exe():
    account_id = session['user_info'][0]
    community_id = session.get('comId')
    title = request.form.get('title')
    start_day = request.form.get('start_day')
    end_day = request.form.get('end_day')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    url = request.form.get('url')
    explanation = request.form.get('explanation')



    count = db.event_register(title,start_day,end_day,start_time,end_time,url,explanation,account_id,community_id)

    if count==0:
        msg='イベント追加に失敗しました'
        return render_template('user/event_register.html',comId=community_id,checkcal=0,msg=msg)

    return redirect(url_for('event_register_result'))


@app.route('/event_register_success')
def event_register_result():
    msg = 'イベントを追加しました。'
    return render_template('user/event_register.html',comId=session['comId'],checkcal=0,msg=msg)


@app.route('/user_event')
def use_event_register():
    return render_template('user/user_event_register.html')


@app.route('/user_event_exe' ,methods=['POST'])
def user_event_exe():
    account_id = session['user_info'][0]
    community_id = 0
    title = request.form.get('title')
    start_day = request.form.get('start_day')
    end_day = request.form.get('end_day')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    url = request.form.get('url')
    explanation = request.form.get('explanation')

    count = db.event_register(title, start_day, end_day, start_time, end_time, url, explanation, account_id,
                              community_id)

    if count == 0:
        msg = 'イベント追加に失敗しました'
        return render_template('user/user_event_register.html', comId=community_id, checkcal=0, msg=msg)

    return redirect(url_for('user_event_result'))


@app.route('/user_event_success')
def user_event_result():
    msg = 'イベントを追加しました。'
    return render_template('user/user_event_register.html', comId=session['comId'], checkcal=0, msg=msg);


@app.route('/event_edit')
def event_edit():
    event_id = session['event_threadId']
    event_info = db.event_info_search(event_id)


    if session['user_info'][0]!=event_info[8]:
        msg = '作成者ではないため編集出来ません'
        return redirect(url_for('event_thread_check',id=event_info[0],msg=msg))
    else:
        return render_template('user/event_edit.html',event_info=event_info)

@app.route('/event_edit_result',methods=['POST'])
def event_edit_result():
    event_id = request.form.get('event_id')
    title = request.form.get('title')
    start_day = request.form.get('start_day')
    end_day = request.form.get('end_day')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    url = request.form.get('url')
    explanation = request.form.get('explanation')

    count = db.event_update(event_id,title,start_day,end_day,start_time,end_time,url,explanation)
    if(count==1):
        return redirect(url_for('event_edit_success'))
    else:
        msg = 'イベント編集に失敗しました。'
        return redirect(url_for('event_edit',msg=msg))

@app.route('/event_edit_success')
def event_edit_success():
    return redirect(url_for('event_thread_check',id=session['event_threadId']))



@app.route('/event_delete')
def event_delete():
    event_id = session['event_threadId']
    event_info = db.event_info_search(event_id)

    if session['user_info'][0] != event_info[8]:
        msg = '作成者ではないため削除出来ません'
        session['message']=msg
        return redirect(url_for('event_thread_check', id=event_info[0]))
    else:
        return render_template('user/event_delete.html', event_info=event_info)

@app.route('/event_delete_result')
def event_delete_result():
    event_id = session['event_threadId']
    event_post_info = db.select_event_post_by_id(event_id)
    count1 = db.event_post_delete(event_id)
    count2 = db.event_post_report_delete(event_post_info)
    count3 = db.event_good_delete(event_post_info)
    count4 = db.event_delete(event_id)

    if(count4==1):
        msg = 'イベントを一件を削除しました'
        session['message'] = msg
        return redirect(url_for('top',id=session['user_info'][0],checkcal=0,msg=msg))
    else:
        return redirect(url_for('event_thread_check', id=session['event_threadId']))
      
@app.route('/report/<int:post_id>', methods=['GET', 'POST'])
def report(post_id):
    if request.method == 'POST':
        report_category = request.form.get('report_category')
        # 確認画面に遷移
        return render_template('user/confirm_report.html', post_id=post_id, report_category=report_category)

    # GETリクエストの場合、通報理由選択画面を表示
    return render_template('user/community_postreport.html', post_id=post_id)

@app.route('/confirm_report/<int:post_id>', methods=['POST'])
def confirm_report(post_id):
    user_info = session.get('user_info')
    if not user_info:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('login_page'))  # ログインページへリダイレクト

    report_category = request.form.get('report_category')
    report_detail = request.form.get('report_detail', None)
    reporter_id = user_info[0]

    success = db.insert_community_post_report(post_id, reporter_id, report_category, report_detail)
    if success:
        flash('通報が完了しました。', 'success')
    else:
        flash('通報に失敗しました。', 'error')
    
    comId = session.get('comId')  # セッションからcomIdを取得
    if comId is None:
        return redirect(url_for('index'))  # comIdがない場合は別のページへリダイレクト

    return redirect(url_for('community',id=comId,checkcal=0))

@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    user_info = session.get('user_info')
    if not user_info:
        flash('セッション情報が不足しています。もう一度ログインしてください。')
        return redirect(url_for('login'))
    account_id = user_info[0]

    if request.method == 'POST':
        account_name = request.form['account_name']
        new_user_id = request.form['user_id']
        profile = request.form['profile']
        file = request.files['file']

        # ユーザーIDの重複チェック
        if new_user_id != user_info[1] and db.check_user_id_exists(new_user_id):
            msg = 'このユーザーIDは既に使用されています。別のIDを選択してください。'
        else:
            
            
          # 推しリストの公開/非公開設定
            all_oshi_ids = [oshi['community_id'] for oshi in db.get_oshi_list(account_id)]
            oshi_list_settings = {str(oshi_id): 0 for oshi_id in all_oshi_ids}
            for key in request.form:
                if key.startswith('oshi_'):
                    oshi_id = key.split('_')[1]
                    oshi_list_settings[oshi_id] = 1 - oshi_list_settings[oshi_id]

            # AWS S3への画像アップロード
            if file and file.filename != '':
                filename = f'user{account_id}_icon.png'
                s3 = boto3.client('s3',
                                  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                  aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                  region_name=os.environ.get('AWS_DEFAULT_REGION'))
                s3.upload_fileobj(file, 'oshimore', f'img/{filename}')
                icon_url = filename
            else:
                # 画像がアップロードされていない場合、以前のアイコンURLを使用
                icon_url = user_info[7]

            # データベースの更新
            update_result = db.update_user_profile(account_id, new_user_id, account_name, profile, icon_url,oshi_list_settings)
            if update_result:
                updated_user_info = db.get_user_profile(account_id)
                if updated_user_info:
                    session['user_info'] = updated_user_info
                    msg = 'プロフィールが更新されました。'
                else:
                    msg = 'プロフィールの更新に失敗しました。'
            else:
                msg = 'プロフィールの更新に失敗しました。'

        session['msg'] = msg
        return redirect(url_for('editprofile'))

    else:
        user_info = db.get_user_profile(account_id)
        user_data = {
            'user_id': user_info[1],
            'account_name': user_info[3],
            'profile': user_info[6],
            'icon_url': user_info[7]
        }
        msg = session.get('msg', '')
        session['msg'] = ''
        oshi_list = db.get_oshi_list(account_id)  
        return render_template('user/editprofile.html', user=user_data, oshis=oshi_list, msg=msg)

@app.route('/community_auth_change', methods=['GET', 'POST'])
def community_auth_change():
    if 'user_info' not in session:
        flash('ログインが必要です。')
        return redirect(url_for('login'))
    
    account_id = session['user_info'][0]
    community_id = session.get('community_id')

    if request.method == 'POST':
        print("Received POST Data:", request.form)
        form_data = dict(request.form)
        for key, values in request.form.lists():
            if key.startswith('authority_'):
                member_id = key.split('_')[-1]
                new_authority = values[-1]
                db.update_authority(member_id, new_authority)
            elif key.startswith('community_authority_'):
                member_id = key.split('_')[-1]
                new_community_authority = values[-1]
                db.update_community_authority(member_id, new_community_authority)

        return redirect(url_for('community_auth_change', community_id=community_id))

    members = db.get_community_members(account_id)
    return render_template('user/community_auth_change.html', members=members)

@app.route('/report_post_list')
def report_post_list():
    if 'user_info' in session:
        report_list=db.community_post_reportList(session['comId'])
        print(report_list)
        msg=session['msg']
        session['msg']=''
        return render_template('user/community_post_reportList.html',report_list=report_list,msg=msg)
    else:
        return redirect(url_for('index'))

@app.route('/report_post_check/<int:postId>')
def report_post_check(postId):
    if 'user_info' in session:
        session['report_post_id']=postId
        return redirect(url_for('report_post_select'))
    else:
        return redirect(url_for('index'))

@app.route('/report_post_select')
def report_post_select():
    if 'user_info' in session:
        postId=session['report_post_id']
        return render_template('user/community_post_report_check.html',id=postId)
    else:
        return redirect(url_for('index'))

@app.route('/report_post_delete/<int:postId>')
def report_post_delete(postId):
    if 'user_info' in session:
        print(postId)
        session['msg']='投稿を削除しました'
        db.del_community_post(session['report_post_id'])
        db.del_community_post_reportList(session['report_post_id'])
        return redirect(url_for('report_post_list'))
    else:
        return redirect(url_for('index'))

@app.route('/report_post_protect/<int:postId>')
def report_post_protect(postId):
    if 'user_info' in session:
        print(postId)
        session['msg']='投稿を保護しました'
        db.del_community_post_reportList(session['report_post_id'])
        return redirect(url_for('report_post_list'))
    else:
        return redirect(url_for('index'))


@app.route('/calender_set',methods=['GET','POST'])
def calender_set():
    user_info = session['user_info']
    if not user_info:
        flash('セッション情報が不足しています。もう一度ログインしてください。')
        return redirect(url_for('index'))
    account_id = user_info[0]
    comInfo_list = db.getcom_info_list(account_id)

    if request.method == 'POST':
        for comInfo in comInfo_list:
            comId = comInfo[0]
            calendar_hidden_flag = request.form.get('calendar_'+str(comId))

            if calendar_hidden_flag==None:
                calendar_hidden_flag=1

            db.calendar_hidden(comId,account_id,calendar_hidden_flag)
            msg = '変更を保存しました。'
        return redirect(url_for('top',checkcal=0))


    return render_template('user/calender_set.html',comInfo_list=comInfo_list)

if __name__ == "__main__":
        app.run(debug=True)