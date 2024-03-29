import re
from TransferDocCut.find_laws import find_laws
from TransferDocCut.find_laws import get_all_laws_list
from TransferDocCut.find_laws import get_blacklist_law_list

def match_name_and_law(text, name_list, break_line='\r\n'):
    # 取出執掌法條
    focus_laws_list = get_all_laws_list()

    # init object for each person
    name_and_law = {}
    all_name_positions = {}
    all_law_positions = {}
    for name in name_list:
        name_and_law[name] = []
        all_name_positions[name] = []
    for focus_law in focus_laws_list:
        all_law_positions[focus_law] = []

    # 清洗Text
    split_str="[_LAW]"
    text = text.split(split_str)[-1]
    text = clean_text(text, break_line)
    # 找出被告跟foucus_law在Text所有的位置
    all_name_positions = find_string_all_positions(
        text, name_list, all_name_positions)
    all_law_positions = find_string_all_positions(
        text, focus_laws_list, all_law_positions)
    fullname_law_dict=find_fullname_law(text, all_law_positions)
    # 若被告只有一人，法條全部灌給他
    if len(name_list)==1:
        for key, law_list in fullname_law_dict.items():
            name_and_law[name_list[0]].extend(law_list)
        for name in name_list:
            name_and_law[name] = list(set(name_and_law[name]))
        return name_and_law
    # 所有的位置
    all_positions_dict, all_positions_list = find_all_positions_dict_and_list(
        all_name_positions, all_law_positions)

    temp_name_list = []
    temp_law_list = []
    temp_law_positions_list = []
    last_flag = ""
    current_flag = ""
    law_position = -1
    for i, position in enumerate(all_positions_list):
        # 紀錄目前的是找被告還是法條
        current_flag = get_key(all_positions_dict, position)

        # 如果是找被告而且上一個flag不是法條
        if current_flag == "name" and last_flag != "law":
            name = get_key(all_name_positions, position)
            temp_name_list.append(name)
        elif current_flag == "law":
            law = get_key(all_law_positions, position)
            temp_law_list.append(law)
            temp_law_positions_list.append(position)
        # 如果上一個是法條，現在是被告的話，要把法條加進來
        if (last_flag == "law" and current_flag == "name") or (i+1 == len(all_positions_list)):
            for temp_name in temp_name_list:
                for temp_law_position in temp_law_positions_list:
                    name_and_law[temp_name].extend(
                        fullname_law_dict[temp_law_position])
                # for temp_law in temp_law_list:
                #     name_and_law[temp_name].append(temp_law)
            # 清空完後，要把剛剛的name 加進來
            temp_name_list.clear()
            temp_law_list.clear()
            temp_law_positions_list.clear()
            name = get_key(all_name_positions, position)
            temp_name_list.append(name)
        
        # 紀錄flag
        last_flag = current_flag
        

    # 以逗號分割
    # SFact_list = SFact.split("，")
    # for name in name_list:
    #     for SFact_a_line in SFact_list:
    #         if name in SFact_a_line:
    #             for focus_law in focus_laws_list:
    #                 if re.search(focus_law, SFact_a_line) != None:
    #                     focus_law_position = re.search(
    #                         focus_law, SFact_a_line)
    #                     SPA_list = find_SPA(
    #                         focus_law, SFact_a_line, focus_law_position.start(), break_line)
    #                     SPA_list = add_ROC(SPA_list)
    #                     SPA_list = trans_tai_to_TAI(SPA_list)
    #                     name_and_law[name].extend(SPA_list)
    #     # 去除重複
    #     name_and_law[name] = list(set(name_and_law[name]))
    for name in name_list:
        name_and_law[name] = list(set(name_and_law[name]))
    return name_and_law


# 用來找完整的法條(包含款、項、條)
def find_fullname_law(text, all_law_positions):
    if len(all_law_positions) == 0: return {};
    regex_subparagraph = "第\d*款"
    regex_paragraph = "第\d*項"
    regex_article = "第\d*條"
    # key , value 轉換
    all_law_positions_dict = {}
    all_law_positions_dict = exchange_key_value(all_law_positions)
    # 取出法律名稱的位置並大到小排列(從後往前排列)
    all_law_positions_list = sorted(all_law_positions_dict, reverse=True)
    subparagraph_positions_dict, all_subparagraph_positions_list = find_article_paragraph_subparagraph_positions(
        text, regex_subparagraph)
    paragraph_positions_dict, all_paragraph_positions_list = find_article_paragraph_subparagraph_positions(
        text, regex_paragraph)
    article_positions_dict, all_article_positions_list = find_article_paragraph_subparagraph_positions(
        text, regex_article)
    # 找黑名單法條
    # 避免以下狀況發生
    # 政府採購法第87條第3項......依刑事訴訟法第251條第1項...
    # 政府採購法第87條第3項,政府採購法第251條第1項
    blacklaw_list=get_blacklist_law_list()
    blacklaw_positions_dict, all_blacklaw_positions_list = find_blacklaw_positions(
        text, blacklaw_list)
    # init object
    law_article_para_subpara_positions_dict={}
    kind_list=["law","article","paragraph","subparagraph","blacklaw"]
    fullname_law_dict = {}
    for law_position in all_law_positions_list:
        fullname_law_dict[law_position]=[]
    for kind in kind_list:
        law_article_para_subpara_positions_dict[kind] = []
        if kind=="law":
            law_article_para_subpara_positions_dict[kind] = all_law_positions_list
        elif kind == "article":
            law_article_para_subpara_positions_dict[kind] = all_article_positions_list
        elif kind == "paragraph":
            law_article_para_subpara_positions_dict[kind] = all_paragraph_positions_list
        elif kind == "subparagraph":
            law_article_para_subpara_positions_dict[kind] = all_subparagraph_positions_list
        elif kind == "blacklaw":
            law_article_para_subpara_positions_dict[kind] = all_blacklaw_positions_list
    # 
    law_article_para_subpara_positions_list = get_extend_list(
        all_law_positions_list, all_article_positions_list, all_paragraph_positions_list, all_subparagraph_positions_list, all_blacklaw_positions_list)
    last_flag = ""
    current_flag = ""
    next_flag=""
    temp_article_name_list=[]
    temp_paragraph_name_list = []
    temp_subparagraph_name_list = []
    fullname_law_list = []
    # pass_flag 用來跳過blacklaw的條項款
    pass_flag=False
    law_name_position=0
    for i, position in enumerate(law_article_para_subpara_positions_list):
        # 紀錄目前的是找法、條、項、款
        current_flag = get_key(
            law_article_para_subpara_positions_dict, position)
        
        if current_flag == "law":
           law_name = get_key(all_law_positions, position)
           law_name_position=position
           pass_flag=False
        elif current_flag == "article" and pass_flag==False:
            temp_article_name_list.append(article_positions_dict[position])
            temp_article_name_list = list(set(temp_article_name_list))
        elif current_flag == "paragraph"and pass_flag == False:
            temp_paragraph_name_list.append(paragraph_positions_dict[position])
        elif current_flag == "subparagraph"and pass_flag == False:
            temp_subparagraph_name_list.append(
                subparagraph_positions_dict[position])
        elif current_flag == "blacklaw":
            pass_flag=True
            continue
        if i+1 < len(law_article_para_subpara_positions_list):
            next_flag = get_key(
                law_article_para_subpara_positions_dict, law_article_para_subpara_positions_list[i+1])
        # 若下一個next_flag 是law 或者 已經到最後一個了
        # 開始組完整的法律名稱
        if (current_flag==next_flag)or (current_flag == "paragraph" and next_flag == "article") or (current_flag == "subparagraph" and next_flag == "paragraph") or (next_flag == "law") or (i+1 == len(law_article_para_subpara_positions_list)):
            if len(temp_subparagraph_name_list) > 0 and len(temp_paragraph_name_list) > 0 and len(temp_article_name_list) > 0:
                for temp_article_name in temp_article_name_list:
                    for temp_paragraph_name in temp_paragraph_name_list:
                         for temp_subparagraph_name in temp_subparagraph_name_list:
                            fullname_law_list.append(
                                law_name+temp_article_name+temp_paragraph_name+temp_subparagraph_name) 
                            fullname_law_dict[law_name_position].append(
                                law_name+temp_article_name+temp_paragraph_name+temp_subparagraph_name)
            elif len(temp_paragraph_name_list) > 0 and len(temp_article_name_list) > 0:
                for temp_article_name in temp_article_name_list:
                    for temp_paragraph_name in temp_paragraph_name_list:
                            fullname_law_list.append(
                                law_name+temp_article_name+temp_paragraph_name)
                            fullname_law_dict[law_name_position].append(
                                law_name+temp_article_name+temp_paragraph_name)
            elif len(temp_article_name_list) > 0:
                for temp_article_name in temp_article_name_list:
                    fullname_law_list.append(law_name+temp_article_name)
                    fullname_law_dict[law_name_position].append(
                        law_name+temp_article_name)
        # 如果由"款"轉換"項" 代表 "條" 要留下
        if (current_flag == "subparagraph" and next_flag == "paragraph"):
            temp_paragraph_name_list.clear()
            temp_subparagraph_name_list.clear()
        # 如果由"項"轉換"條" 代表 "法" 要留下
        if (current_flag == "paragraph" and next_flag == "article") or next_flag=="law":
            temp_paragraph_name_list.clear()
            temp_subparagraph_name_list.clear()
            temp_article_name_list.clear()
        # 如果跟下一個 flag 一樣
        if (current_flag==next_flag):
            if(current_flag=="article"):
                temp_article_name_list.clear()
            elif(current_flag == "paragraph"):
                temp_paragraph_name_list.clear()
            elif(current_flag == "subparagraph"):
                temp_subparagraph_name_list.clear()


        # 如果由 "條"
        # 紀錄flag
        last_flag = current_flag
    # print(fullname_law_list)
    # print(fullname_law_dict)
    return fullname_law_dict
    # # 用款找到對應的項
    # law_delete_list=[]
    # article_delete_list = []
    # paragraph_delete_list = []
    # subparagraph_delete_list=[]
    # # key 是位置 
    # # while len(law_all_positions_list)>0:
    # for law_position in law_all_positions_list:
    #     # 條
    #     for article_position in article_all_positions_list:
    #         # 項
    #         for paragraph_position in paragraph_all_positions_list:
    #             if article_position < paragraph_position:
    #                 # 代表 "項" 有找到對應的 
    #                 paragraph_delete_list.append(paragraph_position)
    #             # 款
    #             for subparagraph_position in subparagraph_all_positions_list:
    #                 if paragraph_position < subparagraph_position:
    #                     # 代表"款"有找到對應的"項"
    #                     subparagraph_delete_list.append(
    #                         subparagraph_position)
    #                     temp_fullname_law = law_all_positions_dict[law_position] + article_positions_dict[article_position] + paragraph_positions_dict[paragraph_position] + \
    #                         subparagraph_positions_dict[subparagraph_position]
    #                     print(temp_fullname_law)
    #             # 刪除 有對應到"項" 的 "款"
    #         #     for key in subparagraph_delete_list:
    #         #         subparagraph_all_positions_list.remove(key)
    #         #     subparagraph_delete_list.clear()
    #         # for key in paragraph_delete_list:
    #         #     subparagraph_all_positions_list.remove(key)


def exchange_key_value(a_dict):
    exchanged_dict = {}
    for key, value_list in a_dict.items():
        for value in value_list:
            exchanged_dict[value] = key
    return exchanged_dict


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


def clean_text(text, break_line='\r\n'):
    # 去空白  去換行符號
    clean_text = re.sub(break_line, "", re.sub(r"\s+", "", text))
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


def find_string_all_positions(text, string_list, string_dict):
    for string in string_list:
        string_all_match_positions = re.finditer(re.escape(string), text)
        for string_match_position in string_all_match_positions:
            string_dict[string].append(string_match_position.start())

    # 空的都不要
    copy_string_dict = string_dict.copy()
    for i in copy_string_dict.items():
        if len(i[1]) == 0:
            del string_dict[i[0]]
    return string_dict

# 找條項款的位置(包含同條、同項)
def find_article_paragraph_subparagraph_positions(text, regex_str):
    regex_positions_dict = {}
    regex_positions = re.finditer(regex_str, text)
    for regex_position in regex_positions:
        # 位置當key
        regex_positions_dict[regex_position.start()] = regex_position[0]
    # 再回傳由大到小的位置(由後往前)
    all_positions_list = sorted(regex_positions_dict, reverse=True)
    return regex_positions_dict, all_positions_list


def find_blacklaw_positions(text, blacklaw_list):
    regex_positions_dict = {}
    for blacklaw in blacklaw_list:
        regex_positions = re.finditer(blacklaw, text)
        for regex_position in regex_positions:
            # 位置當key
            regex_positions_dict[regex_position.start()] = regex_position[0]
    # 再回傳由大到小的位置(由後往前)
    all_positions_list = sorted(regex_positions_dict, reverse=True)
    return regex_positions_dict, all_positions_list

def find_all_positions_dict_and_list(all_name_positions, all_law_positions):
    all_positions_dict = {}
    all_positions_dict["name"] = []
    all_positions_dict["law"] = []
    all_positions_list = []
    for name, position_list in all_name_positions.items():
        all_positions_dict["name"].extend(position_list)
        all_positions_list.extend(position_list)
    for name, position_list in all_law_positions.items():
        all_positions_dict["law"].extend(position_list)
        all_positions_list.extend(position_list)
    # 排列
    all_positions_list.sort()
    return all_positions_dict, all_positions_list


def get_key(dict, value):
    for k, v_list in dict.items():
        if value in v_list:
            return k

def get_extend_list(
        all_law_positions_list, all_article_positions_list, all_paragraph_positions_list, all_subparagraph_positions_list, all_blacklaw_positions_list):

    extend_list=[]
    extend_list.extend(all_law_positions_list)
    extend_list.extend(all_article_positions_list)
    extend_list.extend(all_paragraph_positions_list)
    extend_list.extend(all_subparagraph_positions_list)
    extend_list.extend(all_blacklaw_positions_list)
    return sorted(extend_list)

def get_blacklist_law_position(text):
    blacklist_law_list=get_blacklist_law_list()

class getoutofloop(Exception):
    pass
