import re
import os
from typing import Tuple
""" 
主任务是提取返回结果，并将与prompt内容进行贴合
"""
"""
全局需要修改的变量
下面的folder需要自行创建！
prompt_path: 包含冗余检测的prompt的路径
redundancy_folder: 包含冗余对话的文件夹的路径
saving_folder: 保存贴合的文件夹的路径
"""
prompt_path: str = "/home/wind/Desktop/projects/autogen_some_code/text/sum/redundant_in_context_prompt_code_generation"
redundancy_folder = "/home/wind/Desktop/projects/Redanduncy_AutoGPT/autogpts/mytest/results"
saving_folder = "/home/wind/Desktop/projects/Redanduncy_AutoGPT/autogpts/mytest/redundancy_checking/saving_results"
detecting_folder = "/home/wind/Desktop/projects/Redanduncy_AutoGPT/autogpts/mytest/redundancy_checking/detecting_results"

""" 
读取结果文件夹，返回所有的结果内容，同时返回filename的list
"""
def scan_folder_and_read_files(folder_path) -> list:
    return_list = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        # Iterate through subfolders and filenames
        for filename in filenames:
            # Construct the full path of the file
            file_path = os.path.join(dirpath, filename)
            
            # Read the contents of the file (you can modify this part to process the file data)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents = file.read()
            return_list.append((filename, file_contents))
    return return_list

if __name__ == "__main__":
    with open(prompt_path, "r") as f:
        prompt = f.read()
    list = scan_folder_and_read_files(redundancy_folder)
    # "normal_assistant[\s\S]*?"
    pattern = "---------------------------\nQuestion:[\s\S]*?---------------------------"
    for filename, contents in list:
        answer_list = re.findall(pattern, contents)
        with open(saving_folder + "/" + filename, "w") as f:
            with open(detecting_folder + "/" + filename, "w") as f2:
                index = 0
                for answer in answer_list:
                    index = index + 1
                    eliminated_answer = answer.split('\n', 3)[3][:-27]
                    target_string = prompt + "\n" + r'"""' + '\n' + eliminated_answer + r'"""' + '\n\n\n\n'  
                    f.write(target_string)
                    f2.write(f'## Chat {index}\n' + "### Content\n" + eliminated_answer  + '\n\n### Checking_results\n' + "```\n\n```\n\n\n" )