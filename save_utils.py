import json 
import os 
import time 


def process_answer(full_answer, restrict_leakage):
    public_answer = extract_answer(full_answer, restrict_leakage)
    plan = extract_plan(full_answer)
    return public_answer, plan 


def save_conversation(history, agent_name,full_answer, prompt,round_assign=[],initial=False, restrict_leakage=False):
    if initial: 
        history['content']['slot_assignment'] = round_assign
        history['content']["rounds"] = []
        history['content']['plan'] = {}  
        history['content']["finished_rounds"]= 0   
    else:
        history['content']["finished_rounds"] += 1
    
    public_answer, plan  = process_answer(full_answer, restrict_leakage)
    if initial and public_answer == '':
        public_answer = full_answer

    history['content']["rounds"].append({'agent':agent_name, 'prompt': prompt, 'full_answer': full_answer, 'public_answer': public_answer})

    if plan:        
        if agent_name in history['content']['plan'].keys():
            history['content']['plan'][agent_name].append(plan)
        else:
            history['content']['plan'][agent_name] = [plan]
    
    write_file(history['content'],history['file'])
    if public_answer == '':
        print(full_answer)
        raise ValueError('Public answer is empty')
    return history      
    

def extract_answer(answer, restrict_leakage):
    if restrict_leakage:
        #extract final answer by removing scratchpad 
        if "<ANSWER>" in answer and "</ANSWER>" in answer: 
            return answer.split('<ANSWER>')[-1].split("</ANSWER>")[0]
        elif "<ANSWER>" in answer:
            public_answer = answer.split('<ANSWER>')[-1]
            _plan = extract_plan(public_answer)
            public_answer = public_answer.replace(_plan,'')
            return public_answer
        return ''
    else: # initial paper implementation
        #extract final answer by removing scratchpad 
        if "<ANSWER>" and "</ANSWER>" in answer: 
            answer = answer.split('<ANSWER>')[-1].split("</ANSWER>")[0]
        if "<ANSWER>" in answer:
            answer = answer.split('<ANSWER>')[-1]
        return answer
    
def extract_plan(answer):
    #extract plan 
    if "<PLAN>" in answer and "</PLAN>" in answer: 
        plan = answer.split('<PLAN>')[-1].split("</PLAN>")[0]
        return plan
    elif "<PLAN>" in answer: 
        plan = answer.split('<PLAN>')[-1]
        return plan 
    return ''


def write_file(log_dict,output_file):
    with open(output_file, "w") as outfile:
        json.dump(log_dict, outfile)
    return 

def create_outfiles(args,OUTPUT_DIR):
    '''
    create output dirs of experiment if it does not exit 
    if restart:
        load output files from args.output_file 
        find next round to start from 
        load the same agent assignment per rounds
    else:
        create new dirs, initialize history files and random assignment arrays and start from round 0 
    '''
    
    history ={}

    
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if args.restart:
        history['file'] = os.path.join(OUTPUT_DIR, args.output_file)
        
        with open(history['file'], "r") as file:
            history['content'] = json.load(file)
            
        round_start = int(history['content']["finished_rounds"]) 
        round_assign = history['content']["slot_assignment"]
    else:
        time_str = time.strftime("%H_%M_%S", time.localtime())
        output_file = os.path.join(OUTPUT_DIR,args.output_file.split('.json')[0] + time_str + '.json')

        round_start = 0  

        history = {'file': output_file, 'content': {}}
        round_assign = []
        

    return round_assign, round_start, history 
    



    
    