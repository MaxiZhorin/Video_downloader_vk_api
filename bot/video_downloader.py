# -*- coding: utf8 -*-
import vk
from bs4 import BeautifulSoup
import os
import requests
import datetime
import random
from tqdm import tqdm

ots = '\n__________________________________________________'


def new_title():
    global video_name, random_titles
    new_title = str( video_name )

    for i in random_titles:
        new_title = new_title + str( ' ' + random.choice( i ) )
    return new_title


def video_editor(file_name):
    psw = ''
    for x in range( 12 ):
        psw = psw + random.choice( list( '123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM' ) )
    file_name_new = psw + '.mp4'
    os.system( 'ffmpeg -i ' + file_name + ' -vf "transpose=3,transpose=2" -c:a copy output.mp4 -y' )
    os.system( 'rm ' + file_name )
    os.system(
        "ffmpeg -i output.mp4 -i logo.png -filter_complex 'overlay=(main_w-overlay_w)/2:main_h-overlay_h-10' " + str(
            file_name_new ) + " -y" )
    # water
    os.system( 'rm output.mp4' )
    return file_name_new


def download(url, title, orig_title):
    print(url)
    new_url = str( url.split( '?' )[0] )
    r = requests.get( new_url, stream=True )
    if float( dict( r.__dict__ ).get( 'headers', 'Content-Length' )['Content-Length'] ) / 1048576 > float( 700 ):
        return print( '$$$ Больше 700мб' )
    else:
        new_tit = new_title()
        file_name = str( 'orig.mp4' )
        print( file_name, r )
        with open( file_name, 'wb' ) as file:
            for chunk in tqdm( r.iter_content( 1024000 ) ):
                file.write( chunk )
        print( 'Video downloaded', file_name, ots )
        file_name = video_editor( file_name )
        upload( file_name, new_tit, 181663673, orig_title )


def upload(file_name, title, owner, orig_title):
    video = vk_api.video.get( owner_id=('-' + str( owner )) )
    video_wall = 0
    video_wall_iter = 0
    # Проверка на 50 записей в день
    for video in video.get( 'items' ):
        time_stamp = datetime.datetime.date( datetime.datetime.fromtimestamp( int( video['adding_date'] ) ) )
        data = datetime.datetime.date( datetime.datetime.today() )
        if time_stamp == data:
            video_wall_iter += 1
    print( 'Today wallpost video: ', video_wall_iter )
    if video_wall_iter < 10:
        video_wall = 0

    video = vk_api.video.save( name=title, description=arbitrade, group_id=owner, wallpost=video_wall )
    data = {
        'access_key': video['access_key']
    }
    files = {
        'file': open( file_name, 'rb' )
    }
    req = requests.post( video['upload_url'], data=data, files=files )
    print( req.text )
    print( '\nVideo uploaded', title, ots )
    try:
        with open( "wall_downloaded.txt", 'a' ) as file_wall:
            file_wall.writelines( orig_title + '\n' )
    except IOError:
        print( "An IOError has occurred!" )
    path = os.path.join( os.path.abspath( os.path.dirname( __file__ ) ), file_name )
    os.remove( path )


def get_titles_from_user(owner_id, title, video_url, orig_title):
    video_titles = vk_api.video.get( owner_id=owner_id )
    title = title.upper()
    ne_ravno = True
    if title.count( '"' ) or title.count( "'" ) or title.count( "\u005C" ):
        title = title.replace( '"', '' )
        title = title.replace( "'", '' )
        title = title.replace( "\u005C", '' )
        title = title.replace( "\u002F", '' )

    for titles in video_titles.get( 'items' ):
        titles_url = str( titles['title'] ).upper()
        if titles_url.count('"' ) or titles_url.count( "'" ) or title.count( "\u005C" ):
            titles_url = titles_url.replace( '"', '' )
            titles_url = titles_url.replace( "'", '' )
            titles_url = titles_url.replace( "v", '' )
            title = title.replace( "\u002F", '' )

        if titles_url == title:
            print( '---ravno---', titles_url, title, ots )
            ne_ravno = False
            break
        else:
            pass

    if ne_ravno:
        print( ('---ne ravno---', title, ots) )
        download( video_url, title, orig_title )
    else:
        print( ('---ravno---', title, ots) )


def get_videos_vk(search, ofset=1):
    list_videos = vk_api.video.search( q=search, sort=2, hd=1, adult=0, filters='mp4,short', count=200, offset=ofset )
    for link in list_videos.get( 'items' ):
        false_flag = True
        video_link = str( 'https://m.vk.com/video' + str( link['owner_id'] ) + '_' + str( link['id'] ) )
        print( '***Нашел видео', link['title'], ots )
        with open( "wall.txt", 'r' ) as file_wall:
            for title in file_wall:
                if str( title.upper() )[:-1] == str( link['title'] ).upper():
                    print( '###Выхожу из цикла,совпадение wall', ots )  # Если такое видео уже было скачано выходим из цикла
                    false_flag = False

        with open( "wall_downoaded.txt", 'r' ) as file_wall:
            for title in file_wall:
                if str( title.upper() )[:-1] == str( link['title'] ).upper():
                    print( '###Выхожу из цикла,совпадение wall_downloaded', title, ots )
                    false_flag = False
        if false_flag:
            get_url_vk( video_link, link['title'] )
            print( video_link )
        else:
            pass


def get_url_vk(url, orig_title):
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"}
    html = session.auth_session.get( url, headers=headers ).text
    soup = BeautifulSoup( html, 'html.parser' )
    if soup.find( 'title' ):
        print(soup)
        video_url = soup.text.split( 'ajax.preload' )[1]
        title = soup.text.split( 'id=\u005C"mv_title\u005C">' )[1]
        title = title.split( '<' )[0]
        print( title )
        if video_url.count( 'url720' ):
            video_url = video_url.split( 'url720":"' )[1]
            video_url = video_url.split( '?' )[0]
            video_url = video_url.replace( u"\u005C", '' )
        elif video_url.count( 'url480' ):
            video_url = video_url.split( 'url480":"' )[1]
            video_url = video_url.split( '?' )[0]
            video_url = video_url.replace( u"\u005C", '' )
        else:
            return False
        print(video_url)
        get_titles_from_user( str(id_group), title, video_url, orig_title )

        print( '*** URL video original', video_url, ots )


if __name__ == '__main__':

    id_bot = '6982959'  # id приложения вк
    login_vk = '79272140414'  # логин вк
    password_vk = 'Sz1620151'  # пароль вк
    session = vk.AuthSession(id_bot, login_vk, password_vk, scope='video,wall,groups,offline' )
    vk_api = vk.API( session, v='5.95', lang='ru', timeout=10 )

    arbitrade = """
    Рекламаная запись в описании видео
    """
    video_name = ''

    random_titles = [['здесь', 'набор', 'ключевых', 'слов', 'для', 'названия', 'вашего'],
                     ['видео', '####', '####', '####', '####'],
                     ]

    id_group = "-189062591"  # id группы вк куда будет производиться залив видео
    ofset = 0
    i = 1
    range_set = 2  # каждая единица дает список 100 видео
    find = 'видео бомба'  # ключевое слово для поиска видео
    for i in range( 2 ):
        get_videos_vk(str(find), ofset )
        print(ofset)
        ofset += 100
