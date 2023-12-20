# https://tien89talkenvi-talk-envi-streamlit-app-ojqt7j.streamlit.app/
import streamlit as st
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import time
import base64

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):

    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls and len(href.strip()) > 14:
                #print(f"{GRAY}[!] External link: {href}{RESET}")
                external_urls.add(href)
            continue
        #print(f"{GREEN}[*] Internal link: {href}{RESET}")
        if len(href.strip()) > 14:
            urls.add(href)
            internal_urls.add(href)
    return urls


def crawl(url, max_urls):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    time.sleep(0.01)
    my_bar.progress(percent_complete + total_urls_visited/(max_urls+2))


    #print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    

    links = get_all_website_links(url)


    for i, link in enumerate(links):

        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)

def get_binary_file_downloader_link(file_path, link_text):
    with open(file_path, 'rb') as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{file_path}">{link_text}</a>'
    return href


################################################################################################

if __name__ == "__main__":
    st.title("Lấy website links để tìm hiểu!")
    #st.subheader("(Chỉ để thử lập trình)")

    
    so_url_max_muon=st.radio("Giới hạn cấp độ lấy :",["1", "2","3","10","20","30"],index=0,horizontal=True)
    so_url_max=int(so_url_max_muon)

    st.markdown("<h5 style='color: red;'># Nhập URL của WEB muốn tìm link trong đó vào khung dưới đây (ex.<span style='color:blue;'> https://nld.com.vn </span>) rồi Enter</h5> ", unsafe_allow_html=True)

    url_nhapvao = st.text_input('chon',label_visibility = "hidden")

    if url_nhapvao != '':

        url = url_nhapvao
        max_urls = so_url_max

        # domain name of the URL without the protocol
        domain_name = urlparse(url_nhapvao).netloc

        my_bar = st.progress(0)
        percent_complete=0.00

        crawl(url, max_urls=max_urls)

        #print("[+] Total Internal links:", len(internal_urls))
        #print("[+] Total External links:", len(external_urls))
        #print("[+] Total URLs:", len(external_urls) + len(internal_urls))
        #print("[+] Total crawled URLs:", max_urls)
        time.sleep(1)
        my_bar.empty()

        st.write("[+] Tổng số links ngoài:", len(external_urls))
        st.write("[+] Tổng số links trong:", len(internal_urls))
        st.write("[+] Tổng số URLs:", len(external_urls) + len(internal_urls))
        st.write("[+] Cấp độ lấy :", max_urls)

        # save the internal links to a file
        lsbox_in=[]
        with open(f"{domain_name}_internal_links.txt", "w") as f:
            for internal_link in internal_urls:
                if len(internal_link.strip()) > 14:
                    print(internal_link.strip(), file=f)
                    lsbox_in.append(internal_link.strip())

        lsbox_out=[]
        # save the external links to a file
        with open(f"{domain_name}_external_links.txt", "w") as ff:
            for external_link in external_urls:
                if len(external_link.strip()) > 14:
                    print(external_link.strip(), file=ff)
                    lsbox_out.append(external_link.strip())
        
        st.write("[-] Các links External đã được ghi trong file :", domain_name+"_external_links.txt")
        st.write("[-] Các links Internal đã được ghi trong file :", domain_name+"_internal_links.txt")
        st.markdown(get_binary_file_downloader_link(domain_name+"_external_links.txt", "Nhấp để tải về file "+domain_name+"_external_links.txt"), unsafe_allow_html=True)
        st.markdown(get_binary_file_downloader_link(domain_name+"_internal_links.txt", "Nhấp để tải về file "+domain_name+"_internal_links.txt"), unsafe_allow_html=True)
        
        st.write('---')
        st.markdown("<h5 style='color: red;'># Chọn một url để xem trang web tương ứng</h5> ", unsafe_allow_html=True)

        radio_chon=st.radio(':red[Chọn một url đê xem trang web tương ứng :]',["external links","internal links"],index=0,horizontal=True,label_visibility ="hidden")
        
        if radio_chon=="external link":
            url_option = st.selectbox(':red[Chọn một url đê xem trang web tương ứng :]',lsbox_out,label_visibility ="hidden")
        else:
            url_option = st.selectbox(':red[Chọn một url đê xem trang web tương ứng :]',lsbox_in,label_visibility ="hidden")
        st.write(url_option)
