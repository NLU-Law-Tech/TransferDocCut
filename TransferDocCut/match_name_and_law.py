import re
from TransferDocCut.find_laws import find_laws
from TransferDocCut.find_laws import get_all_laws_list


def match_name_and_law(SFact, name_list, break_line='\r\n'):
    # 取出執掌法條
    focus_laws_list = get_all_laws_list()
    # init object for each person
    name_and_law = {}
    for name in name_list:
        name_and_law[name] = []
    # 以逗號分割
    SFact_list = SFact.split("，")
    for name in name_list:
        for SFact_a_line in SFact_list:
            if name in SFact_a_line:
                for focus_law in focus_laws_list:
                    if re.search(focus_law, SFact_a_line) != None:
                        focus_law_position = re.search(
                            focus_law, SFact_a_line)
                        SPA_list = find_SPA(
                            focus_law, SFact_a_line, focus_law_position.start(), break_line)
                        SPA_list = add_ROC(SPA_list)
                        SPA_list = trans_tai_to_TAI(SPA_list)
                        name_and_law[name].extend(SPA_list)
        # 去除重複
        name_and_law[name] = list(set(name_and_law[name]))
    return name_and_law


def find_SPA(law, text, law_position_start, break_line='\r\n'):
    # 先轉把中文數字轉成阿拉伯數字
    # try:
    #     text = cn2an.transform(text,'cn2an')
    # except:
    #     print(text)

    SPA_list = []

    regex_SPA = "第\d*條第\d*項第\d*款"
    regex_PA = "第\d*條第\d*項"
    regex_A = "第\d*條"
    # regex_article = "第.*條"
    # regex_paragraph = "第.*項"
    # regex_subparagraph = "第.*款"
    SPA_list = re.findall(regex_SPA, text)
    PA_list = re.findall(regex_PA, text)
    A_list = re.findall(regex_A, text)

    SPA_list.extend(set(SPA_list))
    SPA_list.extend(set(PA_list))
    SPA_list.extend(set(A_list))
    SPA_list = list(set(SPA_list))
    # if len(SPA_list)==0:

    SPA_list_copy = SPA_list.copy()
    # 保留含有細項的法條
    for SPA_c in SPA_list_copy:
        for SPA in SPA_list:
            if SPA_c == SPA:
                continue
            else:
                if SPA in SPA_c and len(SPA_c) > len(SPA):
                    SPA_list.remove(SPA)

    SPA_list_copy = SPA_list.copy()
    #　加上法條名稱
    for i in range(len(SPA_list_copy)):

        origin_start = re.search(SPA_list[i], text).start()
        law_name = get_laws_name(SPA_list[i], origin_start,
                                 text, get_all_laws_list(), break_line)
        SPA_list[i] = law_name+SPA_list[i]
    return SPA_list


def add_ROC(law_list):
    # 只要只有寫到刑法第幾條 刑法前面無字元  前面全部加上中華民國
    for i in range(len(law_list)):
        if re.search("^刑法", law_list[i]) != None:
            law_list[i] = "中華民國"+law_list[i]
    return law_list


def trans_tai_to_TAI(law_list):
    # 把台都轉成臺
    for i in range(len(law_list)):
        if "台" in law_list[i]:
            law_list[i] = str(law_list[i]).replace("台", "臺")

    return law_list


def check_name_and_law(name_list, name_and_law):
    # 檢查是否有抓到犯罪事實的法條
    bool_value = False
    for name in name_list:
        if len(name_and_law[name]) != 0:
            bool_value = True
            return bool_value
    return bool_value


def backspace_SP(regex_str, law):
    regex_position = re.search(regex_str, law)
    if regex_position == None:
        return law
    else:
        return law[:regex_position.start()]

# 資料清洗


def clean_text(judgement, break_line='\r\n'):
    # 去空白  去換行符號
    clean_text = re.sub(break_line, "", re.sub(r"\s+", "", judgement))
    return clean_text


def get_laws_name(laws, origin_start, CJ_text, Match_laws_list, Break_line):
    laws_name_dict_list = []
    laws_name_dict = {}
    # 先初始化
    laws_name_dict["law"] = ""
    laws_name_dict["distance"] = 99999999999
    for law in Match_laws_list:
        # 先找該法律名稱是否有在CJ_text
        if re.search(law, CJ_text) == None:
            continue
        else:
            # 如果所標記的法律已經含有 執掌法條  就直接return
            clean_laws = re.sub(Break_line, "", strip_blank(laws))
            if re.search(law, clean_laws) != None:
                return law
            # 找出所有位置
            all_match_positions = re.finditer(law, CJ_text)
            if len(laws_name_dict) == 0:
                distance = 99999999999
            else:
                distance = laws_name_dict["distance"]
            for match_position in all_match_positions:
                # 計算距離多遠  並且法律名稱要在 origin_start 前面
                temp_distance = origin_start-match_position.start()
                # 要找跟laws最接近的位置
                if temp_distance < distance and temp_distance >= 0:
                    distance = temp_distance
                    laws_name_dict["law"] = law
                    laws_name_dict["distance"] = distance
    return laws_name_dict["law"]


def strip_blank(dirty_str):
    # 去空白
    clean_str = re.sub(r"\s+", "", dirty_str)
    return clean_str
