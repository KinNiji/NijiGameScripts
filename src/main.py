import sys
import random

from collections import Counter

from automatic import *

# Debug参数
DEBUG = False
DEBUG_INPUT = ["近卫干员", "狙击干员", "重装干员", "辅助干员", "支援"]


class Logger(object):
    def __init__(self,
                 filename='../log/{}.txt'.format(time.strftime('%Y%m%d_%H%M%S', time.localtime())), stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


sys.stdout = Logger(stream=sys.stdout)

with open('../assets/agent.json', 'r', encoding='utf-8') as f:
    agents_raw = json.load(f)
    agents_dict = {}
    po_agents_list = []
    for agent_raw in agents_raw:
        name = agent_raw['name']
        agents_dict[name] = agent_raw
        if agent_raw['star'] == '6':
            agents_dict[name]['tags'].append("高级资深干员")
            agents_dict[name]['all_tags'].append("高级资深干员")
        elif agent_raw['star'] == '5':
            agents_dict[name]['tags'].append("资深干员")
            agents_dict[name]['all_tags'].append("资深干员")
        elif agent_raw['star'] == '1':
            agents_dict[name]['tags'].append("支援机械")
            agents_dict[name]['all_tags'].append("支援机械")
        if agent_raw['public_only'] == 'True':
            po_agents_list.append(agent_raw['name'])

LEGAL_INPUTS = ["近战位", "远程位",
                "支援机械", "新手", "资深干员", "高级资深干员",
                "先锋干员", "近卫干员", "狙击干员", "重装干员", "医疗干员", "辅助干员", "术师干员", "特种干员",
                "治疗", "支援", "输出", "群攻", "减速", "生存", "防护", "削弱", "位移", "控场", "爆发", "召唤", "快速复活", "费用回复"]


def check():
    print('4月14日更新版本，新增干员：风笛、慑砂、宴。\n')
    print('以下为目前所有能通过公招获得的干员：', end='')
    star_count = 7
    for an_agent in agents_dict.values():
        if int(an_agent['star']) < star_count:
            star_count -= 1
            print()
            print('★' * star_count)
            print(an_agent['name'], end='')
            continue
        print(', ' + an_agent['name'], end='')
    print('\n\n公招限定的干员', end='')
    for an_agent in po_agents_list:
        print(', ' + an_agent, end='')
    print('\n\n未满潜的干员', end='')
    for an_agent in special_agent_user:
        print(', ' + an_agent, end='')
    rounds = input('\n\n输入招募轮数：')
    print()
    try:
        return int(rounds)
    except Exception as e:
        exit('[Error] {}'.format(str(e)))


def find():
    # tag识别，计数器超过2停止
    def identify(n):
        if n > 2:
            exit('[Error] 尝试识别次数过多，脚本停止。')
        identify_result = identify_tags()
        print('识别结果：', identify_result)
        # 输入检测
        for an_input in identify_result:
            if an_input not in LEGAL_INPUTS:
                print('tag”{}“不合法，尝试重新识别。'.format(an_input))
                identify_result = identify(n+1)
        return identify_result

    tag_list = DEBUG_INPUT if DEBUG else identify(1)

    # 初始化查找，每个单独的tag找到对应的结果
    result_group = {}  # 初始化查找结果
    for a_tag in tag_list:
        result = []
        for agent in agents_raw:
            if a_tag in agent['all_tags']:
                result.append(agent['name'])
        result_group[a_tag] = result

    combined_result_group = []  # 将初始化结果取交集，筛选留下所有可能结果

    # 遍历tag的所有组合（dfs）
    def dfs(tags: list, nonius: int, sub_tags: list):
        if len(sub_tags) < len(tags) and len(sub_tags) <= 5:
            for i in range(nonius, len(tags)):
                sub_tags.append(tags[i])
                filtered_result = filtrate(sub_tags, combine(sub_tags))

                if filtered_result:
                    if DEBUG:
                        print(sub_tags, filtered_result, '\n')
                    combined_result_group.append(
                        {'tags': sub_tags.copy(),
                         'result': filtered_result,
                         'score': score(filtered_result) + len(sub_tags) / 10}
                    )
                    dfs(tags, i + 1, sub_tags)
                sub_tags.remove(sub_tags[len(sub_tags) - 1])

    # 合并查找结果
    def combine(sub_tags):
        combined_result = set(result_group[sub_tags[0]])
        for sub_tag in sub_tags:
            combined_result = combined_result & set(result_group[sub_tag])
        return list(combined_result)

    # 过滤结果
    def filtrate(sub_tags, combined_result: list):
        # 干员分类
        x6_agents = []
        x5_agents = []
        x4_agents = []
        x3_agents = []
        x2_agents = []
        x1_agents = []
        x5_special_agents = []
        x4_special_agents = []
        x3_special_agents = []
        x2_special_agents = []
        x1_special_agents = []
        for an_agent in combined_result:
            star = agents_dict[an_agent]['star']
            if star == '6':
                x6_agents.append(an_agent)
            elif star == '5':
                x5_agents.append(an_agent)
                if an_agent in special_agent_user:
                    x5_special_agents.append(an_agent)
            elif star == '4':
                x4_agents.append(an_agent)
                if an_agent in special_agent_user:
                    x4_special_agents.append(an_agent)
            elif star == '3':
                x3_agents.append(an_agent)
                if an_agent in special_agent_user:
                    x3_special_agents.append(an_agent)
            elif star == '2':
                x2_agents.append(an_agent)
                if an_agent in special_agent_user:
                    x2_special_agents.append(an_agent)
            elif star == '1':
                x1_agents.append(an_agent)
                if an_agent in special_agent_user:
                    x1_special_agents.append(an_agent)

        filtered_result_group = {}
        # 最差结果
        if x3_special_agents or x4_special_agents or x5_special_agents:
            filtered_result_group['chance'] = x3_special_agents + x4_special_agents + x5_special_agents

        # 高资过滤
        if '高级资深干员' in sub_tags:
            if x6_agents:
                filtered_result_group['x6'] = x6_agents

        # 资深过滤
        if '资深干员' in sub_tags:
            if x5_agents:
                filtered_result_group['x5'] = x5_agents
                if x5_special_agents:
                    filtered_result_group['x5_special'] = x5_special_agents

        # 星级过滤
        for x3_special_agent in x3_special_agents:
            x3_agents.remove(x3_special_agent)
        for x2_special_agent in x2_special_agents:
            x2_agents.remove(x2_special_agent)
        for x1_special_agent in x1_special_agents:
            x1_agents.remove(x1_special_agent)

        if not x3_agents and not x2_agents:
            if x4_agents:
                filtered_result_group['x4'] = x4_agents
                if x4_special_agents:
                    filtered_result_group['x4_special'] = x4_special_agents
            else:
                if x5_agents:
                    filtered_result_group['x5'] = x5_agents
                    if x5_special_agents:
                        filtered_result_group['x5_special'] = x5_special_agents
            if x3_special_agents:
                filtered_result_group['x3_special'] = x3_special_agents
            if x2_special_agents and '新手' in sub_tags:
                filtered_result_group['x2_special'] = x2_special_agents
            if x1_special_agents and '支援机械' in sub_tags:
                filtered_result_group['x1_special'] = x1_special_agents

        if DEBUG and filtered_result_group:
            print('x6_agents', x6_agents)
            print('x5_agents', x5_agents)
            print('x4_agents', x4_agents)
            print('x3_agents', x3_agents)
            print('x2_agents', x2_agents)
            print('x1_agents', x1_agents)
            print('x5_special_agents', x5_special_agents)
            print('x4_special_agents', x4_special_agents)
            print('x3_special_agents', x3_special_agents)
            print('x2_special_agents', x2_special_agents)
            print('x1_special_agents', x1_special_agents)

        return filtered_result_group

    # 结果评分
    # x6 > x5_special > x5 only > x1_special > x4_special > x4 > x3_special > x2_special > chance > none
    def score(filtered_result: dict):
        cate = list(filtered_result.keys())
        if 'x6' in cate:
            return 1
        elif 'x5_special' in cate:
            return 2
        elif 'x5' in cate and 'x4' not in cate and 'x4_special' not in cate:
            return 3
        elif 'x1_special' in cate:
            return 4
        elif 'x4_special' in cate:
            return 5
        elif 'x4' in cate:
            return 6
        elif 'x3_special' in cate:
            return 7
        elif 'x2_special' in cate:
            return 8
        elif 'chance' in cate:
            return 9
        else:
            return 99

    dfs(list(result_group.keys()), 0, [])

    # 输出
    combined_result_group = sorted(combined_result_group, key=lambda crg: crg['score'])
    return tag_list, combined_result_group


def init_round():
    while True:
        flag = locate('../assets/pic/accelerate.png', 'load')
        if flag and INIT_ACCELERATE:
            click(PROMPT_CONFIRM, 'jump')
        elif flag and not INIT_ACCELERATE:
            exit('[Error] 存在可加速招募位，且未允许加速。如需跳过该招募位，请修改配置禁用该招募位。')
        else:
            break
    while True:
        flag = locate('../assets/pic/hire.png', 'load')
        if flag:
            output_list.append(hire(None))
        else:
            break


def choose_round():
    i = 0
    while i < len(ENABLED):
        index = ENABLED[i]
        print('第 {} 招募位：'.format(index + 1))

        start(index)
        identify_list, result_list = find()
        if result_list:
            print('推荐组合：')
            score_list = []
            min_score = 100
            for r in result_list:
                score_list.append(r['score'])
                print(r['score'], r['tags'], r['result'])
                min_score = result_list[0]['score']
            min_count = Counter(score_list)

            if min_score < 2:
                DISABLED.append(index)
                print('选择组合： 保留\n')
                cancel()
                continue
            elif 2 <= min_score < 10:
                if min_score >= 9 and ACCELERATE:
                    flag = refresh()
                    if flag:
                        print('选择组合： 刷新\n')
                        cancel()
                        continue

                # 如果有多个同分结果，就随机选一个
                rand = random.randint(1, min_count[min_score])
                tags_index = []
                for tag in result_list[rand - 1]['tags']:
                    tags_index.append(identify_list.index(tag))

                choose_tags(tags_index)
                print('选择组合：', result_list[rand - 1]['tags'])
                set_time('short' if int(min_score) == 4 or int(min_score) == 8 else 'normal')
        else:
            print('推荐组合： 无')
            flag = refresh()
            if flag:
                print('选择组合： 刷新\n')
                cancel()
                continue
            else:
                print('选择组合： 无')
                set_time('normal')
        confirm()
        i += 1
        print()


def accelerate_round():
    for index in ENABLED:
        accelerate(index)
        output_list.append(hire(index))
    print()


def test():
    identify_list, result_list = find()
    if result_list:
        print('推荐组合：')
        score_list = []
        min_score = 100
        for r in result_list:
            score_list.append(r['score'])
            print(r['score'], r['tags'], r['result'])
            min_score = result_list[0]['score']
        min_count = Counter(score_list)

        if min_score < 2:
            print('选择组合： 保留')
        elif 2 <= min_score < 10:
            if min_score >= 9 and ACCELERATE:
                print('首选组合： 刷新')

            # 如果有多个同分结果，就随机选一个
            rand = random.randint(1, min_count[min_score])
            tags_index = []
            for tag in result_list[rand - 1]['tags']:
                tags_index.append(identify_list.index(tag))

            print('选择组合：', result_list[rand - 1]['tags'])
    else:
        print('推荐组合： 无')


if __name__ == '__main__':
    if DEBUG:
        test()
    else:
        baidu_ocr.get_access_token(your_client_id, your_client_secret)
        max_round = check()
        print('自动脚本即将开始，运行过程中非必要不要移动鼠标。\n')
        time.sleep(2)
        get_window()

        DISABLED = []
        output_list = []

        print('开始初始化轮。\n')
        init_round()
        for _ in DISABLED:
            ENABLED.remove(_)
        DISABLED.clear()

        for round_num in range(max_round):
            print('第 {} 轮：'.format(round_num + 1))
            choose_round()
            for _ in DISABLED:
                ENABLED.remove(_)
            DISABLED.clear()
            # 招募至最后1轮时不进行加速
            if round_num != max_round - 1:
                accelerate_round()

        if output_list:
            print('招募结果：' + str(output_list))
            print('招募统计：' + str(Counter(output_list)))
            print('招募结果的识别可能存在较大误差，具体结果可打开output文件夹查看。日志可打开log文件夹查看。')
