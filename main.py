# Importing all the required libraries
import os
import pytube
from customtkinter import *
import customtkinter
from tkinter import *
from PIL import Image
from pygame import mixer
from time import strftime, gmtime
from mutagen.mp3 import MP3  # Pydub sucks (no offense to its creators)
from random import shuffle
from tkinter import filedialog
import shutil
from moviepy.editor import *
import json

# Creating main window
root = CTk()
customtkinter.set_appearance_mode('dark')
root.title('MP3 Player')
root.geometry('340x405')

# Top Level Variables
selected_playlist = ""
pause = True
mixer.init()
song_playing = False
song_duration = 0
time_elapsed = 0
forward, backward = False,False
dir = "...\\MP3 Player\\Songs"
char_pos = 0
song_name = ""
songs_list = []
shuffle_songs = False
rough_name = ""
prev_time = 0
loop = False
looped_song = ""
# Functions
def init_song(path_to_song):
    global char_pos
    global song_duration
    global time_elapsed
    global dir
    global song_name
    time_elapsed = 0
    song_name = os.path.splitext(os.path.basename(path_to_song))[0]
    song_name_lbl.configure(text=song_name)
    time_elapsed_lbl.configure(text='00:00')
    audio = MP3(path_to_song)
    song_duration = audio.info.length
    time_remaining_lbl.configure(text=strftime('%M:%S',gmtime(song_duration)))
    song_slider.configure(number_of_steps=song_duration,to=song_duration*2)
    timeline()
    char_pos=0
    animate_song_name()

def animate_song_name():
    global song_name
    global char_pos
    global rough_name
    rough_name = "      " + song_name
    if len(song_name) > 30:
        char_pos = char_pos + 1
        if char_pos == len(song_name) or len(song_name)-char_pos == 1:
            char_pos = 0
        rough_name = rough_name[char_pos:]
        song_name_lbl.configure(text=rough_name)
    root.after(450,animate_song_name)

def add_song_from_dialogue():
    global sys_entry
    new_song_path = filedialog.askopenfile(filetypes=[('MP3 Files','.mp3')])
    sys_entry.delete(0,END)
    sys_entry.insert(0,new_song_path.name)

def install_from_link():
    global online_entry
    global dir
    # Installing from youtube
    try:
        yt = pytube.YouTube(online_entry.get())
        t=yt.streams.filter(only_audio=True)
        t[0].download(dir)
    except:
        print("Invalid Link. Try again")
        return 0
    # Converting to mp3
    files = os.listdir(dir)
    paths = [os.path.join(dir, basename) for basename in files]
    installed_song = max(paths, key=os.path.getctime)
    fileconverter = AudioFileClip(installed_song)
    fileconverter.write_audiofile(dir+"\\"+os.path.splitext(os.path.basename(installed_song))[0]+".mp3")
    fileconverter.close()
    os.remove(installed_song)
    add_song_list('start')

def play_song(path_to_song):
    global song_playing
    global pause
    global dir
    global time_elapsed
    global song_name
    global looped_song
    global loop
    if looped_song != song_name+'.mp3':
        loop=False
    
    # Check if the file exists before proceeding
    if os.path.exists(path_to_song):
        if song_playing:
            song_slider.set(0)
            time_elapsed = 0
            mixer.music.stop()
            timeline()
        else:
            song_playing = True

        mixer.music.load(path_to_song)
        mixer.music.play()
        pause = False
        for x in range(2):  # A few gimmicks
            resume_pause()
        init_song(path_to_song)
    else:
        print("File not found:", path_to_song) 

def add_songs_to_new_playlist(songname):
    global playlist_music_items
    global added_songs_frame
    playlist_music_items.append(songname)
    added_songs_frame_optimization(playlist_music_items)

def added_songs_frame_optimization(music_list):
    global added_songs_frame
    for widget in added_songs_frame.winfo_children():
        widget.destroy()
    for songitem in music_list:
        added_song_btn = CTkButton(added_songs_frame,text=os.path.splitext(songitem)[0],border_color='red',fg_color='transparent',border_width=1,text_color='red',width=100,command=lambda goofysongitem=songitem:delete_songs_from_new_playlist(goofysongitem))
        added_song_btn.pack(padx=5,pady=5)

def delete_songs_from_new_playlist(songname):
    global playlist_music_items
    global added_songs_frame
    playlist_music_items.pop(playlist_music_items.index(songname))
    added_songs_frame_optimization(playlist_music_items)

def create_new_playlist_in_json():
    global playlistname_entry123
    global data
    global playlist_music_items
    data[playlistname_entry123.get()] = playlist_music_items
    dump_json()
    optimize_playlistoptions_frame()
    # TODO Add reset listbox during code optimization

def add_new_playlist():
    global dir
    global playlist_music_items
    global added_songs_frame
    global playlistname_entry123
    # Creating main window
    playlist_music_items = []
    new_playlist_main = CTk()
    new_playlist_main.title('Create New Playlist')
    new_playlist_main.geometry('650x300')
    playlist_name_frame = CTkFrame(new_playlist_main)
    playlistname_entry123 = CTkEntry(playlist_name_frame)
    playlistname_entry_lbl = CTkLabel(playlist_name_frame,text='Enter New PlayList name: ')
    songs_frame = CTkFrame(new_playlist_main)
    songs_to_be_added_frame = CTkScrollableFrame(songs_frame,width=300)
    added_songs_frame = CTkScrollableFrame(songs_frame,width=305)
    create_new_playlist_btn = CTkButton(new_playlist_main,text='Create New PlayList',command=create_new_playlist_in_json)
    for widget in songs_to_be_added_frame.winfo_children():
        widget.destroy()
    for songs in os.listdir(dir):
        addable_songs = CTkButton(songs_to_be_added_frame,text=os.path.splitext(songs)[0],border_color='green',fg_color='transparent',border_width=1,text_color='green',width=100,command=lambda song=songs: add_songs_to_new_playlist(song))
        addable_songs.pack(padx=5,pady=5)
    playlist_name_frame.pack(padx=5)
    playlistname_entry_lbl.pack(side=LEFT,padx=5)
    playlistname_entry123.pack(side=LEFT,padx=5)
    songs_frame.pack(padx=10)
    songs_to_be_added_frame.pack(side=LEFT,pady=5,padx=5)
    added_songs_frame.pack(side=LEFT,pady=5,padx=5)
    create_new_playlist_btn.pack(padx=10)
    new_playlist_main.mainloop()

def add_song_list(when):
    global dir
    global songs_list
    for widget in frame2.winfo_children():
        widget.destroy()
    if when == 'start':
        songs_list = os.listdir(dir)
        for song_item in songs_list:           
            song = CTkButton(frame2,text=os.path.splitext(song_item)[0],width=275,fg_color='transparent',border_color='blue',border_width=1,command=lambda to_be_played=song_item:play_song(dir+"\\"+to_be_played)).pack(pady=5)
    if when == 'shuffle':
        for song_item in songs_list:           
            song = CTkButton(frame2,text=os.path.splitext(song_item)[0],width=275,fg_color='transparent',border_color='blue',border_width=1,command=lambda to_be_played=song_item:play_song(dir+"\\"+to_be_played)).pack(pady=5)

def add_song_to_dir():
    global dir
    global sys_entry
    if os.path.exists(sys_entry.get()):
        shutil.move(sys_entry.get(),dir+"\\"+os.path.basename(sys_entry))
        add_song_list('start')
    else:
        print(f"Directory {sys_entry.get()} does not exist. Check path.")

def remove_song_from_playlist(songname,playlisttobe):
    global data
    data[playlisttobe].pop(data[playlisttobe].index(songname))
    playlist_songs_list_frame_optimization(playlisttobe)
    dump_json()

def rename_playlist(playlist_to_be):
    global data
    global playlist_name_entry
    data[playlist_name_entry.get()] = data.pop(playlist_to_be)
    dump_json()
    playlist_songs(playlist_name_entry.get())
    optimize_playlistoptions_frame()

def playlist_songs(playlist_to_be):
    global songs_list
    global data
    global selected_playlist
    global playlist_songs_list_frame
    global playlist_select_edit_lbl
    global name_edit_frame
    global playlist_name_entry
    global rename_playlist_btn
    global add_song_to_playlist_btn
    global playlist_song_del_lbl
    global playlist_name_lbl
    global delete_playlist_btn
    selected_playlist = playlist_to_be
    songs_list = data[playlist_to_be]
    add_song_list('shuffle')
    try:
        playlist_select_edit_lbl.destroy()
    except:
        pass
    add_song_to_playlist_btn.configure(command=lambda:add_song_to_playlist_main(playlist_to_be))
    rename_playlist_btn.configure(command=lambda:rename_playlist(playlist_to_be))
    playlist_name_entry.delete(0,END)
    playlist_name_entry.insert(0,playlist_to_be)
    playlist_name_lbl.configure(f'PlayList Name: {playlist_to_be}')
    playlist_name_lbl.pack(pady=5)
    name_edit_frame.pack()
    playlist_name_entry.pack(side=LEFT,padx=5,pady=5)
    rename_playlist_btn.pack(side=LEFT,padx=5,pady=5)
    playlist_songs_list_frame_optimization(playlist_to_be)
    playlist_song_del_lbl.pack()
    playlist_songs_list_frame.pack()
    add_song_to_playlist_btn.pack(side=LEFT,padx=5)
    delete_playlist_btn.pack(side=LEFT,padx=5)

def playlist_songs_list_frame_optimization(playlist_to_be):
    global data
    global playlist_songs_list_frame
    for widget in playlist_songs_list_frame.winfo_children():
        widget.destroy()
    for song_names in data[playlist_to_be]:
        playlistsong_btn = CTkButton(playlist_songs_list_frame,text=os.path.splitext(song_names)[0],fg_color='transparent',border_width=1,border_color='red',text_color='red',command=lambda song=song_names: remove_song_from_playlist(song,playlist_to_be),width=150)
        playlistsong_btn.pack(pady=5,padx=5)

def add_song_playlist_goofy(playlist,songname):
    global data
    data[playlist].append(songname)
    dump_json()
    playlist_songs(playlist)

def add_song_to_playlist_main(playlist_name_goofy_ahhh):
    global dir
    # Creating the main window
    song_add_main = CTk()
    song_add_main.geometry('350x150')
    song_add_main
    # Widgets
    addsonglbl = CTkLabel(song_add_main,text='Click to add songs')
    addsongframe = CTkScrollableFrame(song_add_main)
    for song in os.listdir(dir):
        goofy_song_btn = CTkButton(addsongframe,command=lambda song1=song: add_song_playlist_goofy(playlist_name_goofy_ahhh,song1),text=os.path.splitext(song)[0],width=150,fg_color='transparent',border_color='green',border_width=1)
        goofy_song_btn.pack(pady=5,padx=5)
    addsonglbl.pack()
    addsongframe.pack()
    song_add_main.mainloop()

def delete_playlist(playlist):
    global data
    data.pop(playlist)
    dump_json()
    optimize_playlistoptions_frame()

def dump_json():
    global data
    a = open('playlist_data.json','w')
    json.dump(data,a)
    a.close()

def optimize_playlistoptions_frame():
    global data
    global playlistoptions_frame
    for widget in playlistoptions_frame.winfo_children():
        widget.destroy()
    for playlist in data.keys():
        playlistname_btn = CTkButton(playlistoptions_frame,text=playlist,width=100,command=lambda playlistname=playlist:playlist_songs(playlistname))
        playlistname_btn.pack(pady=5,padx=10)

def play_list():
    global data
    global selected_playlist
    global delete_playlist_btn
    global playlist_songs_list_frame
    global playlist_select_edit_lbl
    global name_edit_frame
    global playlist_name_entry
    global playlistoptions_frame
    global rename_playlist_btn
    global add_song_to_playlist_btn
    global playlist_song_del_lbl
    global playlist_name_lbl
    data_file = open('playlist_data.json')
    data = json.load(data_file)
    # Creating the main window
    playlist_main = CTk()
    playlist_main.title('Playlists')
    playlist_main.geometry('400x400')
    # Widgets
    tabview_playlist = CTkTabview(playlist_main,width=300)
    tabview_playlist.add('Select')
    tabview_playlist.add('Edit')
    delete_playlist_btn = CTkButton(tabview_playlist.tab('Edit'),text='Delete Playlist -',fg_color='transparent',border_color='red',text_color='red',border_width=1)
    playlist_select_lbl = CTkLabel(tabview_playlist.tab('Select'),text='Select a Play List: ')
    playlist_select_edit_lbl = CTkLabel(tabview_playlist.tab('Edit'),text='Select A playlist to edit')
    name_edit_frame = CTkFrame(tabview_playlist.tab('Edit'))
    add_playlist_btn = CTkButton(tabview_playlist.tab('Select'),text='Add A PlayList +',border_color='blue',border_width=1,fg_color='transparent',text_color='blue',command=add_new_playlist)
    playlist_name_entry = CTkEntry(name_edit_frame,width=300)
    rename_playlist_btn = CTkButton(name_edit_frame,text='Rename')
    playlist_song_del_lbl = CTkLabel(tabview_playlist.tab('Edit'),text='Songs || Click to remove songs from playlist')
    playlist_songs_list_frame = CTkScrollableFrame(tabview_playlist.tab('Edit'),width=400)
    add_song_to_playlist_btn = CTkButton(tabview_playlist.tab('Edit'),text='Add a song +',fg_color='transparent',border_color='blue',text_color='blue',border_width=1)
    playlistoptions_frame = CTkScrollableFrame(tabview_playlist.tab('Select'),height=260,width=400)
    playlist_name_lbl = CTkLabel(tabview_playlist.tab('Edit'),text='PlayList Name:')
    for playlist in data.keys():
        playlistname_btn = CTkButton(playlistoptions_frame,text=playlist,width=100,command=lambda playlistname=playlist:playlist_songs(playlistname))
        playlistname_btn.pack(pady=5,padx=10)
    tabview_playlist.pack()
    playlist_select_lbl.pack()
    playlistoptions_frame.pack(pady=10)
    add_playlist_btn.pack()
    data_file.close()
    if selected_playlist == '':
        playlist_select_edit_lbl.pack()
    playlist_main.mainloop()

def install_song():
    global sys_entry
    global online_entry
    # Creating the main window
    install_win = CTk()
    install_win.title('Install Songs')
    install_win.geometry('600x90')
    # Widgets
    # Tabs
    tabview = CTkTabview(install_win,width=100)
    tabview.add('System')
    tabview.add('Online Link')
    # System Tab Widgets
    sys_entry = CTkEntry(tabview.tab('System'),width=300,border_color='blue',border_width=1,fg_color='transparent')
    search_sys_gui_btn = CTkButton(tabview.tab('System'),command=add_song_from_dialogue,text='File Explorer')
    find_file_btn = CTkButton(tabview.tab('System'),width=20,text="Add Song",command=add_song_to_dir)
    # Online Link Widgets
    framex = CTkFrame(tabview.tab('Online Link'))
    framey = CTkFrame(tabview.tab('Online Link'))
    online_entry = CTkEntry(framex,width=300,border_color='blue',border_width=1,fg_color='transparent')
    install_yt_vid_btn = CTkButton(framex,text="Install From Youtube",command=install_from_link)
    online_link_info_lbl = CTkLabel(framey,text='Enter Youtube link of the song you want to install',text_color='blue')
    # Packing
    # Tab
    tabview.pack()
    tabview.tab('System').grid(padx=(15,15))
    tabview.tab('Online Link').grid(padx=(15,15))
    tabview.set('System')
    # System Tab
    search_sys_gui_btn.pack(side=LEFT,padx=10)
    sys_entry.pack(side=LEFT,padx=10)
    find_file_btn.pack(side=LEFT,padx=10)
    # Online Link
    framex.pack()
    framey.pack()
    online_entry.pack(side=LEFT,padx=10)
    install_yt_vid_btn.pack(side=LEFT)
    online_link_info_lbl.pack(side=BOTTOM,pady=20)
    install_win.mainloop()
    
def timeline():
    global song_duration
    global time_elapsed
    global pause
    global prev_time
    global forward
    global backward
    if song_slider.get() == song_duration*2 and not pause:
        next_prev_song('next')
    if time_elapsed-song_slider.get() > 8 or time_elapsed-song_slider.get() < 0:   
        try:    
            mixer.music.set_pos(song_slider.get()/2)
        except:
            pass
        time_elapsed = song_slider.get()
        song_slider.set(song_slider.get())
    if forward:
        time_elapsed += 8
        forward = False
        mixer.music.set_pos(time_elapsed/2)
        song_slider.set(time_elapsed)
    if backward:
        time_elapsed -= 12
        if time_elapsed < 0:
            time_elapsed = 0           
        backward = False
        mixer.music.set_pos(song_slider.get()/2)
        song_slider.set(time_elapsed)
    if not pause:    
        if (int(strftime('%S',gmtime())) - prev_time) == 1:
            song_slider.set(time_elapsed)
            time_elapsed += 2
            time_elapsed_lbl.configure(text=strftime('%M:%S',gmtime(time_elapsed/2))) # Python is speeeeeed 
        prev_time = int(strftime('%S',gmtime()))
    root.after(1000,timeline,) # One second timer not applicable for 'time_elapsed += 1'

def resume_pause():
    global pause   
    if pause:
        resume_pause_song_btn.configure(image=resume_pause_song_but_its_pause)
        mixer.music.unpause()
        pause=False
    elif not pause:
        resume_pause_song_btn.configure(image=resume_pause_song)
        mixer.music.pause()
        pause = True

def forward_behind(direction):
    global backward, forward
    if direction == "ahead":
        forward = True
        backward = False
    else:
        forward = False
        backward = True
    timeline()

def next_prev_song(next_prev):
    global songs_list
    global song_name
    global dir
    global loop
    global looped_song
    raw_song_name = song_name + '.mp3'
    if loop and song_name+".mp3" == looped_song:
        play_song(dir + "\\"+looped_song)
        return 0
    try:
        song_index = songs_list.index(raw_song_name)
    except:
        song_index=-1

    if next_prev == 'next':
        try:
            play_song(dir + "\\"+ str(songs_list[song_index+1]))
        except:
            song_index = 0
            play_song(dir + "\\"+ str(songs_list[song_index]))
    else:
        try:
            play_song(dir + "\\"+ str(songs_list[song_index-1]))
        except:
            song_index = len(songs_list)
            play_song(dir + "\\"+ str(songs_list[song_index]))

def shuffle_songs():
    global songs_list
    shuffle(songs_list)
    add_song_list('shuffle')

def loop_song():
    global song_name    
    global looped_song
    global loop
    looped_song = song_name + '.mp3'
    if loop:
        loop=False
        root.title('MP3 Player')
    else:
        loop=True
        root.title('MP3 Player (On Loop)')
# Widgets
# Menu
"""
Date: 25/03/24
At the time of writing, menubars do not exist in this module for some reason.
Need to make own menu bar
"""
frame1 = CTkFrame(root,width=200)
shuffle_btn = CTkButton(frame1,text='Shuffle',width=10,command=shuffle_songs)
install_btn = CTkButton(frame1,text='Install',width=10,command=install_song)
playlist_btn = CTkButton(frame1,text='Playlist',width=10,command=play_list)

#Songs List
"""
Date: 26/03/24
At the time of writing, list boxes do not exist in this module for some reason.
Need to make own list box.
"""
frame2 = CTkScrollableFrame(root,width=375,height=250)

#Song info
frame3 = CTkFrame(root,width=50)
song_name_frame = CTkFrame(frame3,width=50)
song_name_lbl = CTkLabel(frame3,font=('aerial',20),text_color='white',text=song_name)
song_slider = CTkSlider(frame3)
song_slider.set(0)
time_elapsed_lbl = CTkLabel(frame3,text="00:00")
time_remaining_lbl = CTkLabel(frame3,text="00:00")
loop_img = CTkImage(Image.open('loop.png'),size=(30,30))
loop_btn = CTkButton(frame3,image=loop_img,fg_color='transparent',text='',width=30,command=loop_song)

# Song Controls
frame4 = CTkFrame(root)
prev_song = CTkImage(Image.open('prev song.png'),size=(30,30))
prev_song_btn = CTkButton(frame4,image=prev_song,fg_color='transparent',text='',width=30,command=lambda:next_prev_song('goofy ahhhh'))
behind_song = CTkImage(Image.open('behind.png'),size=(30,30))
behind_song_btn = CTkButton(frame4,image=behind_song,fg_color='transparent',text='',width=30,command=lambda:forward_behind('behind'))
resume_pause_song = CTkImage(Image.open('resum.png'),size=(30,30))
resume_pause_song_but_its_pause = CTkImage(Image.open('pause_btn.png'),size=(30,30))
resume_pause_song_btn = CTkButton(frame4,image=resume_pause_song_but_its_pause,fg_color='transparent',text='',width=30,command=resume_pause)
ahead_song = CTkImage(Image.open('ahead.png'),size=(30,30))
ahead_song_btn = CTkButton(frame4,image=ahead_song,fg_color='transparent',text='',width=30,command=lambda:forward_behind('ahead'))
nxt_song = CTkImage(Image.open('next_song.png'),size=(30,30))
nxt_song_btn = CTkButton(frame4,image=nxt_song,fg_color='transparent',text='',width=30,command=lambda:next_prev_song('next'))
# Packing
# Menu Widgets
frame1.pack(padx=15)
shuffle_btn.pack(side=LEFT,padx=22,pady=2)
install_btn.pack(side=LEFT,padx=22,pady=2)
playlist_btn.pack(side=LEFT,padx=22,pady=2)
# delete_song_btn.pack(side=LEFT,padx=13)

# Songs list widgets
frame2.pack(anchor='w')

# Songs info widgets
frame3.pack()
song_name_lbl.pack(pady=3)
time_elapsed_lbl.pack(side=LEFT,padx=5)
song_slider.pack(side=LEFT,padx=5)
time_remaining_lbl.pack(side=LEFT,padx=5)
loop_btn.pack(side=LEFT,padx=3)

# Song control widgets
frame4.pack()
prev_song_btn.pack(side=LEFT,padx=7)
behind_song_btn.pack(side=LEFT,padx=6)
resume_pause_song_btn.pack(side=LEFT,padx=6)
ahead_song_btn.pack(side=LEFT,padx=6)
nxt_song_btn.pack(side=LEFT,padx=7)

# Function execution
add_song_list('start')
timeline()
root.mainloop()