import os,uuid

def handle_User_file(f,exten):
    st = str(uuid.uuid4())
    with open('media/User/'+st+"."+exten,'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            viewPath = '/User/'+st+"."+exten
        return viewPath
def extention(file):
    txt = file.name
    ext = txt.split(".")
    exten = ((ext[-1]).strip()).lower()
    return exten





