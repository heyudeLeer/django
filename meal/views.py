# -*- coding: utf-8 -*-

#from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
import os
import shutil
from pathlib2 import Path
import time
from threading import Timer
from time import sleep
import zipfile
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context
from form import UploadFileForm

'''
    train_data_set(data_set_path='/home/heyude/temp',out_path='/home/heyude/PycharmProjects/mysite/meal/img_rec_out/')

  ret = predict_img(lib_name='temp',image_url='/home/heyude/temp/seg/qs-fqjd-mf2.jpg',out_path='/home/heyude/PycharmProjects/mysite/meal/img_rec_out/')
'''
import keras
import sys
sys.path.append('/home/heyude/PycharmProjects/meal-recognize')
print sys.path
import img_rec
ABS_PATH = "/home/heyude/PycharmProjects/mysite/meal/restaurant/"


lib_name = None
LIB_PATH = None
model_info = None

def home(request):
    keras.backend.tensorflow_backend.clear_session()
    return render(request, 'home.html')

def reset_django():
    os.system("touch meal/urls.py")
    pass

    return

def start_train(request):

    global model_info

    unzip_dir(LIB_PATH+'/'+lib_name+'.zip',LIB_PATH)  # /unzip train_data_set,and split to train/validation
    temp_path = LIB_PATH
    print 'temp path '+temp_path
    os.system("cp /home/heyude/PycharmProjects/mysite/split.sh %s " % temp_path)
    temp_path2 = temp_path +'/' +  lib_name
    print 'temp path2 ' +temp_path2
    os.system("cd %s; ./split.sh %s 0.5" % (temp_path,temp_path2) )
    if model_info is not None:
        model_info = None
        reset_django()
        HttpResponse('restart django to free GPU source,please wait 4s...')
        sleep(4)

    HttpResponse('start train....')
    model_info = img_rec.train_data_set(data_set_path=LIB_PATH)
    print(model_info.name)

    return render(request, 'upload_img.html')


def start_predict(request):
    global lib_name
    global model_info
    #print model_info.name
    print 'start predict...'

    # lib_name = 'heliwu'  ### default
    lib_name = request.POST['lib_name']
    model_name = None
    if model_info is not  None:
        model_name = model_info.name.strip('/').split('/')[-1]
    print 'lib_name is ' + lib_name
    print 'model name is'
    print  model_name

    if lib_name == model_name :
        print 'hot predict'
        data_set_path = ABS_PATH + request.POST['lib_name']
        image_file_path = request.POST['image_file_path']
        print model_info.model
        ret = img_rec.hot_predict_img(data_set_path=data_set_path, image_url=image_file_path, predicInfo=model_info)

    else:
        print 'cold predict'
        if model_info is not None:
            model_info = None
            Timer(1, reset_django).start()
            # sleep(1, reset_django())
            return HttpResponse('restart django to free GPU source,please wait 4s...')

        HttpResponse('cold start,please wait ...')
        data_set_path = ABS_PATH + request.POST['lib_name']
        image_file_path = request.POST['image_file_path']
        print("data_set_path: %s" % data_set_path)
        print('image_file_path: %s' % image_file_path)
        ret, predInfo = img_rec.cold_predict_img(data_set_path=data_set_path,
                                                 #image_url='/home/heyude/temp/seg/qs-fqjd-mf2.jpg'
                                                 image_url=image_file_path)
        model_info = predInfo

    if ret is not None:
        print(ret)
        pixel_file_path = data_set_path + '/' + os.path.basename(image_file_path) + 'rgb.jpg'
        print('current path: %s' % os.path.curdir)
        shutil.copyfile(pixel_file_path, './meal/static/rgb_pixel.jpg')
        return render(request, 'predict_success.html', {'result': ret})
    else:
        return HttpResponse("predict err back...")


def upload_zip(request):
    global lib_name
    global LIB_PATH
    # 请求方法为POST时,进行处理;
    if request.method == "POST":
        # 获取上传的文件,如果没有文件,则默认为None;
        print 'in post...'
        File = request.FILES.get("myfile", None)
        if File is None:
            return HttpResponse("no files for upload!")
        else:
            # 打开特定的文件进行二进制的写操作;
            lib_name,_ = os.path.splitext(File.name)
            LIB_PATH = ABS_PATH + lib_name
            print 'the LIB_PATH is ' + LIB_PATH
            if os.path.exists(LIB_PATH):
                time_info = time.strftime('%m_%d_%H_%M', time.localtime(time.time()))
                print time_info
                print
                os.rename(LIB_PATH + '/' + lib_name + '.h5', LIB_PATH + '/' + lib_name + time_info + '.h5')
                os.rename(LIB_PATH,LIB_PATH+time_info)
            os.makedirs(LIB_PATH)

            with open(LIB_PATH + "/%s" % File.name, 'wb+') as f:
                # 分块写入文件;
                for chunk in File.chunks():
                    f.write(chunk)
                return render(request, 'upload_zip_success.html')
    else:
        print 'in get...'
        return render(request, 'upload_zip.html')


def upload_img(request):
    # 请求方法为POST时,进行处理;
    if request.method == "POST":
        # 获取上传的文件,如果没有文件,则默认为None;
        print 'in post...'
        File = request.FILES.get("myfile", None)
        if File is None:
            return HttpResponse("no files for upload!")
        else:
            LIB_PATH = ABS_PATH + 'heliwu'
            # 读出所有 lib name 列表
            lib_path = Path(ABS_PATH)
            lib_names = []
            for lib in lib_path.iterdir():
                lib_names.append(lib.name)
            # 打开特定的文件进行二进制的写操作;
            image_file_path = LIB_PATH + "/%s" % File.name
            with open(image_file_path, 'wb+') as f:
                # 分块写入文件;
                for chunk in File.chunks():
                    f.write(chunk)
                return render(request, 'predict.html', context={"lib_names": lib_names, 'image_file_path': image_file_path})
    else:
        print 'in get...'
        return render(request, 'upload_img.html')


def unzip_dir(srcname,dstPath):
    print srcname
    print srcname
    print srcname
    print
    print zipfile.is_zipfile(srcname)
    print
    zipHandle=zipfile.ZipFile(srcname,'r')
    zipHandle.extractall(dstPath) #解压到指定目录
    zipHandle.close()




