import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

base_Url = 'https://www.talesrunner.com.hk'
webhook_links = ['']

#create requirements.txt
#pipreqs --force --encoding UTF-8

def remove_new_line_symbol(lines):
    removedLines = []
    for line in lines:
        removedLines.append(line.rstrip('\r\n\t').rstrip())
    _str = ''
    for rl in removedLines:
        _str += rl
    return _str

def remove_new_line_symbol2(lines):
    removedLines = []
    for line in lines:
        removedLines.append(line.rstrip('\r\n\t'))
    _str = ''
    for rl in removedLines:
        _str += rl
    return _str

def getNews_html():
    r = requests.get('https://www.talesrunner.com.hk/notice/notice.php?type=system')
    csoup = BeautifulSoup(r.text, 'html.parser')
    return csoup

def getpatchNews_html():
    r = requests.get('https://www.talesrunner.com.hk/notice/notice.php?type=patch')
    csoup = BeautifulSoup(r.text, 'html.parser')
    return csoup

def get_trmsg_news():
    
    # File Input
    f = open('trmsg_titles.txt','r+', encoding="utf-8")
    readTitles = f.readlines()
    writeTitles = readTitles

    # Crawler
    r = requests.get("https://www.talesrunner.com.hk/news/MMXIII_news.html")
    r.encoding = 'big5'#抓官網的meta標籤看編碼
    soup = BeautifulSoup(r.text, 'html.parser')

    # Crawler get News and patchNews
    newsSoup = getNews_html()
    patchSoup = getpatchNews_html()

    boardData = soup.find(id="allNoticeContainer")
    boardItems = boardData.find_all("tr")
    isUpdated = False
    for div in reversed(boardItems):
        #link type
        dtObjects = div.find_all('td')
        if len(dtObjects) < 3:
            continue
        if dtObjects[1].find("span") == None:
            continue
        event_link = dtObjects[0].img['src']
        event_type = '最新消息'
        if "item_02" in event_link:
            event_type = '更新情報'
        if "item_03" in event_link:
            event_type = '活動消息'
        title = dtObjects[1].a
        board_title = str(dtObjects[1].span.get_text())
        if "停權" in board_title:
            continue
        board_date = dtObjects[2].get_text()
        board_read = False
        if event_type == '最新消息':
            tsoup = newsSoup
            board_read = True
        elif event_type == '更新情報':
            tsoup = patchSoup
            board_read = True
        board_content = ""
        if (board_read):
            csoup = tsoup
            searchOtherContent = False
            Content = ""
            findPointer = csoup.find_all('td', 'pointer')
            for line in findPointer:
                titleCheck = line.find_previous('tr')
                for titleC in titleCheck:
                    afterboardTitle = remove_new_line_symbol(board_title)
                    afterTitleC = remove_new_line_symbol(titleC.text)
                    if afterboardTitle in afterTitleC:
                        searchOtherContent = True
                        break
                if searchOtherContent:
                    tempContent = line.find_parent('tr').find_parent('tr').find_next_siblings('tr')
                    lineCount = 0
                    for addC in tempContent:
                        if lineCount > 3:
                            break
                        lineCount += 1
                        Content += addC.text
                    break
            board_content = Content
        # tag color
        tag_color = 5028631
        if event_type == '活動消息':
            tag_color = 561039
        elif event_type == '更新情報':
            tag_color = 16734003

        current_title = board_title
        find_news = False
        for line in readTitles:
            temp_title = remove_new_line_symbol2(current_title)
            temp_line = remove_new_line_symbol2(line)
            if temp_title in temp_line:
                if len(temp_title) == len(temp_line):
                    find_news = True
                    break
        if find_news == False:
            temp_title = remove_new_line_symbol2(current_title)
            writeTitles.insert(0, temp_title + '\n')
            current_link = title['href']

            content = title['onmouseover']
            content = content.replace('changeBanner("', '')
            content = content.replace('");', '')

            embed = DiscordEmbed()
            embed.set_author(name='跑online官網公告轉送', url=current_link,
                            icon_url='https://www.talesrunner.com.hk/images/MMXIII/index/tr_logo.png')
            embed.title = event_type + '：' + current_title
            embed.description = board_content[:600]
            embed.set_thumbnail(url='https://www.talesrunner.com.hk/news' + '/' + event_link)
            embed.set_image(url=content)
            embed.add_embed_field(name='官網連結', value=current_link)
            embed.color = tag_color
            
            for link in webhook_links:
                new_embed = embed
                webhook = DiscordWebhook(url=link)
                webhook.add_embed(new_embed)
                webhook.execute()
            print("已更新：" + current_title)
            isUpdated = True
        else:
            print("未更新：" + current_title)
        
        #count -= 1
    
    while len(writeTitles) > 20:
        writeTitles.pop()

    if isUpdated:
        print("已儲存檔案")
        f.seek(0)
        f.truncate(0)
        f.writelines(writeTitles)
    f.close()


if __name__ == '__main__':
    get_trmsg_news()
