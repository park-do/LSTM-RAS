
from html2text import html2text
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd

driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
id=''
pw=''



page = 1
menuid = ''

jasoseoList = []
categoryList = []

# ToDo
# 1. td_apply_subject의 td를 찾아서 그 안의 a태그 찾기
    # 2. a태그들로 들어가서 자소서 내용 긁기
# 3. 다음 자소서로 넘어가기
# 4. 끝가지 갔으면 다음 페이지로

# a태그 긁어서 리스트에 넣기
# endPage = 26884
endPage = 26884
while page <= endPage:  # 1.
    url = 'http://www.saramin.co.kr/zf_user/public-recruit/coverletter?real_seq='+str(page)
    driver.get(url)
    # driver.switch_to.frame('cafe_main')
    try:
        soup = bs(driver.page_source, 'html.parser')
    except:
        print(str(page)+"가 비어있다. 다음으로 이동.")
        driver.switch_to.alert.accept()
        page += 1
        continue
    span = soup.find('span', {'class': 'tag_apply'})
    divs = soup.find_all('div', {'class': 'box_ty3'})

    if span is None:
        category = "None"
    else:
        category = span.get_text()
    # 지원분야 | XXX <- 지원분야 쪽이 필요가 없으므로 삭제한다.
    category = category[category.find('| ')+2:]

    for div in divs:
        categoryList.append(category)
        divtext = div.get_text()
        # divtext에서 두번째 엔터 부터, 필요없는 '첨삭 결과' 또는 '작성 포인트' 등의 전까지 떼버린다.
        secondnewline = divtext.find('\n', 2) + 1
        divtext = divtext[secondnewline:]
        checkingstr = ['첨삭 결과', '작성 포인트', '  글자수 ', '\n글자수']

        for check in checkingstr:
            if divtext.find(check) >= 0:
                divtext = divtext[:divtext.find(check) - 1]

        divtext = divtext.strip()  # trim

        jasoseoList.append(divtext)
        print("category : " + category)
        print("jasoseo  : " + divtext)

    #tdList = div.find_all("td", attrs={'class': 'td_apply_subject'})

    # URL 긁어오기
    # for td in tdList:
    #     a = td.find("a")  # a 가져오기
    #     # title = tdList[1].a.string  # 제목 가져오기
    #     # linkList.append('http://cafe.naver.com/' + tdList[1].find("a")["href"])
    #     print(a["href"])
    #     jasoseoList.append(a["href"])
    print(page, "/", endPage, "페이지 URL 긁기 완료")
    page = page + 1

df = pd .DataFrame(data={"category": categoryList, "jss": jasoseoList})
df.to_csv('자소서Data.csv')

# i = 0
# length = len(linkList)
# while i < length:
#     try:
#         url = linkList[i]
#         driver.get(url)
#         driver.switch_to_frame('cafe_main')
#         soup = bs(driver.page_source, 'html.parser')
#
#         soup = soup.find('div','list-blog border-sub') #글 영역만 가져오기
#         title = soup.find('span', 'b m-tcol-c').string
#         date = soup.find('td', 'm-tcol-c date').string
#         name = soup.find('td', 'p-nick').string
#
#         # 내용 다듬기 ######################################################################################################
#         contentTable = soup.find('div', 'tbody m-tcol-c')
#         content_tmp = contentTable.find_all('p')
#         content = str(content_tmp)
#
#         text = html2text(content) # html to text 사용
#         text = text.replace('[', '').replace(']', '').replace(',', '').replace('\n', '')
#
#         # 게시판 공지 삭제
#         if text.find('★ 자유게시판 글'):
#             text = text.replace(content[text.find('★ 자유게시판 글'):text.find('허위사실 게시글 금지') + 11], '')
#         if text.find('★ 나눔게시판 글'):
#             text = text.replace(content[text.find('★ 나눔게시판 글'):text.find('말머리로 나눔완료 설정 필수') + 15], '')
#         if text.find('★ 매장 MD 제보'):
#             text = text.replace(content[text.find('★ 매장 MD 제보'):text.find('판매 유도 불가') + 8], '')
#         if text.find('★ 등업했어요'):
#             text = text.replace(content[text.find('★ 등업했어요'):text.find('무통보 삭제') + 6], '')
#
#         # 내용 다듬기 ######################################################################################################
#
#
#         # 리스트에 담기
#         postList.append({'content': text, 'date': date, 'name': name,'title': title})
#         print(i + 1, "번째 글 크롤링...", float((i/length)*100), "% 완료")
#         i = i + 1
#     except:
#         # 리스트에 담기
#         postList.append({'content': '', 'date': '', 'name': '', 'title': ''})
#         print(i + 1, "번째 글 크롤링...", float((i / length) * 100), "% 완료")
#         i = i + 1
#         pass
#
# cafe_df = pd.DataFrame(postList)
# print("출력 준비")
# writer = pd.ExcelWriter('C:/Users/이동우/Downloads/MD01_50.xlsx')
# cafe_df.to_excel(writer,'Sheet1')
# writer.save()
# print("끝")






#############################################################################################################################
# 필요없는 태그 지우기
# while content.find('<img') != -1 or content.find('<span ') != -1 or content.find('<p ') != -1 \
#         or content.find('<font ') != -1:
#     if content.find('<img') != -1:  # 이미지 링크 지우기
#         content = content.replace(content[content.find('<img'):content.find('px;"/>') + 3], '')
#
#     if content.find('<span ') != -1:  # 이미지 링크 지우기
#         content = content.replace(content[content.find('<span '):content.find(';">') + 3], '')
#
#     if content.find('<p ') != -1:  # 이미지 링크 지우기
#         content = content.replace(content[content.find('<p '):content.find(';">') + 3], '')
#
#     if content.find('<font ') != -1:  # 이미지 링크 지우기
#         content = content.replace(content[content.find('<font '):content.find(';">') + 3], '')

# 필요없는 문자 지우기
# content = content.replace('<br/>', ' ')
# content = content.replace('<p>', ' ')
# content = content.replace('</p>', '')
# content = content.replace('<span>', '')
# content = content.replace('</span>', '')
# content = content.replace('<strong>', '')
# content = content.replace('</strong>', '')
# content = content.replace('</font>', '')
# content = content.replace('"/>', '')
# content = content.replace(',', '')
# content = content.replace('[', '')
# content = content.replace(']', '')
#############################################################################################################################