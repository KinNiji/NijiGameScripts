import pyautogui
import win32api
import win32con
import win32com.client
import win32gui
import time
import json

from configparser import ConfigParser

from ocr import BaiduOCR
baidu_ocr = BaiduOCR()

parse = ConfigParser()
parse.read('../config.ini', encoding='utf-8')
# 自定义参数
WINDOW_TITLE = parse.get('default', 'WINDOW_TITLE')
your_client_id = parse.get('api', 'API_Key')
your_client_secret = parse.get('api', 'Secret_Key')
special_agent_user = [a for a in parse.get('strategy', 'special_agent_user').split(' ')]
INIT_ACCELERATE = bool(int(parse.get('strategy', 'INIT_ACCELERATE')))
ENABLED = [i - 1 for i in json.loads(parse.get('strategy', 'ENABLED'))]
ACCELERATE = bool(int(parse.get('strategy', 'ACCELERATE')))
CLICK_INTERVAL = float(parse.get('click', 'CLICK_INTERVAL'))
JUMP_INTERVAL = float(parse.get('click', 'JUMP_INTERVAL'))
LOAD_INTERVAL = float(parse.get('click', 'LOAD_INTERVAL'))

# 屏幕分辨率
# 获取屏幕分辨率
window_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
window_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
# 按键位置写死了相对位置省的烦
# 四个招募位
RECRUIT_1 = {'x': 512/1920, 'y': 442/1080}
RECRUIT_2 = {'x': 1408/1920, 'y': 442/1080}
RECRUIT_3 = {'x': 512/1920, 'y': 834/1080}
RECRUIT_4 = {'x': 1408/1920, 'y': 834/1080}
RECRUITS = [RECRUIT_1, RECRUIT_2, RECRUIT_3, RECRUIT_4]
# 四个招募位的加速
ACCELERATE_1 = {'x': 718/1920, 'y': 570/1080}
ACCELERATE_2 = {'x': 1614/1920, 'y': 570/1080}
ACCELERATE_3 = {'x': 718/1920, 'y': 960/1080}
ACCELERATE_4 = {'x': 1614/1920, 'y': 960/1080}
ACCELERATES = [ACCELERATE_1, ACCELERATE_2, ACCELERATE_3, ACCELERATE_4]
# 四个招募位的聘用
OFFER_1 = {'x': 512/1920, 'y': 576/1080}
OFFER_2 = {'x': 1408/1920, 'y': 576/1080}
OFFER_3 = {'x': 512/1920, 'y': 968/1080}
OFFER_4 = {'x': 1408/1920, 'y': 968/1080}
OFFERS = [OFFER_1, OFFER_2, OFFER_3, OFFER_4]

# 五个标签识别范围
TAG_RANGE = [585/1920, 541/1080, 1261/1920, 706/1080]
# 五个标签
TAG_1 = {'x': 684/1920, 'y': 574/1080}
TAG_2 = {'x': 924/1920, 'y': 574/1080}
TAG_3 = {'x': 1160/1920, 'y': 574/1080}
TAG_4 = {'x': 684/1920, 'y': 676/1080}
TAG_5 = {'x': 924/1920, 'y': 676/1080}
TAGS = [TAG_1, TAG_2, TAG_3, TAG_4, TAG_5]
# 刷新
REFRESH = {'x': 1424/1920, 'y': 608/1080}
# 加速确认、取消
PROMPT_CONFIRM = {'x': 1412/1920, 'y': 748/1080}
PROMPT_CANCEL = {'x': 472/1920, 'y': 748/1080}
# 加减时间
HOUR_UP = {'x': 690/1920, 'y': 244/1080}
MINUTE_UP = {'x': 928/1920, 'y': 244/1080}
HOUR_DOWN = {'x': 690/1920, 'y': 450/1080}
MINUTE_DOWN = {'x': 928/1920, 'y': 450/1080}
# 确认
CONFIRM = {'x': 1434/1920, 'y': 850/1080}
CANCEL = {'x': 1434/1920, 'y': 944/1080}
# 开包
SKIP = {'x': 1788/1920, 'y': 100/1080}
# 干员姓名识别范围
NAME_RANGE = [900/1920, 728/1080, 1350/1920, 836/1080]

CENTER = {'x': 960/1920, 'y': 540/1080}

LOCATE_CENTER = {'x': 960/1920, 'y': 660/1080}


def get_window():  # 定位窗口
    # 屏幕分辨率
    print('屏幕分辨率：{} * {}'.format(window_x, window_y))
    TAG_RANGE[0] *= window_x
    TAG_RANGE[1] *= window_y
    TAG_RANGE[2] *= window_x
    TAG_RANGE[3] *= window_y
    NAME_RANGE[0] *= window_x
    NAME_RANGE[1] *= window_y
    NAME_RANGE[2] *= window_x
    NAME_RANGE[3] *= window_y
    LOCATE_CENTER['x'] *= window_x
    LOCATE_CENTER['y'] *= window_y

    window = win32gui.FindWindow(None, WINDOW_TITLE)
    if not window:
        exit('获取窗口失败，请检查窗口名是否正确！')
    else:
        print('获取窗口成功！')
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    # 置顶窗口
    win32gui.SetForegroundWindow(window)
    # 窗口最大化
    win32gui.ShowWindow(window, win32con.SW_MAXIMIZE)
    print()


def interval(mode):
    if mode == 'click':
        time.sleep(CLICK_INTERVAL)
    elif mode == 'jump':
        time.sleep(JUMP_INTERVAL)
    elif mode == 'load':
        time.sleep(LOAD_INTERVAL)


def click(position, mode='click', clicks=1):  # 点击事件封装
    pyautogui.click(int(position['x'] * window_x), int(position['y'] * window_y), clicks=clicks)
    interval(mode)


def get_index(x, y):
    if x < LOCATE_CENTER['x'] and y > LOCATE_CENTER['y']:
        return 1
    elif x > LOCATE_CENTER['x'] and y > LOCATE_CENTER['y']:
        return 2
    elif x < LOCATE_CENTER['x'] and y < LOCATE_CENTER['y']:
        return 3
    elif x > LOCATE_CENTER['x'] and y < LOCATE_CENTER['y']:
        return 4
    else:
        return 0


def locate(png_path, mode):  # 定位事件封装
    flag = False
    try:
        x, y = pyautogui.locateCenterOnScreen(png_path, grayscale=False, confidence=0.8)
        pyautogui.click(x, y)
        interval(mode)
        flag = get_index(x, y)
    except Exception as e:
        raise e
    finally:
        return flag


def start(index):  # 开始招募
    recruit = RECRUITS[index]
    click(recruit, 'jump')


def identify_tags():  # 识别tag
    screenshot = pyautogui.screenshot()
    input_list = baidu_ocr.res2tags(baidu_ocr.ocr(screenshot.crop(tuple(TAG_RANGE))))
    return input_list


def choose_tags(tags_index):  # 选择tag
    for tag_index in tags_index:
        tag = TAGS[tag_index]
        click(tag)


def refresh():  # 刷新tag
    if locate('../assets/pic/refresh.png', 'jump'):
        click(PROMPT_CONFIRM, 'load')
        return True
    return False


def set_time(mode):  # 设置时间
    if mode == 'normal':
        click(HOUR_DOWN)
    elif mode == 'short':
        click(HOUR_UP, clicks=3)
        click(MINUTE_DOWN)


def confirm():  # 确认招募
    click(CONFIRM, 'load')


def cancel():  # 取消招募
    click(CANCEL, 'jump')


def accelerate(index):  # 立即招募
    recruit = ACCELERATES[index]
    click(recruit, 'jump')
    click(PROMPT_CONFIRM, 'load')


def hire(index):  # 聘用
    if index is not None:
        offer = OFFERS[index]
        click(offer, 'load')
    click(SKIP)
    time.sleep(0.4)
    name = identify_name()
    time.sleep(2)
    click(CENTER, 'jump')
    if index is not None:
        print('第 {} 招募位： {}'.format(index + 1, name))
    return name


def identify_name():  # 识别干员
    screenshot = pyautogui.screenshot()
    screenshot.save('../output/{}.png'.format(time.strftime('%Y%m%d_%H%M%S', time.localtime())))
    img = screenshot.crop(tuple(NAME_RANGE))
    output = baidu_ocr.res2name(baidu_ocr.ocr(img))
    return output


if __name__ == '__main__':
    print(locate('../assets/pic/hire.png', 'jump'))
