from time import sleep
import datetime as dt
import warnings
#import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options


warnings.simplefilter("ignore",DeprecationWarning) #DeprecationWarningをターミナルで非表示

#引数：無。戻り値：PandAの初期画面を開いたbrowser。
def new_browser(isVisible=False):
    #ブラウザはchrome。demo用にブラウザは表示。
    if isVisible : 
        browser = webdriver.Chrome()
        browser.get("https://panda.ecs.kyoto-u.ac.jp/portal/")
        return browser
    else :
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Chrome(options=options)
        browser.get("https://panda.ecs.kyoto-u.ac.jp/portal/")
        return browser

#引数：browser,ユーザーID,パスワード。戻り値：loginに成功した場合True。
def log_in(abrowser,userid,password):
    lgin = abrowser.find_element_by_id("loginLink1")
    lgin.click()
    sleep(1)
    
    beforeUrl = abrowser.current_url
    
    useridBox = abrowser.find_element_by_id("username")
    useridBox.send_keys(userid)
    passwordBox = abrowser.find_element_by_id("password")
    passwordBox.send_keys(password)
    sleep(1)

    login = abrowser.find_element_by_name("submit")
    login.click()
    sleep(1)
    
    afterUrl = abrowser.current_url
    browser = abrowser

    return (not afterUrl.startswith("https://cas.ecs.kyoto-u.ac.jp/cas/login")) #loginに成功した場合URLが変わる→URLが一致しないという条件式はTrue。

def log_in_check(userId,password) :
    browser = new_browser()
    ret = log_in(browser,userId,password)
    browser.quit()
    return ret

def go_to_site_setup(abrowser) :
    try :
        dashboard = abrowser.find_element_by_link_text("サイトセットアップ")
        dashboard.click()
        sleep(1)

        #iframe = abrowser.find_element_by_id(iframeId)
        #(iframeのidがuserに固有かもしれない。)
        #abrowser.switch_to_frame(iframe)
        iframe = abrowser.find_element_by_class_name("portletMainIframe")
        abrowser.switch_to_frame(iframe)
       
        select_element = abrowser.find_element_by_id("selectPageSize")
        select_object = Select(select_element)
        select_object.select_by_visible_text("表示 1000 件ずつ")
        sleep(2)

        browser = abrowser

        return True

    except Exception as e: 
        print("COULD NOT GO TO SITE SETUP")
        abrowser.quit()
        exit
        return False 


#引数：browser,講義名。戻り値：成功した場合True。
#loginからにしか対応していません！！課題を提出した後に戻る関数ではありません！！
#講義名は一意に決まる名前にしてください。
#戻り値に特に意味はありません。「ドラフトを保存」ができているということは講義が必ず存在するからです。
def go_to_worksite(abrowser,worksiteName):
    try :
        go_to_site_setup(abrowser)

        #講義を選択。
        worksiteButton = abrowser.find_element_by_partial_link_text(worksiteName)
        worksiteUrl = worksiteButton.get_attribute("href")
        #worksiteButton.click() #自分用なので、テスト/クイズには対応していません。
        abrowser.get(worksiteUrl)
        sleep(1)

        broser = abrowser

        return True

    except Exception as e: 
        print("COULD NOT GO TO WORKSITE")
        abrowser.quit()
        exit
        return False 

#引数：browser,課題提出先の名前（提出する課題ファイルの名前ではない）。戻り値：成功した場合True。
#gotoWorksiteからにしか対応していません！！課題を提出した後にAssignmentに戻る関数ではありません！！
#課題提出先の名前は一意に決まる名前にしてください。
def go_to_assignment(abrowser,assignmentName):
    #左のバーから"課題"を選択。
    assignmentTabButton = abrowser.find_element_by_partial_link_text("課題")
    assignmentTabUrl = assignmentTabButton.get_attribute("href")
    #assignmentTabButton.click()
    abrowser.get(assignmentTabUrl)
    sleep(1)
    
    iframe = abrowser.find_element_by_class_name("portletMainIframe")
    abrowser.switch_to_frame(iframe)
    #tt = abrowser.title
    #assignment = abrowser.find_element_by_partial_link_text("課題")
    
    try :
        table = abrowser.find_element_by_xpath('/html/body/div/form/table')
        assignmentButton = table.find_element_by_partial_link_text(assignmentName)
        assignmentUrl = assignmentButton.get_attribute("href")
        #assignmentButton.click()
        abrowser.get(assignmentUrl)
        sleep(1)

        browser = abrowser
        
        return True
    
    except Exception as e: 
        print("COULD NOT GO TO ASSIGNMENT")
        abrowser.quit()
        exit
        return False 


#引数：browser。戻り値：成功した場合True。
#課題の提出ボタンを押します。何らかの理由で提出できなかった場合、TotalTimeまで提出を試みます。
def submit(abrowser):
    count = 0
    sleepTime = 0.5
    totalTime = 1

    beforeUrl = afterUrl = abrowser.current_url

    while (beforeUrl == afterUrl and count < totalTime/sleepTime) :
        click_submit_button(abrowser)
        sleep(sleepTime)
        afterUrl = abrowser.current_url
        count += 1

    return beforeUrl != afterUrl #提出に成功した場合URLが変わる→URLが一致しないという条件式はTrue。

def click_submit_button(abrowser):
    try :
        submitButton = abrowser.find_element_by_id("post")
        submitButton.click()
        return True

    except Exception as e :
        return False

#引数：userId,password・戻り値：課題リスト。
#①PandAをクロールし、締切まで一定期間にある未開始の課題を自動で提出します。提出するだけなので、「ドラフトを保存」を事前にする必要があります。
#②クロールの過程で、締切まで一定期間にある未開始の課題をToDoリストに追加します。このToDoリストが戻り値になります。ToDoリストは各要素が「課題名」「締切」の2要素からなる2次元配列です。
def crawl_panda(userId,password):
    browser = new_browser()
    
    if log_in(browser,userId,password) :
        print("log-in succeeded")
    else :
        browser.quit()
        exit

    go_to_site_setup(browser)

    to_do_list = []
    worksite_url_and_worksite_name_list = [] #[URL,講義名]のリスト。

    for worksiteButton in browser.find_elements_by_partial_link_text("2020後期") : #テスト中の負荷削減のため、この文字列にしています。
        worksite_url_and_worksite_name_list.append([worksiteButton.get_attribute("href"),worksiteButton.text])

    for worksite_url_and_worksite_name in worksite_url_and_worksite_name_list :
        worksite_url = worksite_url_and_worksite_name[0]
        worksite_name = worksite_url_and_worksite_name[1]
        
        #各講義の課題タブを開きます。
        browser.get(worksite_url)
        assignmentTabButton = browser.find_element_by_partial_link_text("課題")
        assignmentTabUrl = assignmentTabButton.get_attribute("href")
        browser.get(assignmentTabUrl)
        sleep(1)

        #各課題のURLを取得します。
        #課題はデフォルトが200件表示なので、1000件表示する必要は無いと思っています。
        iframe = browser.find_element_by_class_name("portletMainIframe")
        browser.switch_to_frame(iframe)

        try :
            table = browser.find_element_by_xpath('/html/body/div/form/table')
            assignmentUrl_list = [] 
            tr_list = table.find_elements_by_tag_name("tr")

            for tr in tr_list[1:] :
                td_list = tr.find_elements_by_tag_name("td")

                assignmentButton = (td_list[1].find_elements_by_tag_name("a"))[0]
                status = td_list[2].text
                deadline = dt.datetime.strptime(td_list[4].text+":00","%Y/%m/%d %H:%M:%S")
                
                now = dt.datetime.now()
                submitDeadline = now + dt.timedelta(hours=1) #テストののため、この値にしています。
                solveDeadline = now + dt.timedelta(weeks=2) #テストののため、この値にしています。

                if status == "未開始" and now <= deadline <= submitDeadline :
                    assignmentUrl_list.append(assignmentButton.get_attribute("href"))
                if status == "未開始" and now <= deadline <= solveDeadline : 
                    to_do_list.append([worksite_name,assignmentButton.text,td_list[4].text])
            
            for assignmentUrl in assignmentUrl_list : 
                browser.get(assignmentUrl)
                sleep(2)
                submit(browser)

        #課題が存在しない場合、未提出の課題が存在しない場合
        except Exception as e :
            continue

    browser.quit()

    return to_do_list

#===============================================================================
