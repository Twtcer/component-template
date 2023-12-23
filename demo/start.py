import streamlit as st
from audio_recorder_streamlit import audio_recorder 
from iat_ws_python3 import Ws_Param,on_error
import websocket
import ssl
import base64
import json
import _thread as thread  
import time 
import uuid
from io import BytesIO
from base64 import b64decode
from pydub import AudioSegment
import numpy as np 
# from audiorecorder import audiorecorder 

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识
# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args): 
        frameSize = 8000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(wsParam.AudioFile, "rb") as fp: 
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "lame"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "lame"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "lame"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())

# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            print(result) 
            st.text(result)
            #json.dumps(data, ensure_ascii=False)
    except Exception as e: 
        print("receive msg,but parse exception:", e)

def on_close(a):
    print(f"### closed ###, file: {a}")
    #TODO: dele pcm file 
    # os.remove(rf'{a}')

audio_bytes = audio_recorder(text= "点击录音",icon_size="2x",sample_rate=16_000) #关键：设置采样率
if audio_bytes:
    # save audio file 
    audio = AudioSegment.from_file(BytesIO(audio_bytes))
    path = './wave/'+str(uuid.uuid4()).replace('-','')
    fileName = path+'.mp3'
    audio.export(fileName, format="mp3")
  
    # audio1 = AudioSegment.from_file(fileName, format="mp3")
    # audio1.set_channels(1)
    # audio1.set_frame_rate(16000)   
    # audio1.export(pcmfile, format="s16le", codec="pcm_s16le") 

    st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.sample_width}, Duration: {audio.channels}") 
    
    wsParam = Ws_Param(APPID='6e3a6d53', APISecret='MWYxNDVhYmRkYWE1YjlkZjY4NmQ0ZDUw',
                       APIKey='dd6bb38626618a489b59c600d66d3495',
                       AudioFile = fileName )
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error)
    ws.on_open = on_open
    ws.on_close= on_close(fileName)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  