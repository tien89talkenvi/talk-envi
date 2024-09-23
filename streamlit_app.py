import streamlit as st
import streamlit.components.v1 as components 
from pytube import YouTube, extract
from streamlit_input_box import input_box
from subprocess import run
import yt_dlp
import os
from faster_whisper import WhisperModel
import tempfile
import requests

st.set_page_config(page_title="Speak Youtube Subtitles", layout="wide")
st.markdown(" <style> div[class^='block-container'] { padding-top: 1.8rem;} ", unsafe_allow_html=True)
#----------------------------------------------------------------------------------------------------------
#@st.cache_data
#def ydl_download_audio(url_yt):
#    #'https://www.youtube.com/watch?v=BaW_jenozKc' url ua 1 tep audio rat ngan
#    lenh = 'yt-dlp --extract-audio --audio-format wav --audio-quality 0 -o audioyt.%(ext)s --yes-overwrites '+url_yt
#    l_lenh=lenh.split(' ')
#    run(l_lenh) # cai nay de ra tep audioyt.m4a 
#    return "audioyt.wav"

def download_yt_audio(url_yt,filename):
    # filename thuc ra la pathfilename thay doi moi khi me no truyen vao
    ydl_opts = {
        "format" : 'bestaudio/best',
        "outtmpl": filename,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url_yt)    # kq la tep .webm
    return filename    

def Lay_id_tde_tluong(url_yt):
    try:
        videoID = extract.video_id(url_yt)
        tieude = YouTube(url_yt).title
        tluong = YouTube(url_yt).length
        return videoID,tieude,tluong
    except:
        return None,None,None

def doi_hhmmss_000_giay(hhmmss_000):
    #vd: hhmmss_000 = "12:01:1.01"
    # Tao list va dao nguoc list
    listh = (hhmmss_000.split(":"))[::-1]
    mtotal=0
    sonhan=1
    for i, pt in enumerate(listh):
        if i==0:
            sonhan=1
        elif i==1:
            sonhan=60
        elif i==2:
            sonhan=3600        
        mtotal=mtotal+float(pt)*sonhan
    # Dinh dang mtotal la string voi 3 cs thap pjhan
    mtotal="%.3f" %mtotal
    #print(mtotal)
    # 43261.01
    return mtotal

@st.cache_data
def Lay_transcript_en(url_yt):
    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url_yt, download=False)
        if info_dict["automatic_captions"]:
            #Trong info_dict["automatic_captions"]['en'] o vi tri ap chot la url cua ttml
            url_ttml = info_dict["automatic_captions"]['en'][-2]['url']
            # lay text tu url de rut ra transcript_en
            f=requests.get(url_ttml)
            textall = f.text
            vtpdau=textall.find("<p")
            textlay=textall[vtpdau:]
            vtdivc=textlay.find("</div>")
            textlay=textlay[:vtdivc]
            l_textlay=textlay.split("\n")
            l_textlays=[]
            for pt in l_textlay:
                if pt.strip() !='':
                    l_textlays.append(pt.strip())
            #print(l_textlays, len(l_textlays))
            transcript_en = []
            for j,dong in enumerate(l_textlays):
                tim=dong.split(">")[0]
                startt=tim.split(" ")[1]
                endt=tim.split(" ")[2]
                starts=startt.split('="')[1][:-2]
                ends=endt.split('="')[1][:-2]
                #print(len(starts),len(ends))
                startcc=doi_hhmmss_000_giay(starts)    
                endcc=doi_hhmmss_000_giay(ends)
                #print(startcc,endcc)
                text=dong.split(">")[1].split("<")[0]
                dictpt={}
                dictpt['start']=startcc
                dictpt['end']=endcc
                dictpt['text']=text
                transcript_en.append(dictpt)
                #print(startcc,endcc,text)
            #print(transcript_en)
            # Lenh CMD de download subtitle tu dong dich sang en cho ra file ttml ghi de khong can hoi
            #luu de nc lenh='yt-dlp -o subyt.%(ext)s --skip-download --write-auto-subs --sub-format ttml --yes-overwrites'+' '+url_yt
            return transcript_en
    except:
        print('Loi!')
        transcript_en=[]
        return transcript_en


#-------------------------------------------------------------
#@st.cache_data
def Lap_html_video(transcript_en, videoID,langSourceText):
    chp = ''
    for pt_dict in transcript_en:
        start = pt_dict['start']
        end = pt_dict['end']
        text = pt_dict['text']
        chp1 = '<div class="f-grid">\n'
        chp2 = '<div class="youtube-marker-l" data-start='+'"'+start+'"' + ' data-end='+'"'+end+'"'+'>'+text+'</div>\n'
        chp3 = '<div class="youtube-marker-r" data-start='+'"'+start+'"' + ' data-end='+'"'+end+'"'+'></div>\n'
        chp4 = '</div>\n' 
        chp = chp + chp1 + chp2 + chp3 +chp4
    # in chp de copy dan vao html     
    #print(chp)    
    sty='''
        body{
            background:lightgray;
            /*background-color: darkgray;*/}
        .video-wrapper {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;}
        .video-wrapper iframe {
            position: absolute;
            top:0;
            left: 0;
            width: 100%;
            height: 100%;}
        .f-grid {
            display: flex;
            justify-content: space-between;
            margin-left:0rem;
            flex-flow: row wrap;
            margin-bottom: -1.5rem;}
        .youtube-marker-l{
            flex: 3 0;
            margin-left: 0.5rem;
            margin-bottom: 0rem;
            font-size: 0pt;
            padding: 1rem;}
        .youtube-marker-r{
            flex: 3 0;
            margin-left: 0.5rem;
            margin-bottom: 0rem;
            font-size: 0pt;
            padding: 1rem;
            color:darkblue;}
        .youtube-marker-r:hover {
            cursor: pointer;}
        .youtube-marker-r-current {
            color: brown;}
        .center {
            font-size: 13pt;
            display: flex;
            justify-content: center;
            align-items: center;}

        h2 {
            font-size:20pt;
            text-align: center;
            color:green;}

        #elm_url_yt{
            font-size: 0pt;}
        #elm_lang_source{
            font-size: 0pt;}
        .rateread {
            font-size: 13pt;
            display: flex;
            justify-content: center;
            align-items: center;}
        #trudi{
            color:red;
            height: 30px;
            width: 30px;
            border-radius: 50%;
            border: none;} 
        #congthem {
            color:red;
            height: 30px;
            width: 30px;
            border-radius: 50%;
            border: none;}
        #vnoi {
            color:blue;
            height: 40px;
            width: 40px;
            border: 4;}
        #read_sub {
            color:green;}    
        #btn {
            color:green;}
        #volume {
            height: 40px;
            width: 40px;
            text-align: center;
            border-radius: 50%;
            border: none;} 
        '''
    js1='''
        //bien global
        var strBuffer = {};
        var btn_elm = document.getElementById('btn');
        var k_sub = 0;
        var lang_source_text = document.getElementById('elm_lang_source').innerHTML;
        var lang_dich_ra;
        var voice_speak_dich;
        var rate =  Number(document.getElementById('vnoi').innerHTML).toFixed(1);   
        var Read_Sub_Crack = 1;
        var volume_value = 1;
        const readSubEl = document.getElementById('read_sub');
        
        //tao menu select_target_dialect lang dich ra tu dong dich 
        let l_target_language = ['Danish', 'English', 'French', 'German', 'Italian', 'Japanese', 'Korean', 'Mexico', 'Nederlands', 'Rusian', 'Taiwan', 'Thai', 'Vietnamese']; 
        let l_target_voices = ['da-DK', 'en-US', 'fr-FR', 'de-DE', 'it-IT', 'ja-JP', 'ko-KR', 'es-MX', 'nl-NL', 'ru-RU', 'zh-TW', 'th-TH', 'vi-VN']; 
        let l_target_voices_tg = []; 

        //---------------------------------
        function populateVoiceList() {
            if (typeof speechSynthesis === "undefined") {
                return;
            }
            const voices = speechSynthesis.getVoices();
            for (let i = 0; i < voices.length; i++) {
                //neu voices[i].lang co trong l_target_voices va voices[i].lang chua co trong l_target_voices_tg thi lay 
                //l_target_language[l_target_voices.indexOf(voices[i].lang] dua vao  select_target_language
                if ( l_target_voices.indexOf(voices[i].lang) >= 0 ){
                    select_target_language.options.add(new Option(l_target_language[l_target_voices.indexOf(voices[i].lang)]+' ('+voices[i].lang+') - '+voices[i].name));
                    //cai nay de kiem tra voices[i].lang dem vao chi 1 lan
                    l_target_voices_tg.push(voices[i].lang);
                    
                    //chon default
                    //if (voices[i].lang.includes('vi-VN') && (voices[i].name.includes('Linh') || voices[i].name.includes('An')) ){
                    if (voices[i].lang.includes('vi-VN') ){
                        //hai bien global lay gia tri ghi vao memory
                        lang_dich_ra = voices[i].lang.slice(0, 2) ;
                        voice_speak_dich = voices[i].lang;
             
                        //chi dinh default trong menu se hien ra
                        let indexChon = l_target_voices_tg.indexOf(voices[i].lang);
                        select_target_language.selectedIndex = indexChon;
                        t_translate(lang_source=lang_source_text, lang_dich_ra=lang_dich_ra);
                        //return;
                    }
                }
            }
        }
        //---------------------
        populateVoiceList();
        if (typeof speechSynthesis !== "undefined" && speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = populateVoiceList;
        }
        //-----------------------------------------------
        function active_target_lang() {
            //let selectedValue = select_target_language.options[select_target_language.selectedIndex].text;
            let index_chon = select_target_language.selectedIndex;
            //let text_brow = select_target_language.value;
            let lang_rut = l_target_voices_tg[index_chon];
            //alert(lang_rut);
            if (typeof speechSynthesis === "undefined") {
                return;
            }
            const voices = speechSynthesis.getVoices();
            for (let i = 0; i < voices.length; i++) {
                if (voices[i].lang.includes(lang_rut)){
                    lang_dich_ra = lang_rut.slice(0, 2);
                    voice_speak_dich =  voices[i].lang;
                    t_translate(lang_source=lang_source_text, lang_dich_ra=lang_dich_ra);
                    return;
                }  
            }
        }
        //---Dich ra ----------------------------------------- 
        function t_translate(lang_source, lang_dich_ra) { 
            const sourceLanguage = lang_source;
            const targetLanguage = lang_dich_ra;
            var els = document.getElementsByClassName("youtube-marker-l"); // Creates an HTMLObjectList not an array.
            var elsd = document.getElementsByClassName("youtube-marker-r")

            Array.prototype.forEach.call(els, function(el,i) {
                let inputText = el.innerText;
                let outputTextEle = elsd[i];

                const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${sourceLanguage}&tl=${targetLanguage}&dt=t&q=${encodeURI(inputText)}`;

                const xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function () {
                    if (this.readyState == 4 && this.status == 200){
                        const responseReturned = JSON.parse(this.responseText);
                        const translations = responseReturned[0].map((text) => text[0]);
                        const outputText = translations.join(" ");
                        outputTextEle.textContent = outputText;
                    }
                };
                //---------------------
                xhttp.open("GET", url);
                xhttp.send();
            });
        }
        //======== Cua youtube API ====================================
        let videoIDcurrent = document.getElementById("elm_url_yt").innerText;
        //---------------------------------
        let player;
        let timeStart = 0;
        let timeStartl = -1;

        //-----------------------------------
        function onYouTubeIframeAPIReady() {

            //3a-Instantiate the Player, phai co player=... de iframeWindow hoat dong
            player = new YT.Player("player", {
                //da co iframe quy dinh roi
                height: "300",
                width: "480",
                videoId: videoIDcurrent
            });
            //3b- This is the source "window" that will emit the events.
            var iframeWindow = player.getIframe().contentWindow;

            //3c- So we can compare against new updates.
            var lastTimeUpdate = 0;
            //3d- Listen to events triggered by postMessage ,this is how different windows in a browser (such as a popup or iFrame) can communicate. // See: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
            window.addEventListener("message", function(event) {
                // Check that the event was sent from the YouTube IFrame.
                if (event.source === iframeWindow) {
                    var data = JSON.parse(event.data);
                    // The "infoDelivery" event is used by YT to transmit any kind of information change in the player, such as the current time or a playback quality change.
                    //===SPEAK SUB HERE=======================================================
                    if (data.event === "infoDelivery" && data.info && data.info.currentTime) {
                        //console.log(data.info.currentTime);
                        //time co dang 212.544 giay
                        //var time = Math.round(data.info.currentTime * 1000) / 1000;
                        var time = Math.round(data.info.currentTime);//lam tron sec

                        const [strBuffer, strBuffer2] = lay_strBuffer();
                        //dang cua strBuffer la {1.224:'Toi', 2.16:'Anh', 3.111: 'No'}

                        timeStart = time;
                        let text = strBuffer[timeStart];
                        let ellay = strBuffer2[timeStart];

                        //Neu timeStart khac voi timeStartl luu va text khac trong  
                        if (timeStart !== timeStartl && text){
                            //console.log(timeStart, ellay);
                            timeStartl = time; 
                            subtitle.innerText = text;
                            ellay.classList.add("youtube-marker-r-current");
                            //phat am----------------------------------------
                            Read_Sub(text);
                        }//--------------------------------------------------

                        //Cu sau moi sec thi hien thi thoi gian
                        // currentTime is emitted very frequently (milliseconds), but we only care about whole second changes.
                        //var time = Math.floor(data.info.currentTime);
                        //var time = data.info.currentTime;
                        if (time !== lastTimeUpdate) {
                            lastTimeUpdate = time;
                            // It's now up to you to format the time. tinh ra phan tram thoi gian da chay youtub
                            //document.getElementById("time").innerHTML = '(' + Math.round(100*time/player.getDuration()) +' %) &nbsp;';
                        }  
                    }
                }
            });
        }
                            //marker.dom.classList.add("youtube-marker-r-current");

        //---------Lay strBuffer phu de moi sec--------------------------
        function lay_strBuffer(){
            let strBuffer = {},
                strBuffer2 = {};
            var elsd = document.getElementsByClassName("youtube-marker-r");
            Array.prototype.forEach.call(elsd, function(el,i) {
                let start = Math.round(el.attributes[1].value);
                let text = el.innerHTML;
                strBuffer[start] = text;
                strBuffer2[start] = el;

            });
            return [strBuffer, strBuffer2];
        }
        //------------------------------------------------------
        function cong1(){
            rate =  Number(document.getElementById('vnoi').innerHTML).toFixed(1);
            if (rate >= 0.0 && rate < 3.0) {
                document.getElementById('vnoi').innerHTML = (Number(document.getElementById('vnoi').innerHTML) + Number("0.1")).toFixed(1);
            }
        }
        //----------------    
        function tru1(){
            rate =  Number(document.getElementById('vnoi').innerHTML).toFixed(1);
            if (rate <= 3 && rate > 0) {
                document.getElementById('vnoi').innerHTML = (Number(document.getElementById('vnoi').innerHTML) - Number("0.1")).toFixed(1);
            }
        }
        //------Moi lan click thi hien thi hoac an di subtitles-------
        btn_elm.onclick = function(){
        
            k_sub = k_sub + 1;
            if (k_sub % 2 === 1){
                document.getElementById("btn").style.color="brown";

                var el = document.querySelectorAll(".youtube-marker-l");
                for ( var i = 0; i < el.length; i ++ ) {
                    el[i].style.fontSize = "14pt";
                }
                var el = document.querySelectorAll(".youtube-marker-r");
                for ( var i = 0; i < el.length; i ++ ) {
                    el[i].style.fontSize = "14pt";
                }

            }else{
                document.getElementById("btn").style.color="green";

                var el = document.querySelectorAll(".youtube-marker-l");
                for ( var i = 0; i < el.length; i ++ ) {
                    el[i].style.fontSize = "0pt";
                }
                var el = document.querySelectorAll(".youtube-marker-r");
                for ( var i = 0; i < el.length; i ++ ) {
                    el[i].style.fontSize = "0pt";
                }

            }
        }       
        //-----------------------
        function Read_Sub_Volume(){
            Read_Sub_Crack = Read_Sub_Crack + 1;
            if (Read_Sub_Crack % 2 === 0){
                volume_value = 0;
                document.getElementById("volume").style.color="red";
                document.getElementById("read_sub").style.color="red";
            }else{
                volume_value = 1;
                document.getElementById("volume").style.color="green";
                document.getElementById("read_sub").style.color="green";

            }
        }
        //--------------------------
        function Read_Sub(text){
        
            rate = Number(document.getElementById('vnoi').innerHTML).toFixed(1);
            var msg     = new SpeechSynthesisUtterance();
            msg.volume = volume_value;
            msg.rate = rate; 
            msg.lang = voice_speak_dich;
            msg.text = text;
            speechSynthesis.speak(msg);
        
        }
        //--------------------------------------------------------------
        '''
    components.html(f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Video Translate Speak Subtitle</title>

                    <style>{sty}</style>
                    </head>
                    <body>
                    <div class="video-wrapper">
                        <div id="player"></div>
                    </div>
                    <span id="elm_url_yt">{videoID}</span><span id="elm_lang_source">{langSourceText}</span>

                    <hr>
                    <div class="center">
                        Voice &nbsp; <select id="select_target_language" onchange ="active_target_lang()"></select>&emsp;
                        <button id="volume" onclick="Read_Sub_Volume()">Vol</button>
                    </div><br>

                    <div class="rateread">
                        <button id="read_sub" onclick="Read_Sub()">Speak</button>&emsp; &emsp; 
                        <button id="trudi" onclick="tru1()">-</button>&emsp; &emsp; 
                        <button id="vnoi">1.2</button>&emsp; &emsp; 
                        <button id="congthem" onclick="cong1()">+</button>&emsp;&emsp;
                        <button id="btn">Sub</button>
                    </div>

                    <hr>
                    <h2 id="subtitle"></h2>


                    {chp}

                    <script>{js1}</script>

                    <!-- Phai co dong sau thi moi speak duoc-->
                    <script src="https://www.youtube.com/iframe_api"></script>

                </body>
                </html>
                """,height=900,scrolling=True)

@st.cache_data
def get_subtu_fastwhisper(url_yt):
    try:
        # Moi khi ham nay chay thi tao ra mot thu muc tam voi ten nau nhien moi, xong viec thi xoa
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, "audioyt.wav")
            filepath = download_yt_audio(url_yt, filepath)
            #with open(filepath, "rb") as f:
            #    data_inputs = f.read()
            #st.audio(data_inputs)
            model = WhisperModel("base", device="cpu", compute_type="int8") #
            segments, info = model.transcribe(filepath)
            langnhanra = info.language
            listdongs=[]
            for segment in segments:
                dongtext="[%.3fs -> %.3fs] %s" % (segment.start, segment.end, segment.text)
                listdongs.append(dongtext)
                #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            # Dua [[0.000s -> 9.000s]  Now, the VOA,...]  ve dang json: [{'start':'001.234', 'end':'005.567','text':'tien'},...]
            list_dict_dong=[]
            for dong in listdongs:
                #dong co dang: [0.000s -> 9.000s]  Now, the VOA.
                dictdong={}
                dong_time=dong.strip().split("]")[0][1:] #dang: 0.000s -> 9.000s
                dictdong['start']=dong_time.split(" -> ")[0][:-2]
                dictdong['end']=dong_time.split(" -> ")[1][:-2]
                dictdong['text']=dong.strip().split("]")[1].strip()
                list_dict_dong.append(dictdong)
            return list_dict_dong,langnhanra
    except:
        print('Loi')
        list_dict_dong=[]
        langnhanra=''
        return list_dict_dong,langnhanra
#==============================================================================
#https://youtu.be/3c-iBn73dDE?si=loeUZPwUmmh0iGW4   2h 40phut
#https://youtu.be/DpxxTryJ2fY?si=oMvtK4Nqt-y6Een9   BIGATE          ok en vi
#https://youtu.be/zBHxv8gbleg?si=zeo5OQ_cx5XsQgeG   TRUMP           ok en vi
#https://www.youtube.com/embed/lcZDWo6hiuI          Gs University   ok en vi
#https://www.youtube.com/watch?v=Z2iXr8On3LI        voa anh van     no en no vi (not is yt)
#https://youtu.be/Zgfi7wnGZlE?si=TzeWpiERRxzdJKVA   obama           ok en vi (#1h)
#https://youtu.be/d6k48XVpgcM?si=F6f6VjqTQSTk8mwZ   tin Viet
#https://www.youtube.com/embed/e079x_gKE3Xp_Bt      che lai
#https://youtu.be/8QlXeGWS-EU?si=vPyl1aFhfCPEEEzK beo dat
#---Bat Dau Main ------------------------------------------------------------------------------------------------
tbaodong1 = st.empty()
tbaodong1.write("<h2 style='text-align: center; color: green;'>VIDEO FOR LISTENING SUBTITLES</h2>", unsafe_allow_html=True)
link_vidu="https://youtu.be/DpxxTryJ2fY?si=oMvtK4Nqt-y6Een9"
tbaodong2 = st.markdown("<h6 style='text-align: center; color: lightblue;'>"+link_vidu+"</h6>", unsafe_allow_html=True)


url_yt=input_box(min_lines=1,max_lines=3,just_once=True)
tbaodong3 = st.empty()
tbaodong3.write(':blue[Nhập vào khung trên URL của video youtube muốn xem. Ví dụ như url ở trên]')

if url_yt:
    videoID,tieude,tluong = Lay_id_tde_tluong(url_yt)
    if videoID:
        tbaodong3.write(':blue[Lấy phụ đề từ yt_dlp...]')
        transcript_en = Lay_transcript_en(url_yt)
        if transcript_en:
            Lap_html_video(transcript_en, videoID, langSourceText="en")
            tbaodong3.write("<h4 style='text-align: center; color:orange;'>"+tieude+"</h4>", unsafe_allow_html=True)
            st.write('---')
            st.write('Video này dài  ' + str(int(tluong/60)+1) + ' phút. (Có thể bị cắt khi quá 120 phút!)')
            st.balloons()
        else:   # khong co transcript_en tai Yt thi phai lay ai api whjax, cung chua co f audio
            tbaodong3.write(':green[Xin đợi phiên âm từ Fast-Whisper do không có phụ đề trên yt...Có thể phải làm lại cho đén khi thành công!]')
            transcript_language,langnhanra = get_subtu_fastwhisper(url_yt)
            #print(transcript_language,langnhanra)
            if transcript_language:
                Lap_html_video(transcript_language, videoID, langSourceText=langnhanra)
                tbaodong3.write("<h4 style='text-align: center; color:orange;'>"+tieude+"</h4>", unsafe_allow_html=True)
                st.write('---')
                st.write('Video này dài  ' + str(int(tluong/60)+1) + ' phút. (Có thể bị cắt khi quá 120 phút!)')
                st.balloons()
            else:
                tbaodong3.write(':blue[Nhập vào khung trên URL của video youtube muốn xem. Ví dụ như url ở trên]')
                pass
#Improve your English 👍_ Very Interesting Story - Level 3 - The History of America _ VOA #7
# 7-https://youtu.be/WCZ2-SIT7W8?si=eUAWum9rCDYEsjY8

#Improve your English ⭐ | Very Interesting Story - Level 3 - Million Pound Bank Note | VOA #8
# 8-https://youtu.be/G_uExyg8M2A?si=hFnMcBJCndcyiApg

#Improve your English ⭐ | Very Interesting Story - Level 3 - The Great Gatsby P1 | VOA #9
# 9-https://youtu.be/4ONCixK4z1A?si=mDV3a0ru82g-_fTe

#Improve your English ⭐ | Very Interesting Story - Level 3 - History of the USA | VOA #10
# 10-https://youtu.be/K9W6v57l6Ag?si=Tz6EZk6a66hS_lWo

#Improve your English ⭐ | Very Interesting Story - Level 3 - Aesop's Fables | VOA #11
# 11- https://youtu.be/4aqjFp1o9iE?si=t5_tl56iR8hVmsnj

#Improve your English ⭐ | Very Interesting Story - Level 3 - Beauty's Sacrifice | VOA #12
# 12-https://youtu.be/HdGN08QZqlY?si=LQlDfyEvvsn-Id2S
