# 
import streamlit as st
import textwrap
import yt_dlp
import requests
import re
import html
#--------------
import json
import os
import xml.etree.ElementTree as ET
import time


def lay_info(URL):
    info=None
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(URL, download=False)
            # ℹ️ ydl.sanitize_info makes the info json-serializable
            #print(json.dumps(ydl.sanitize_info(info)))
            if info:
                return info
        except:        
            return info
    return info

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



def ttml_to_json(ttml_text):
    # ham dung ben trong
    def ttml_time_to_seconds(t):
        if t.endswith("s"):
            return float(t[:-1])
        if t.endswith("ms"):
            return float(t[:-2]) / 1000.0

        parts = t.split(":")
        parts = [float(p) for p in parts]

        if len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = parts
            return m * 60 + s
        else:
            return parts[0]
    #-het ham trong-------------------

    root = ET.fromstring(ttml_text)
    ns = {'tt': 'http://www.w3.org/ns/ttml'}

    items = []

    for p in root.findall('.//tt:p', ns):
        begin = p.attrib.get('begin')
        end = p.attrib.get('end')

        text = ''.join(p.itertext()).strip()
        text = html.unescape(text)

        if not text:
            continue

        items.append({
            "start": round(ttml_time_to_seconds(begin),3),
            "end": round(ttml_time_to_seconds(end),3),
            "text": text
        })

    return items

#--merge cap---
def merge_by_sentence(subtitles, max_gap=1.5, max_length=150):
  """
  Gộp các phụ đề ngắn thành câu dài hơn để đọc tự nhiên hơn.
  
  Args:
      subtitles: List các phụ đề gốc
      max_gap: Khoảng cách tối đa giữa 2 phụ đề để gộp (giây)
      max_length: Độ dài tối đa của câu đã gộp (ký tự)
  
  Returns:
      List phụ đề đã được gộp
  """
  if not subtitles:
      return []
  
  merged = []
  current = {
      'start': subtitles[0]['start'],
      'end': subtitles[0]['end'],
      'text': subtitles[0]['text'],
      'textdich': ""
  }
  
  for i in range(1, len(subtitles)):
      sub = subtitles[i]
      gap = sub['start'] - current['end']
      
      # Kiểm tra xem có nên gộp không
      should_merge = False
      
      # Điều kiện 1: Khoảng cách giữa 2 phụ đề nhỏ
      if gap <= max_gap:
          # Điều kiện 2: Câu hiện tại chưa kết thúc (không có dấu câu kết thúc)
          current_text_stripped = current['text'].rstrip()
          if not current_text_stripped.endswith(('.', '!', '?', '。', '！', '？')):
              should_merge = True
          # Hoặc câu tiếp theo bắt đầu bằng chữ thường (tiếp nối)
          elif sub['text'] and sub['text'][0].islower():
              should_merge = True
      
      # Điều kiện 3: Không gộp nếu câu quá dài
      if should_merge and len(current['text']) + len(sub['text']) > max_length:
          should_merge = False
      
      if should_merge:
          # Gộp phụ đề vào câu hiện tại
          current['text'] = current['text'].rstrip() + ' ' + sub['text']
          current['end'] = sub['end']
      else:
          # Lưu câu hiện tại và bắt đầu câu mới
          merged.append(current)
          current = {
              'start': sub['start'],
              'end': sub['end'],
              'text': sub['text'],
              'textdich': ""
          }
  
  # Thêm câu cuối cùng
  merged.append(current)
  
  return merged



#=== MAIN =====================================================
st.set_page_config(page_title="YouTube TTS",  layout="centered",)
st.markdown("""
<style>
#MainMenu {visibility: visible;}
header {visibility: visible;}
.block-container {
padding-top: 2.2rem;
}
</style>
""", unsafe_allow_html=True)


tieuDeTrangChinh = st.empty()
tde = "YouTube với Phụ đề nói"
tieuDeTrangChinh.markdown(
  f"<h4 style='text-align: center;color:green;'>{tde}</h4>", 
  unsafe_allow_html=True
)
aboutApp = st.empty()

with aboutApp.container():
    st.markdown("🎯 :red[ABOUT:]")
    st.write(":blue[App này được viết để xem các video youtube có phụ đề tiếng Anh. Phụ đề này có thể được dịch ra ngôn ngữ khác và]" + ":red[ NÓI phụ đề theo giọng của trình đọc trong máy đồng bộ với tiếng nói trong video.👍]") 
    st.write(":green[Nó giúp cho những người chưa rành tiếng Anh có thể xem youtube thuần tiếng Anh hiểu được nội dung theo tiếng dịch ra và được máy đọc lên.]") 
    st.write(":blue[Nó cũng giúp cho việc tự học tiếng Anh qua việc chỉ xem yt gốc tiếng Anh, hoặc chỉ nghe tiếng đã dịch theo các nút chọn. Hiện nay có rất nhiều yt dạy tiếng Anh để ta sử dụng cho việc tự học này.]") 
    st.write("🔎 :red[CÁCH SỬ DỤNG:]") 
    st.write(":green[1 >> Vào sidebar bên trái để nhập một URL của video youtube.]") 
    st.write(":green[URL này có nhiều cách lấy. Thông dụng nhất là vào trang youtube, chọn một video để mở nó lên rồi Crt-C url đó đem dán vào khung nhập url của app này.]") 
    st.write(":blue[2 >> Sau đó làm theo lời nhắc trên sidebar cho đến khi thành công thì khung video yt sễ hiển thị ở trang chính.]") 
    st.write(":green[3 >> Chọn tiếng sẽ dịch và giọng đọc tại nút đâu tiên bên trái. (có thể chọn lại trong quá trình xem)]") 
    st.write(":blue[4 >> Nhấp vào nút START để bắt đầu play video.]") 
    st.write(":green[5 >> Nếu cần điều chỉnh tốc độ giọng đọc băn dịch thì nhấp nút RATE cho đến khi phù hợp.]") 
    st.write(":blue[6 >> Nút 4: Chỉ nghe giọng đọc bản dịch, tắt âm thanh video.]") 
    st.write(":green[7 >> Nút 5: Chỉ nghe âm thanh video, tắt giọng đọc bản dịch.]") 
    st.write(":blue[8 >> Nút 6: Chỉ nghe âm thanh video, tắt giọng đọc bản dịch.]") 
    st.write(":red[9 >> Nếu muốn xem video yt khác thì xóa url cũ và nhập url khác.]") 
    st.write("⁉️ :green[Hãy nhấp vào biểu tượng 🔊 khi đã bật nghe phụ đề mà không có tiếng.]") 
# bien global
video_id=""
title=""
subtitles=[]
thoiluong=0
#############

# Khởi tạo state
if "url" not in st.session_state:
    st.session_state.url = ""

if "last_url" not in st.session_state:
    st.session_state.last_url = ""

def save_and_clear():
    # Lưu lại giá trị trước khi xoá
    st.session_state.last_url = st.session_state.url
    # Xoá nội dung ô nhập
    st.session_state.url = ""

#st.text_input("Nhập URL:", key="url")

#st.button("Lưu & Xoá", on_click=save_and_clear)

#st.write("URL cuối cùng đã lưu:", st.session_state.last_url)


with st.sidebar:
    st.title('🏷️ :blue[Youtube với Phụ đề "nói"]')
    st.write("---")
    st.subheader('✅ :red[Nhập URL Youtube rồi nhấp OK]')
  
    URL = st.text_input("Nhập vào đây một URL YouTube hợp lệ:", key="url", label_visibility="hidden", placeholder="Nhập URL YouTube:")
    
    butUrl = st.button('🆗', on_click=save_and_clear)

    st.write("---")
    Tb_khi_ok_url = st.empty()
    if butUrl:
        URL = st.session_state.last_url
        if URL:
            with st.spinner("Đang lấy Id từ Url đã nhập..."):
                info = lay_info(URL)
                if info == None:
                    Tb_khi_ok_url.write(":red[Chưa nhập URL YT hợp lệ!]. Hãy nhập một Url Youtube hợp lệ.")
                    #os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    video_id = info['id']
                    title = info['title'] 
                    thoiluong = round(info['duration']/60,1)
                    #st.write(Thoiluong)
                    with Tb_khi_ok_url.container():
                        st.write('🔗: '+URL) 
                        st.write('🆔: '+video_id) 
                        st.write('🏷️: '+title) 
                        st.write('🕒minutes: ',thoiluong) 
                        st.write(':red[Đang lấy phụ đề...]') 
                    # xet phu de                    
                    subtitle_data = get_subtitle_urls(info)
                    # xet phu de truyen thong
                    if subtitle_data["automatic_captions"] != {}:
                        if subtitle_data["automatic_captions"]["en"]:
                            dangPdEn = subtitle_data["automatic_captions"]["en"]["ext"]
                            urlPdEn = subtitle_data["automatic_captions"]["en"]["url"]
                            ttLayPdEn = [dangPdEn, urlPdEn]
                            f = requests.get(ttLayPdEn[1])
                            if dangPdEn == "ttml":
                                ttml_content = f.text
                                #st.write(ttml_content)
                                json_subs = ttml_to_json(ttml_content)
                                subtitles = merge_by_sentence(json_subs)
                                #st.write(json_subs)🏷️ Label Emoji | Meaning, Copy And Paste
                                #bo >> trong subtitles
                                pattern = ">>" 
                                for item in subtitles:
                                    item['text'] = re.sub(pattern, "", item['text'])

                                with Tb_khi_ok_url.container():
                                    st.write('🔗: '+URL) 
                                    st.write('🆔: '+video_id) 
                                    st.write('🏷️: '+title) 
                                    st.write('🕒minutes: ',thoiluong) 
                                    st.write('✅:blue[Đã thành công và đang hiển thị video:]') 
                        else:
                            Tb_khi_ok_url.write("No en subtitles!")           
                    else:
                        subtitles = []
                        Tb_khi_ok_url.write("No subtitles!")
        else:
            Tb_khi_ok_url.write(":red[Chưa nhập URL YT !]. Hãy nhập một Url Youtube.")


#-----------Trang Chinh--------------------
if video_id and title and subtitles :
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
    background-image: linear-gradient(45deg, rgb(236, 236, 236), rgb(255,255,255)); 
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
    font-size: 1.2rem;
    height:9rem;
    color: darkgreen;
    }}
    #subdich{{
    text-align: left;
    color: darkblue;
    font-size: 1.4rem;
    height:9rem;
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
    .outiframe{{
    margin-bottom:100%;
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
    tieuDeTrangChinh.empty()
    aboutApp.empty()
    st.components.v1.html(html_code, height=800, scrolling=False)



# Nhập URL YouTube
#url = st.text_input("Nhập URL YouTube:", label_visibility="hidden", placeholder="Nhập URL YouTube:")
# https://www.youtube.com/watch?v=dQw4w9WgXcQ   # có phụ đề en
# https://www.youtube.com/watch?v=U6PoUg7jXsA   # có phụ đề en
# https://www.youtube.com/watch?v=HNueJboqgxg   # yt vietnam gay loi
#url = "https://www.youtube.com/watch?v=U6PoUg7jXsA"
#https://www.youtube.com/watch?v=Wvyk1Ti_NbY

# Nhập URL YouTube
#url = st.text_input("Nhập URL YouTube:", label_visibility="hidden", placeholder="Nhập URL YouTube:")

