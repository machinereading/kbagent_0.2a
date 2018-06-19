import json
from nlg_module import NLG
import simsimi
import random
from time import strftime

NLG = NLG()
Dialog_Counter = 0
Dialog_Counter_Limit = 0

def select_best_chitchats(chitchats):
    # random
    d = random.choice(chitchats)
    return d

def save_data(dialogs_data):
    now = strftime("%y%m%d_%H%M%S")
    logid = str(now)+'_'+str(random.randint(1,1000))
    filename = './logs/'+logid
    with open(filename,'w', encoding='utf-8') as f:
        json.dump(dialogs_data,f,indent=4,ensure_ascii=False)
    print(filename, '이 저장되었습니다')

def terminal():
    global Dialog_Counter
    global Dialog_Counter_Limit
    utterance = input("Input the number of dialogs : ")
    Dialog_Counter_Limit = int(utterance)
    dialogs_data = { "RECOMMEND" : {}, "DEBUT" : {}, "SIMILAR" : {}, "TV" : {}, "RECORD" : {}, "MISC" : {} }
    while Dialog_Counter < Dialog_Counter_Limit:
        question_dict = {}
        question_dict = NLG.nlg()
        question_list = []
        question_list = list(question_dict.keys())
        for i in range(len(question_list)):
            for j in range(len(question_dict[question_list[i]])):
                for_simsimi = []
                input_json = {}
                input_json['text'] = question_dict[question_list[i]][j]
                input_json['lang'] = 'ko'
                sim_result = simsimi.simsimi_interface(input_json)
                for_simsimi.append(sim_result)
                answer = select_best_chitchats(for_simsimi)['text']
                if input_json['text'] in dialogs_data[question_list[i]]:
                    tmp = dialogs_data[question_list[i]][input_json['text']]
                    tmp.append(answer)
                else:
                    dialogs_data[question_list[i]][input_json['text']] = [answer]
        Dialog_Counter += 1
        print(str(Dialog_Counter))
    save_data(dialogs_data)

terminal()
