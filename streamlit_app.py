# SHA256:RoAD9Z4kYydmuiQnyfJBZJXBKR4K7wariN94kO3MJgI
import streamlit as st
import textwrap
import yt_dlp
import requests
#--------------
import json
#import streamlit.components.v1 as components 
import os
import xml.etree.ElementTree as ET
import time
from urllib.parse import urlparse, parse_qs

#----------------------- cac def ---------------------
def get_subtitle_urls(info_dict):
    def extract_urls(subs_dict):
        urls = {}
        for lang, tracks in subs_dict.items():
            ttml_url = None
            for track in tracks:
                ext = track.get("ext")
                if ext == "ttml" and not ttml_url:
                    ttml_url = track.get("url")
            # Ưu tiên TTML, fallback sang VTT nếu không có
            if ttml_url:
                urls[lang] = {"ext": "ttml", "url": ttml_url}
        return urls

    subtitles = info_dict.get("subtitles", {})
    auto_captions = info_dict.get("automatic_captions", {})

    return {
        "official_subtitles": extract_urls(subtitles),
        "automatic_captions": extract_urls(auto_captions)
    }

def time_to_seconds(t):
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def parse_ttml_with_seconds(ttml_string):
    root = ET.fromstring(ttml_string)
    namespace = {'ttml': root.tag.split('}')[0].strip('{')}

    subtitles = []
    for p in root.findall('.//ttml:body//ttml:p', namespaces=namespace):
        begin = p.attrib.get('begin')
        end = p.attrib.get('end')
        text = ''.join(p.itertext()).strip()

        if begin and end and text:
            subtitles.append({
                'start': round(time_to_seconds(begin),3),
                'end': round(time_to_seconds(end),3),
                'text': text,
                'textdich': ""
            })
    return subtitles


#--------------------------MAIN ---------------------------------------
def lay_Id_Title_Sub(url):
    video_url = url
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ratelimit': 500000,  # giới hạn tốc độ tải: 500 KB/s
        #'sleep_interval_requests': 2,  # nghỉ 2 giây giữa các request
        'skip_download': True,
        'forcejson': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        videoID = info_dict['id']
        tieude = info_dict['title']
        print("videoID: ",videoID)
        print("Tieu de: ",tieude)
        # xet phu de                    
        subtitle_data = get_subtitle_urls(info_dict)
        # xet phu de truyen thong
        if subtitle_data["automatic_captions"] != {}:
            if subtitle_data["automatic_captions"]["en"]:
                dangPdEn = subtitle_data["automatic_captions"]["en"]["ext"]
                urlPdEn = subtitle_data["automatic_captions"]["en"]["url"]
                ttLayPdEn = [dangPdEn, urlPdEn]
                f = requests.get(ttLayPdEn[1])
                if dangPdEn == "ttml":
                    ttml_content = f.text
                    subtitles = parse_ttml_with_seconds(ttml_content)
                    print("Co subtitles")
            else:
                print("No en subtitles!")           
        else:
            subtitles = []
            print("No subtitles!")

        if len(subtitles)>0:
            #tepjson = videoID + ".json"
            #output_file = os.path.join(save_dir, f"{tepjson}")
            #with open(output_file, 'w', encoding='utf-8') as f:
            #    json.dump(subtitles, f, ensure_ascii=False, indent=2)

            #print(f"✅ Đã lưu vào: {output_file}")
            return videoID,tieude,subtitles

#=== MAIN =====================================================
st.set_page_config(page_title="YouTube TTS", layout="centered")
st.markdown("<h4 style='text-align: center;color:green;'>YouTube với Phụ đề nói</h4>", unsafe_allow_html=True)

# Nhập URL YouTube
url = st.text_input("Nhập URL YouTube:", label_visibility="hidden", placeholder="Nhập URL YouTube:")
# https://www.youtube.com/watch?v=dQw4w9WgXcQ

video_id=""
title=""
subtitles=[]

if url:
    with st.spinner("Đang tải phụ đề json..."):
        try:
          video_id,title,subtitles = lay_Id_Title_Sub(url)
          if video_id=="" or title=="" or len(subtitles)==0 :
            st.write(":red[Sorry! Không thể lấy Phụ đề!]")
            sys.exit()

             
          # Load phụ đề từ subtitles.json
          #with open("1ivMkhtGq4o.json", "r", encoding="utf-8") as f:
          #    subtitles = json.load(f)

          #subtitles_js = json.dumps(subtitles, ensure_ascii=False)
          subtitles_js = subtitles
          listVideoId = [video_id+"|"+title]

          # HTML + JS nhúng vào Streamlit
          html_code = f"""
          <!DOCTYPE html>
          <html lang="en">
          <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script> <!-- Import SweetAlert2 -->
              <title>Preparing to settle in the US</title>

          <style>
          body{{
            height:100%;
            background-image: linear-gradient(30deg, #1666b0, #fbfafb); 
            color: #fff;
            font: 1rem/1 'Poppins', sans-serif;
            max-width: 800px;
            flex-direction: column;
            padding-bottom: env(safe-area-inset-bottom);
            background-size: cover;
            background-position: center;
            display: block;
            margin-left: auto;
            margin-right: auto; /* hoặc margin: 0 auto; */
            margin-bottom: 100%;
          }}
          .video-container {{
            position: relative;
            width: 100%;
            min-width: 100%;      /* ép không co lại */
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            background: #000;
          }}
          iframe {{ 
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: block;       /* tránh Safari thêm khoảng trắng */
          }}
          .menu-group {{
            margin-top: 4px;  
            display: flex;
            justify-content: space-between;
            padding: 0 0 ; 
            width: 100%;
            box-sizing: border-box;
          }}
          .butp1,.butp2{{
            font-size: 1.4rem;
          }}
          #voiceSelect{{
            color:darkgreen;
            width: 30%; 
            display: block;
            margin-left: 0;
            font-size: 1.4rem;
          }}
          #videoSelect {{
            color:rgb(2, 78, 2);
            width: 75%; 
            display: block;
            margin-left: auto;
            margin-right: auto; /* hoặc margin: 0 auto; */
            font-size: 1.1rem;
            color:gray;
            text-align: center;
          }}
          #rateRead{{
            font-size: 1.4rem;
          }}
          #voiceSelect,#rateRead,.butp1,.butp2,#playBtn{{
            width: 19%;
            font-size: 0.9rem;
          }}
          #currentSubtitle{{
            text-align: right;
            font-size: 1.4rem;
            color: darkgreen;
          }}
          #subdich{{
            text-align: left;
            color: darkblue;
            font-size: 1.6rem;
            height:4rem;
            margin-left:10px;
            font-style: italic;
          }}
          #playBtn{{
            background-color: transparent;
            color:darkblue;
            font-weight:bolder;
            font-size: 1.2rem;
          }}
          #currentSubtitle{{
            height:3rem;
            margin-right: 10px;
          }}
          #loa_button{{
            margin-left:10px;
            margin-bottom:4px;
          }}
          </style>
          </head>
          <body>
              <div class="video-container">
                  <div id="playerContainer"></div>
              </div>
              
              <div class="menu-group">
                  <select id="voiceSelect" ></select>
                  <button id='rateRead' onclick="tocDoDoc()">Rate: 1</button>

                  <button id="playBtn">START ▶️</button>

                  <button class='butp1' onclick="btnReadSub()">Read sub only</button>
                  <button class='butp2' onclick="btnYoutubeSound()">Sound yt only</button>
              </div>
              <hr>
              <div class='outiframe'>
                  <br>
                  <div id="currentSubtitle">[source subtitles]</div>
                  <div id="loa_button">🔊</div>
                  <div id="subdich">[translated subtitles ]</div>
                  <br>
                  <hr><hr>
                  <select id="videoSelect" ></select>
              </div>

            <!-- YouTube API -->
            <script src="https://www.youtube.com/iframe_api"></script>

          <script>
          let subtitles = '';   
          var rateVread = 1;
          var utterance_volume=1;
          // ==========================
              // 0. TAO MENU VDEO_ID
              // ==========================

              let listIdTd = {listVideoId};

              //tao list videos chua cac thong tin id, subtitle, title
              const videos = listIdTd.map(item => {{
              const [id, title] = item.split("|");
              return {{
                  id: id,
                  title: title.trim()
              }};
              }});

              //tao menu chon video (select_id)
              videos.forEach((v, index) => {{
              const option = document.createElement("option");
              option.value = v.id;
              option.textContent = v.title;
              videoSelect.appendChild(option);
              }});

              // ==========================
              // 1. LOAD VOICES
              // ==========================
              const voiceSelect = document.getElementById("voiceSelect");
              let voices = [];

              function loadVoices() {{
                voices = speechSynthesis.getVoices();
                if (!voices.length) return;

                voiceSelect.innerHTML = "";
                voices.forEach(v => {{
                  const opt = document.createElement("option");
                  opt.value = v.name;
                  opt.textContent = `${{v.lang}} ${{v.name}}`;
                  voiceSelect.appendChild(opt);
                }});
              }}

              speechSynthesis.onvoiceschanged = loadVoices;
              loadVoices();

          //ham khoi phuc 
          function restoreSelections() {{
            const savedVideo = localStorage.getItem("selectedVideoId");
            const savedVoice = localStorage.getItem("selectedVoiceName");
            // Khôi phục video
            if (savedVideo) {{
              videoSelect.value = savedVideo;
            }}
            // Khôi phục voice
            if (savedVoice) {{
              const check = voices.find(v => v.name === savedVoice);
              if (check) voiceSelect.value = savedVoice;
            }}
          }}

          //moi khi voice thay doi thi khoi phuc da luu
          speechSynthesis.onvoiceschanged = () => {{
            loadVoices();
            restoreSelections();   // 🔥 khôi phục voice + video
          }};

              // ==========================
              // 2. YOUTUBE PLAYER
              // ==========================
              let player = null;

              function onYouTubeIframeAPIReady() {{
                player = new YT.Player("playerContainer", {{
                  height: "315",
                  width: "560",
                  videoId: document.getElementById("videoSelect").value,
                  playerVars: {{ autoplay: 0, controls: 1 }},
                  events: {{
                    onReady: () => {{}},
                    onStateChange: (e) => {{
                      if (e.data === YT.PlayerState.PAUSED) stopReading();
                      if (e.data === YT.PlayerState.PLAYING) resumeSync();
                      if (e.data === YT.PlayerState.ENDED) stopReading();
                    }}
                  }}
                }});
              }}
              window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;

              // ==========================
              // 3. FETCH JSON SUBTITLES
              // ==========================

              // ==========================
              // 4. TTS + SYNC SUBTITLES
              // ==========================
              //let subtitles = [];
              let interval = null;
              let currentIndex = -1;
              const subDiv = document.getElementById("currentSubtitle");

              function speak(textd) {{
                speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance(textd);
                utter.rate = rateVread;
                const selected = voiceSelect.value;
                const voice = voices.find(v => v.name === selected);
                if (voice) utter.voice = voice;
                loa_button.onclick = () => {{
                  utter.volume = utterance_volume;
                  speechSynthesis.speak(utter);
                }}
                loa_button.click(); // tự động phát luôn
            }}

              function stopReading() {{
                speechSynthesis.cancel();
                clearInterval(interval);
                interval = null;
                currentIndex = -1;
              }}

              function resumeSync() {{
                stopReading();
                startSync();
              }}

              function startSync() {{
                interval = setInterval(() => {{
                  if (!player || !subtitles.length) return;

                  const t = player.getCurrentTime();
                  let idx = subtitles.findIndex(s => t >= s.start && t < s.end);

                  if (idx !== currentIndex) {{
                    currentIndex = idx;

                    if (idx === -1) {{
                      subDiv.textContent = "";
                    }} else {{
                      document.getElementById("currentSubtitle").textContent = subtitles[idx].text;
                      document.getElementById("subdich").textContent = subtitles[idx].textdich;
                      speak(subtitles[idx].textdich);
                    }}
                  }}
                }}, 200);
              }}

              // ==========================
              // 5. PLAY BUTTON
              // ==========================
          document.getElementById("playBtn").addEventListener("click", async () => {{
            const videoId = document.getElementById("videoSelect").value;

            //subtitles = await fetchSubtitles(videoId);
            subtitles = {subtitles_js};

            // 🔥 DỊCH TOÀN BỘ JSON
            translateFullJson(subtitles);

            player.loadVideoById(videoId);
            player.playVideo();

            startSync();
          }});


              // ==========================
              // 6. AUTO PLAY WHEN CHANGE VIDEO
              // ==========================
          document.getElementById("videoSelect").addEventListener("change", async () => {{
              localStorage.setItem("selectedVideoId", videoSelect.value);
              const videoId = videoSelect.value;

              subtitles = {subtitles_js};

              // 🔥 DỊCH TOÀN BỘ JSON
              translateFullJson(subtitles);

              player.loadVideoById(videoId);
              player.playVideo();

              startSync();

            }});

          //moi lan thay doi voice thi dich lai
          document.getElementById("voiceSelect").addEventListener("change", async () => {{
              //
              localStorage.setItem("selectedVoiceName", voiceSelect.value);
              translateFullJson(subtitles);
              startSync();
          }});




          //---dich
          function translateFullJson(){{
              const selected = voiceSelect.value;
              const v = voices.find(x => x.name === selected);

              let sourceLanguage = 'en';
              let targetLanguage = v.lang.split("-")[0];
              //console.log(sourceLanguage, targetLanguage);
              //tao texts la list chua cac text cua subtitles
              let texts = subtitles.map(item => item.text);
              let textdichs = subtitles.map(item => item.textdich);

              //console.log(texts);
              
              Array.prototype.forEach.call(texts, function(cau,i) {{
                  let inputText = cau;
                  let outputTextEle = textdichs[i];

                  const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${{sourceLanguage}}&tl=${{targetLanguage}}&dt=t&q=${{encodeURI(inputText)}}`;

                  const xhttp = new XMLHttpRequest();  
                  xhttp.onreadystatechange = function () {{
                      if (this.readyState == 4 && this.status == 200){{
                          const responseReturned = JSON.parse(this.responseText);
                          const translations = responseReturned[0].map((text) => text[0]);
                          const outputText = translations.join(" ");
                          //outputTextEle.textdich = outputText;
                          subtitles[i].textdich = outputText;
                          console.log(subtitles[i].textdich);
                      }}
                  }};
                  //---------------------
                  xhttp.open("GET", url);
                  xhttp.send();
              }});
          }}
          const rateRead = document.getElementById('rateRead');
          function tocDoDoc(){{
            let rateReadValue = Number(rateRead.textContent.split(':')[1]);
            rateReadValue = (1+rateReadValue)%10;//1,2,3,4,5,0
            if (rateReadValue==0) rateReadValue=1;
            rateRead.textContent = 'Rate: '+ rateReadValue;
            rateVread = 1+rateReadValue/10;//1, 1.5, 2, 2.5, 3, 3.5
          }}

          function btnReadSub() {{
            // Tắt tiếng YouTube
            if (player && player.mute) {{
              player.mute();
            }}
            // Bật âm lượng đọc phụ đề
            utterance_volume = 1;
          }}

          function btnYoutubeSound(){{
            // Bật tiếng YouTube
            if (player && player.unMute) {{
              player.unMute();
              player.setVolume(100);
            }}
            // Tắt âm lượng đọc phụ đề
            utterance_volume = 0;
          }}


          //moi khi chay lai trang thi khoi phuc  voice + video
          restoreSelections();   // 🔥 khôi phục voice + video

          </script>


          </body>
          </html>
          """

          # Hiển thị trong Streamlit
          st.components.v1.html(html_code, height=800, scrolling=False)
        except Exception:
          st.write(":red[Sorry!! Không thể lấy Phụ đề!!]")


