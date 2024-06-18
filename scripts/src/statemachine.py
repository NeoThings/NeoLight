import os
import sys
import cv2
import time
import psutil
import argparse
import configparser
from multiprocessing import Process
from transitions import Machine
from httpclient import httpClient
from playaudio import playaudio
from gtts import gTTS

from cvmodule.cvinterface import CVInterface


config = configparser.ConfigParser()
config.read('../config/wled.cfg')

http_client = httpClient()
wled_addr = "http://192.168.100.128/json"

class StateMachine(object):
    def get_process_pid(self, process_name):
        for proc in psutil.process_iter():
            try:
                if proc.name() == process_name:
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return None
    
    def terminate_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait()
            return True
        except psutil.NoSuchProcess:
            return False

    # def play_audio(self):
    #     audio_path = self.audio_path
    #     playaudio(audio_path)
    
    def play_audio_sun(self):
        playaudio("../audios/stardustalarmclock.mp3")

    def get_current_hour():
        current_time = time.time()
        current_hour = time.localtime(current_time).tm_hour
        return current_hour
    
    def go_to_sleep(self):
        if http_client.get_wled_json()['on']:
            print('true')
            data = config.get('effect', 'sleep')
            http_client.post_wled_json(wled_addr, data)
        else:
            pass

    def http_send_night_light(self):
        if http_client.get_wled_json()['on']:
            pass
        else:
            data = config.get('effect', 'night_light')
            http_client.post_wled_json(wled_addr, data)
    
    def http_send_music(self):
        data = config.get('effect', 'music')
        http_client.post_wled_json(wled_addr, data)

    def http_send_rain(self):
        data = config.get('effect', 'rain')
        http_client.post_wled_json(wled_addr, data)
        if os.path.exists("../audios/softrainambient.mp3"):
            playaudio("../audios/softrainambient.mp3")
            # self.audio_path = "../audios/softrainambient.mp3"
            # self.p.start()
        else:
            print("path did not exist")
    
    def http_send_sun(self):
        data = config.get('effect', 'sun')
        http_client.post_wled_json(wled_addr, data)
        if os.path.exists("../audios/stardustalarmclock.mp3"):
            playaudio("../audios/stardustalarmclock.mp3")
            # self.audio_path = "../audios/stardustalarmclock.mp3"
            # self.p.start()
        else:
            print("path did not exist")
    
    def http_send_standby(self):
        playaudio_pid = self.get_process_pid("mpv")
        if playaudio_pid:
            self.terminate_process(playaudio_pid)
        else:
            pass
        data = config.get('effect', 'standby')
        http_client.post_wled_json(wled_addr, data)

    def http_send_ding(self):
        data = config.get('effect', 'ding')
        http_client.post_wled_json(wled_addr, data)
        playaudio("../audios/ding00.mp3")
    
    def http_send_warning(self):
        data = config.get('effect', 'warning')
        http_client.post_wled_json(wled_addr, data)
        playaudio("../audios/tribedrum.mp3")

    def at_day(self):
        current_time = StateMachine.get_current_hour()
        if current_time > 7 and current_time < 24:
            return True
        else:
            print("It's not daytime now")
            return False
        
    def at_night(self):
        current_time = StateMachine.get_current_hour()
        if current_time < 7 or current_time > 24:
            return True
        else:
            print("It's not night now")
            return False
    
    def rainy_day(self):
        # implement face detector

        weather_info = http_client.get_weather()
        weather = weather_info["weather"][0]["main"]
        self.temperature = weather_info["main"]["temp"]

        print("current weather is: " + weather)
        if weather == "Rain":
            return True
        else:
            return False
    
    def sunny_day(self):
        weather_info = http_client.get_weather()
        weather = weather_info["weather"][0]["main"]
        self.temperature = weather_info["main"]["temp"]

        print("current weather is: " + weather)
        if weather == "Sun":
            return True
        else:
            return False
    
    def broadcast_temperature(self):
        # self.p.terminate()
        playaudio_pid = self.get_process_pid("mpv")
        if playaudio_pid:
            self.terminate_process(playaudio_pid)
        else:
            pass
        cast_text = "今日温度： " + str(round((self.temperature - 273.15), 0))
        language = 'zh-CN'
        speech = gTTS(text=cast_text, lang=language, slow=False)
        speech.save("../audios/temperature.mp3")
        playaudio("../audios/temperature.mp3")
        
    states = ['standby', 'sleep', 'night_light', 'weather', 'music', 'warning', 'cast_weather', 'cast_done', 'ding']

    transitions = [
        ['camera_detect_human', 'standby', 'warning']
    ]

    def __init__(self, name):
        self.name = name
        # self.audio_path = None
        # self.p = Process(target=self.play_audio)
        # self.machine = Machine(model=self, states=StateMachine.states,
        #                        transitions=StateMachine.transitions, initial='standby')
        
        self.machine = Machine(model=self, states=StateMachine.states, initial='standby', ignore_invalid_triggers=True)

        self.machine.add_transition('good_night', 'standby', 'sleep',
                                    conditions='at_night', after='go_to_sleep')
        
        self.machine.add_transition('night_light_on', 'sleep', 'night_light',
                                    conditions='at_night', after='http_send_night_light')
        
        self.machine.add_transition('night_light_off', 'night_light', 'sleep',
                                    conditions='at_night', after='go_to_sleep')
        
        self.machine.add_transition('good_morning', 'sleep', 'weather',
                                    conditions='rainy_day', after='http_send_rain')
        
        self.machine.add_transition('good_morning', 'sleep', 'weather',
                                    conditions='sunny_day', after='http_send_sun')
        
        self.machine.add_transition('broadcast', 'weather', 'cast_weather', after='broadcast_temperature')
        
        self.machine.add_transition('take_a_break', '*', 'standby', after='http_send_standby')

        self.machine.add_transition('start_play', 'standby', 'music', after='http_send_music')

        self.machine.add_transition('stop_play', 'music', 'standby', after='http_send_standby')

        self.machine.add_transition('water_overflow', '*', 'warning', after='http_send_warning')

        self.machine.add_transition('someone_outside', 'standby', 'ding', after='http_send_ding')