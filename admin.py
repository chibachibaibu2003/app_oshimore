from flask import Flask,Blueprint ,render_template,redirect,url_for,request,session
import random,string,db,datetime

admin_bp=Blueprint('admin',__name__,url_prefix='/admin')

admin_bp.secret_key=''.join(random.choices(string.ascii_letters,k=256))