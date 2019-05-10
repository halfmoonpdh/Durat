from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import re
import time

from .forms import UserCreationMultiForm, TagingDataForm, DocumentForm
from .models import *
from .jongmodel import *

TAG = ['RE_S', 'RE_D', 'EX_E', 'EX_R', 'EX_M', 'PR', 'OB']

def get_time():
    now = time.localtime()
    return "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

# Create your views here.
class SignUp(generic.CreateView):
    form_class = UserCreationMultiForm
    success_url = reverse_lazy('login')
    template_name = 'brat/signup.html'

    def form_valid(self, form):
        user = form['user'].save()
        profile = form['profile'].save(commit=False)
        profile.user = user
        profile.save()
        return redirect(self.success_url)

def home(request, message=None, is_admin=False):
    taging_list = TagingList.objects.all()
    taging_list_count = taging_list.count()
    try:
        if type(request.user).__name__ == "SimpleLazyObject":
            user = User.objects.get(username=request.user.username)
            user_ = Profile.objects.get(user_id=user.id)
            if not user_.taging_count:
                message = "관리자모드로 접속 완료"
                return render(request, 'brat/home.html',
                              {'taging_list': taging_list, 'taging_list_count': taging_list_count,
                               'message': message, 'admin': True})
            else:
                return render(request, 'brat/home.html',
                              {'taging_list': taging_list, 'taging_list_count': taging_list_count,
                               'message': message, 'admin': False})
    except:
        return render(request, "brat/home.html", {'taging_list': taging_list, 'taging_list_count': taging_list_count,
                           'message': message, 'admin': False})

@login_required
def listcreate(request):
    import os
    if request.method == "POST":
        if TagingList.objects.filter(taging_list_title=request.POST['listname']).exists():
            message = "이미 존재하는 이름입니다."
            return home(request, message)
        else:
            if re.compile('[A-Za-z_]+').match(request.POST['listname']):
                os.mkdir('media/brat/' + request.POST['listname'])
                TagingList.objects.create(taging_list_title=request.POST['listname'])
                return HttpResponseRedirect("/home")
            else:
                message = "영어 대소문자 및 _만 사용가능합니다."
                return home(request, message)

    return render(request, "brat/listcreate.html", {})

def datalist(request, taging_list_title, message=None):
    taging_list = TagingList.objects.all()
    taging_list_title_id = TagingList.objects.get(taging_list_title=taging_list_title)
    taging_data_list = TagingData.objects.filter(taging_list_id=taging_list_title_id.id).order_by('-taging_data_created')

    return render(request, 'brat/datalist.html', {'taging_data_list': taging_data_list, 'taging_list': taging_list,
                                                  'taging_list_title': taging_list_title, 'message': message})

@login_required
def create_to_file(request, taging_list_title):

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdata = Document(datafile=request.FILES['datafile'])
            newdata.save()
            data_location = str(newdata)
            data_type = data_location.split(".")[1]
            data_name = data_location.split("\\")[-1].split(".")[0]
            if (data_type == "txt"):
                # txt면 데이터를 하나 만들고 삭제하기
                with open(str(newdata), 'r', encoding='utf-8') as f:
                    text_from_txt = f.read()
                    taging_data = TagingData.objects.create(
                        taging_data_title=data_name,
                        taging_data_detail=text_from_txt,
                        taging_data_ann="",
                        taging_list=TagingList.objects.get(taging_list_title=taging_list_title))
                    print(text_from_txt)
                    taging_data.save()
                makeratemodel(taging_list_title, taging_data.id)
                newdata.delete()
                return HttpResponseRedirect("/home/{}".format(taging_list_title))
            else:
                message = "txt파일이 아닙니다."
                newdata.delete()
                return datalist(request, taging_list_title, message)

    return render(request, "brat/createtofile.html", {})

@login_required
def listrename(request, taging_list_title):
    if request.method == "POST":
        if request.POST['yesno'] == "yes":
            if TagingList.objects.filter(taging_list_title=request.POST['listname']).exists():
                message = "이미 존재하는 이름입니다."
                return home(request, message)
            else:
                if re.compile('[A-Za-z_]+').match(request.POST['listname']):
                    ta = TagingList.objects.get(taging_list_title=taging_list_title)
                    ta.taging_list_title = request.POST['listname']
                    ta.save()
                    return HttpResponseRedirect('/home')
                else:
                    message = "영어 대소문자 및 _만 사용가능합니다."
                    return home(request, message)

        elif request.POST['yesno'] == "no":
            message = "취소!"
            return home(request, message)
    return render(request, "brat/listrename.html", {})

@login_required
def listdelete(request, taging_list_title):
    if request.method == "POST":
        if request.POST['yesno'] == "yes":
            import os
            import string
            import random
            _LENGTH = 8  # 8자리
            # 숫자 + 대소문자
            string_pool = string.ascii_letters + string.digits
            # 랜덤한 문자열 생성
            result = ""
            for i in range(_LENGTH):
                result += random.choice(string_pool)  # 랜덤한 문자열 하나 선택

            TagingList.objects.filter(taging_list_title=taging_list_title).delete()
            message = taging_list_title+"삭제를 성공하였습니다."
            os.rename('media/brat/'+taging_list_title+'/','media/brat/'+taging_list_title+'_'+result+'_deleted/')
            return home(request, message)
        elif request.POST['yesno'] == "no":
            message = "취소!"
            return home(request, message)
    return render(request, "brat/listdelete.html", {})


def detail(request, taging_list_title, taging_data_id, is_success=False):
    taging_data = TagingData.objects.get(pk=taging_data_id)
    tad_list = taging_data.taging_data_detail.split("\n")
    taging_list = TagingList.objects.all()


    taging_data_ann = taging_data.taging_data_ann
    ann = taging_data_ann.split("\r\n")
    ann_dic = {}
    for ann_ in ann:
        i = ann_.split(" ")
        if(i[0] is not ""):
            ann_dic[i[0]] = i[1]

    return render(request, 'brat/detail.html', {'taging_list_title': taging_list_title, 'taging_data_id': taging_data_id,
                                                'taging_list': taging_list, 'taging_data': taging_data,
                                                'tad_list': tad_list, 'ann_dic': ann_dic, 'is_success': is_success})

@login_required
def create(request, taging_list_title):

    if request.method == 'POST':
        form = TagingDataForm(request.POST, request.FILES)

        if form.is_valid():
            taging_data = TagingData.objects.create(
                taging_data_title=form.cleaned_data['taging_data_title'],
                taging_data_detail=form.cleaned_data['taging_data_detail'],
                taging_data_ann=form.cleaned_data['taging_data_ann'],
                taging_list=TagingList.objects.get(taging_list_title=taging_list_title))
            taging_data.save()
            makeratemodel(taging_list_title, taging_data.id)

            return HttpResponseRedirect("/home/{}".format(taging_list_title))
    else:
        form = TagingDataForm()

    return render(request, 'brat/create.html', {'form': form})

@login_required
def dataedit(request, taging_list_title, taging_data_id):

    taging_data = TagingData.objects.get(pk=taging_data_id)
    taging_data_detail = taging_data.taging_data_detail
    taging_data_ann = taging_data.taging_data_ann
    taging_list = TagingList.objects.all()

    if request.method == 'POST':
        taging_data.taging_data_detail = request.POST['detail']
        taging_data.taging_data_ann = request.POST['ann']
        taging_data.taging_is_taging = True
        taging_data.save()
        return HttpResponseRedirect("/home/{}/{}".format(taging_list_title, taging_data_id))

    return render(request, 'brat/dataedit.html', {'taging_list': taging_list, 'title': taging_data.taging_data_title, 'detail': taging_data_detail, 'ann': taging_data_ann })

@login_required
def datarename(request, taging_list_title, taging_data_id):
    if request.method == "POST":
        ta = TagingData.objects.get(pk=taging_data_id)
        ta.taging_data_title = request.POST['dataname']
        ta.save()
        return HttpResponseRedirect("/home/{}".format(taging_list_title))

    return render(request, "brat/datarename.html", {})

@login_required
def datadelete(request, taging_list_title, taging_data_id):
    taging_list = TagingList.objects.all()

    if request.method == 'POST':
        taging_data = TagingData.objects.get(pk=taging_data_id)

        if request.POST['yesno'] == "yes":
            taging_data.delete()
            return HttpResponseRedirect("/home/{}".format(taging_list_title))

        elif request.POST['yesno'] == "no":
            return HttpResponseRedirect("/home/{}/{}".format(taging_list_title, taging_data_id))

    return render(request, 'brat/delete.html', {'taging_list': taging_list})

@login_required
def autoannotation(request, taging_list_title, taging_data_id):
    taging_data = TagingData.objects.get(pk=taging_data_id)
    tad_list = taging_data.taging_data_detail.split("\n")
    result = ""

    j=1
    s = get_time()
    for i in tad_list:
        temp = model_predict(i)
        result = result+str(j)+" "+temp+"\r\n"
        taging_data_rate = TagingDataRate.objects.get(taging_data_id=taging_data_id, taging_number=j)
        taging_data_rate.taging_log += s + " " + "auto" + " " + temp + "추가 \n"
        taging_data_rate.save()
        j = j+1

    taging_data.taging_data_ann = taging_data.taging_data_ann + result
    taging_data.taging_Data_modified = s
    taging_data.save()
    print("자동태깅 완료")

    return HttpResponseRedirect("/home/{}/{}".format(taging_list_title, taging_data_id))

@login_required
def datarate(request, taging_list_title, taging_data_id):
    taging_list = TagingList.objects.all()
    taging_data = TagingData.objects.get(pk=taging_data_id)
    taging_rate_list = TagingDataRate.objects.filter(taging_data=taging_data).order_by('taging_number')

    return render(request, 'brat/datarate.html', {'taging_list': taging_list, 'taging_data': taging_data, 'taging_rate_list': taging_rate_list})

@login_required
def different_user(request, taging_list_title, taging_data_id):
    taging_list = TagingList.objects.all()
    taging_data = TagingData.objects.get(pk=taging_data_id)
    tad_list = taging_data.taging_data_detail.split("\n")
    taging_data_user_log = TagingDataRate.objects.filter(taging_data=taging_data)

    taging_user_tag = {}

    for taging_data_rate_taging_log in taging_data_user_log:
        taging_number = taging_data_rate_taging_log.taging_number

        seperate_logs = taging_data_rate_taging_log.taging_log.split("\n")

        for seperate_log in seperate_logs:
            if seperate_log == "":
                continue
            tag_user = seperate_log.split()[2]
            if tag_user == "auto":
                continue
            if tag_user not in taging_user_tag:
                taging_user_tag[tag_user] = []

            taging_user_tag[tag_user].append(str(taging_number) + "번 " + seperate_log + "\n")

    return render(request, 'brat/DiffrentUser.html', {'taging_list': taging_list, "taging_user_tag": taging_user_tag,
                                                      'tad_list': tad_list})

@login_required
def userratemodify(request, taging_list_title, taging_data_id):
    taging_data = get_object_or_404(TagingData, pk=taging_data_id)
    # 변한게 없는데 수정할때
    if taging_data.taging_is_taging == False:
        return render(request, 'brat/userrate_confirm.html', {})
    # 그냥 수정할때
    else:
        makeratemodel(taging_list_title, taging_data_id)

@login_required
def userratemodify_confirm(request, taging_list_title, taging_data_id):
    taging_data = get_object_or_404(TagingData, pk=taging_data_id)
    message = ""

    if taging_data.taging_is_taging == False:
        message = "변경 된 것이 없습니다. 안해도 됩니다..."

    if request.method == "POST":
        if request.POST['yesno'] == 'yes':
            makeratemodel(taging_list_title, taging_data_id)
            return HttpResponseRedirect("/home/{}/{}".format(taging_list_title, taging_data_id))
        if request.POST['yesno'] == 'no':
            return HttpResponseRedirect("/home/{}/{}".format(taging_list_title, taging_data_id))

    return render(request, 'brat/userrate_confirm.html', {'message': message})

def makeratemodel(taging_list_title, taging_data_id):
    taging_data = get_object_or_404(TagingData, pk=taging_data_id)
    taging_data_rate = TagingDataRate.objects.filter(taging_data_id=taging_data_id)
    tad_list = taging_data.taging_data_detail.split("\n")
    taging_data_ann = taging_data.taging_data_ann.split("\r\n")
    num = 1
    # 데이터베이스 저장 후 초기화 해야함
    # 만들어지자마자 모델 만들때
    if taging_data.tagingdatarate_set.count() == 0:
        pass
    # 이미 만들어진 모델이 있을때 파일로 저장
    else:
        file = open('media/brat/'+taging_list_title+'/'+str(taging_data_id)+'_'+str(taging_data.taging_modified)+'.txt', 'w', encoding='utf8')
        log = ''
        for i in taging_data_rate:
            for j in i.taging_log.split("\n"):
                log += str(i.taging_number)+' '+i.taging_text[:15]+' '+i.taging_tag+' '+j+'\n'
        file.write(log)
        file.close()
        taging_data.taging_modified += 1
        taging_data_rate_delete = taging_data_rate.delete()
        taging_data.save()
    # ==================================
    for i in tad_list:
        # 현재 태깅이 되어있는 상태에서 누를때
        if taging_data_ann:
            temp = ""
            for j in taging_data_ann:
                if j == "":
                    continue
                jsp = j.split()
                if int(jsp[0]) == num:
                    temp = jsp[1]
                    break
                else:
                    pass
            create_taging_log = TagingDataRate.objects.create(
                taging_data=TagingData.objects.get(pk=taging_data_id),
                taging_number=num,
                taging_tag=temp,
                taging_text=i
            )
        # 태깅이 아무것도 없는거 따로
        else:
            create_taging_log = TagingDataRate.objects.create(
                taging_data=TagingData.objects.get(pk=taging_data_id),
                taging_number=num,
                taging_text=i
            )
        num = num+1

    return HttpResponseRedirect('home/{}/{}'.format(taging_list_title, taging_data_id))

@login_required
def tagedit(request, taging_list_title, taging_data_id, tag_number):
    taging_data = TagingData.objects.get(pk = taging_data_id)
    taging_data_ann = taging_data.taging_data_ann
    taging_data_rate = TagingDataRate.objects.get(taging_data_id=taging_data_id, taging_number=tag_number)
    ann = taging_data_ann.split("\r\n")

    checked = ""
    blank = True

    for ann_ in ann:
        i = ann_.split(" ")
        if i[0] == str(tag_number):
            checked = i[1]

    if request.method == 'POST':
        user_ = User.objects.get(username=request.user.username)
        user = Profile.objects.get(user_id=user_.id)

        s = get_time()

        if request.POST['tag'] == "delete":
            blank = False
            for ann_ in ann:
                temp = ann_.split(" ")
                if temp[0] == str(tag_number):
                    ta = taging_data_ann.replace(str(temp[0])+" "+checked, "")
                    taging_data.taging_data_ann = ta
                    taging_data.save()

                    taging_data_rate.taging_log += ""+s+" "+request.user.username+" "+checked+" >> delete \n"
                    taging_data_rate.taging_tag = ""
                    taging_data_rate.save()
                    break

        elif request.POST['tag'] in TAG:
            for ann_ in ann:
                temp = ann_.split(" ")
                if temp[0] == str(tag_number):
                    ta = taging_data_ann.replace(str(temp[0])+" "+checked, str(temp[0])+" "+request.POST['tag'])
                    taging_data.taging_data_ann = ta
                    blank = False
                    taging_data.save()

                    taging_data_rate.taging_log += ""+s + " " + request.user.username +" "+checked +"에서 "+request.POST['tag']+"로 변경 \n"
                    taging_data_rate.taging_tag = request.POST['tag']
                    taging_data_rate.save()

                    if user.for_document_taging_count != taging_data.id:
                        user.for_document_taging_count = taging_data.id
                        user.for_document_taging_count_num = 1
                    else:
                        user.for_document_taging_count_num += 1
                        if user.for_document_taging_count_num >2:
                            user.document_taging_count +=1
                            user.for_document_taging_count_num = 0

                    user.save()

                    break

        #새로운 태그 추가
        if blank == True:
            ta = taging_data_ann + str(tag_number) + " " + request.POST['tag'] + "\r\n"
            taging_data.taging_data_ann = ta
            taging_data.save()

            taging_data_rate.taging_log += ""+s + " " + request.user.username + " " + request.POST['tag'] + " 추가 \n"
            taging_data_rate.taging_tag = request.POST['tag']
            taging_data_rate.save()

            if user.for_document_taging_count != taging_data.id:
                user.for_document_taging_count = taging_data.id
                user.for_document_taging_count_num = 1
            else:
                user.for_document_taging_count_num += 1
                if user.for_document_taging_count_num > 2:
                    user.document_taging_count += 1
                    user.for_document_taging_count_num =0

            user.save()

        return HttpResponseRedirect("/home/{}/{}".format(taging_list_title, taging_data_id))

    return render(request, 'brat/tagedit.html', {'TAG': TAG, 'checked': checked})






##admin
@login_required
def admin(request):
    user_ = User.objects.get(username=request.user.username)
    user = Profile.objects.get(user_id=user_.id)
    user.taging_count = 0
    user.save()

    return HttpResponseRedirect("/home")

@login_required
def admin_derestrict(request):
    user_ = User.objects.get(username=request.user.username)
    user = Profile.objects.get(user_id=user_.id)
    user.taging_count = 1
    user.save()

    return HttpResponseRedirect("/home")

@login_required
def admin_all_document(request):
    taging_data_list = TagingData.objects.all().order_by('-taging_Data_modified')
    taging_data_dict = {}
    for taging_data in taging_data_list:
        tl=TagingList.objects.get(pk=taging_data.taging_list_id).taging_list_title
        taging_data_dict[taging_data.taging_list_id]=tl

    return render(request, 'brat/AllDocument.html', {'taging_data_list': taging_data_list, 'taging_data_dict': taging_data_dict})

@login_required
def admin_month_rate(request):
    USER = {}
    user_ = User.objects.all().order_by('-last_login')
    for user__ in user_:
        user = Profile.objects.get(user_id=user__.id)
        USER[user__] = user.document_taging_count

    return render(request, 'brat/UserRate.html', {'user': user_, 'USER': USER})

def temp(request):
    filelist = os.listdir("C:/Users/user/Desktop/ann파일/chem")
    txtfilelist = []
    for file in filelist:
        if file[-3:] == "txt":
            txtfilelist.append(file)
    print(txtfilelist)

    taging_list_title = "chemistry"

    for txtfile in txtfilelist[:]:
        with open("C:/Users/user/Desktop/ann파일/chem/"+txtfile, 'r', encoding="utf-8") as f:
            all_text = f.read().split("\n")
            detail = ""
            for text_with_point in all_text[2:]:
                # 빈 문자열이면 다음차례로
                if text_with_point == "":
                    continue
                # 앞에 태깅했던게 있으면 지워주고~
                for tag in TAG:
                    if text_with_point.find(tag + "\t") > -1:
                        text_with_point = text_with_point.replace(tag + "\t", "")
                # 맨 뒤에 .으로 끝나면 지워주고~
                if text_with_point[-2:] == ". ":
                    text_with_point = text_with_point[:-2]
                if text_with_point[-1:] == ".":
                    text_with_point = text_with_point[:-1]
                # .을 기준으로 텍스트 분리
                for text_without_tag in text_with_point.split(". "):
                    detail += text_without_tag+". \n"

            taging_data = TagingData.objects.create(
                taging_data_title=all_text[0],
                taging_data_detail=detail,
                taging_data_ann="",
                taging_list=TagingList.objects.get(taging_list_title=taging_list_title))
            taging_data.save()
            makeratemodel(taging_list_title, taging_data.id)

    return HttpResponseRedirect("/home")

def all_delete():
    all_delete_data_and_datarate = TagingData.objects.all()
    all_delete_data_and_datarate.delete()
