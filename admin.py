from flask import Flask,Blueprint ,render_template,redirect,url_for,request,session,jsonify
import random,string,db,datetime,boto3

admin_bp=Blueprint('admin',__name__,url_prefix='/admin')

admin_bp.secret_key=''.join(random.choices(string.ascii_letters,k=256))

@admin_bp.route('/')
def index():
    session['msg']=''
    return render_template('index.html')

@admin_bp.route('/admin_menu')
def admin_menu():
    if 'user_info' in session and session['user_info'][8]==1:
        msg=session['msg']
        session['msg']=''
        return render_template('admin/menu.html',msg=msg)
    else:
        return redirect(url_for('index'))

@admin_bp.route('/user_menu')
def user_menu():
    if 'user_info' in session and session['user_info'][8]==1:
        return render_template('admin/user_menu.html')
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/report_user_list')
def report_user_list():
    if 'user_info' in session and session['user_info'][8]==1:
        user_list=db.ban_userList_search()
        print(user_list)
        return render_template('admin/user_list.html',user_list=user_list)
    else:
        return redirect(url_for('index'))    

@admin_bp.route('/report_user_search',methods=['GET','POST'])
def report_user_search():
    if 'user_info' in session and session['user_info'][8]==1:
        if request.method == 'POST':
            search_query = request.json['search_query']  # Ajax リクエストからデータを取得
            search_results = db.report_user_search(search_query,session['user_info'][0])
            return jsonify(search_results)  # 検索結果を JSON で返す
        return render_template('admin/user_search.html')
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/user_detail/<int:id>')
def user_detail(id):
    if 'user_info' in session and session['user_info'][8]==1:
        report_post_list=[]
        events=db.event_postList_toaccId(id)
        events2=db.community_postList_toaccId(id)
        cnt=0
        for event_info in events:
            info_list=[]
            event=db.event_reportList_toPostId(event_info[0])
            if event!=0:
                for info in event:
                    info_list.append(info)
                if (info_list[2]=='0'):
                    info_list[2]='スパム'
                    report_post_list.append(info_list)
                    cnt+=1
                elif (info_list[2]=='1'):
                    info_list[2]='攻撃またはハラスメント'
                    report_post_list.append(info_list)
                    cnt+=1
                elif (info_list[2]=='2'):
                    info_list[2]='有害な誤情報または暴力の是認'
                    report_post_list.append(info_list)
                    cnt+=1
                elif (info_list[2]=='3'):
                    info_list[2]='個人を特定できる情報を晒している'
                    report_post_list.append(info_list)
                    cnt+=1
                elif (info_list[2]=='4'):
                    info_list[2]='その他'
                    report_post_list.append(info_list)
                    cnt+=1
                    
        for event_info2 in events2:
            info_list=[]
            event=db.community_reportList_toPostId(event_info2[0])
            if event!=0:
                cnt+=1
                for info in event:
                    info_list.append(info)
                report_post_list.append(info_list)
        
        session['reporter_id']=id
        session['event_post_list']=report_post_list
        session['report_num']=cnt
        return redirect(url_for('admin.report_detail'))
    else:
        return redirect(url_for('index'))

@admin_bp.route('/report_detail')
def report_detail():
    if 'user_info' in session and session['user_info'][8]==1:
        event_post_list=session['event_post_list']
        cnt=session['report_num']
        account_info=db.get_accountInfo_toaccId(session['reporter_id'])
        session['account_info']=account_info
        return render_template('admin/user_detail.html',info=account_info,cnt=cnt,post_list=event_post_list)
    else:
        return redirect(url_for('index'))

@admin_bp.route('/reporter_profile')
def reporter_profile():
    if 'user_info' in session and session['user_info'][8]==1:
        user_info = db.user_detail(session['account_info'][1])
        return render_template('admin/reporter_profile.html',user=user_info)
    else:
        return redirect(url_for('index'))

@admin_bp.route('/user_ban_check')
def user_ban_check():
    if 'user_info' in session and session['user_info'][8]==1:
        return render_template('admin/user_ban_check.html')
    else:
        return redirect(url_for('index'))

@admin_bp.route('/user_ban')
def user_ban():
    if 'user_info' in session and session['user_info'][8]==1:
        msg="BANしました！"
        session['msg']=msg
        db.ban_user_toaccId(session['reporter_id'])
        db.del_event_toaccId(session['reporter_id'])
        db.del_comThread_toaccId(session['reporter_id'])
        return redirect('admin_menu')
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/community_menu')
def community_menu():
    if 'user_info' in session:
        return render_template('admin/community_menu.html')
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/report_community_search')
def report_community_search():
    if 'user_info' in session:
        return render_template('admin/community_search.html')
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/community_search',methods=['POST'])
def community_search():
    if 'user_info' in session:
        keyword = request.form.get('name')
        result = db.report_community_search(keyword)
        return render_template('admin/community_search_result.html',keyword=keyword,result=result)
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/community_management_set/<int:id>')
def community_management_set(id):
    if 'user_info' in session:
        session['id'] = id
        return redirect(url_for('admin.community_management')) 
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/community_management')
def community_management():
    if 'user_info' in session:
        id = session['id'] 
        result = db.select_community(id)
        cushion = db.account_id_search(result[0])
        name = db.user_id_search(cushion)
        report = db.report_count(result[0])
        cnt = len(report)
        session['community_id'] = id
        return render_template('admin/community_ban.html',community=result,name=name,report=report,cnt=cnt)
    else:
        return redirect(url_for('index'))
    
@admin_bp.route('/commuinty_ban_check')
def community_ban_check():
    if 'user_info' in session:
        return render_template('admin/community_ban_check.html')
    else:
        return redirect(url_for('index'))

    
@admin_bp.route('/community_ban')
def community_ban():
    if 'user_info' in session:
        msg="BANしました！"
        session['msg']=msg
        print(session['community_id'])
        db.ban_community(session['community_id'])
        db.delete_rc(session['community_id'])
        return redirect('admin_menu')
    else:
        return redirect(url_for('index'))