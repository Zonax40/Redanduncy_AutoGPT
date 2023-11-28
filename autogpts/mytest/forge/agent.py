from forge.sdk import (
    Agent,
    AgentDB,
    ForgeLogger,
    Step,
    StepRequestBody,
    Task,
    TaskRequestBody,
    Workspace,    
    PromptEngine,	
    chat_completion_request,	
    ChromaMemStore	
)
import json	
import pprint

LOG = ForgeLogger(__name__)

""" 
ATTENTION: 注意：
由于需要记录对话框，因此对话框为一次性的！
同时，由于多线程的问题，为了正确的保存结果，请一定一定分开询问
"""

""" 
全局需要修改的变量
result_folder: 用于保存访问的结果
target_folder: 真正的保存路径，会随着后续操作改变
"""
result_folder: str = "/home/wind/Desktop/projects/Redanduncy_AutoGPT/autogpts/mytest/results"

def mkdir_result_folder(folder: str) -> None:
    import os
    os.makedirs(folder, exist_ok=True)


class ForgeAgent(Agent):
    """
    The goal of the Forge is to take care of the boilerplate code, so you can focus on
    agent design.

    There is a great paper surveying the agent landscape: https://arxiv.org/abs/2308.11432
    Which I would highly recommend reading as it will help you understand the possabilities.

    Here is a summary of the key components of an agent:

    Anatomy of an agent:
         - Profile
         - Memory
         - Planning
         - Action

    Profile:

    Agents typically perform a task by assuming specific roles. For example, a teacher,
    a coder, a planner etc. In using the profile in the llm prompt it has been shown to
    improve the quality of the output. https://arxiv.org/abs/2305.14688

    Additionally, based on the profile selected, the agent could be configured to use a
    different llm. The possibilities are endless and the profile can be selected
    dynamically based on the task at hand.

    Memory:

    Memory is critical for the agent to accumulate experiences, self-evolve, and behave
    in a more consistent, reasonable, and effective manner. There are many approaches to
    memory. However, some thoughts: there is long term and short term or working memory.
    You may want different approaches for each. There has also been work exploring the
    idea of memory reflection, which is the ability to assess its memories and re-evaluate
    them. For example, condensing short term memories into long term memories.

    Planning:

    When humans face a complex task, they first break it down into simple subtasks and then
    solve each subtask one by one. The planning module empowers LLM-based agents with the ability
    to think and plan for solving complex tasks, which makes the agent more comprehensive,
    powerful, and reliable. The two key methods to consider are: Planning with feedback and planning
    without feedback.

    Action:

    Actions translate the agent's decisions into specific outcomes. For example, if the agent
    decides to write a file, the action would be to write the file. There are many approaches you
    could implement actions.

    The Forge has a basic module for each of these areas. However, you are free to implement your own.
    This is just a starting point.
    """

    def __init__(self, database: AgentDB, workspace: Workspace):
        """
        The database is used to store tasks, steps and artifact metadata. The workspace is used to
        store artifacts. The workspace is a directory on the file system.

        Feel free to create subclasses of the database and workspace to implement your own storage
        """
        super().__init__(database, workspace)

    async def create_task(self, task_request: TaskRequestBody) -> Task:
        """
        The agent protocol, which is the core of the Forge, works by creating a task and then
        executing steps for that task. This method is called when the agent is asked to create
        a task.

        We are hooking into function to add a custom log message. Though you can do anything you
        want here.
        """
        task = await super().create_task(task_request)
        LOG.info(
            f"📦 Task created: {task.task_id} input: {task.input[:40]}{'...' if len(task.input) > 40 else ''}"
        )
        """ 
        创建保存路径: 问题名 + 创建时间
        """
        from datetime import datetime
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.target_folder = result_folder + "/" + task.input + ":" + current_time_str
        mkdir_result_folder(self.target_folder)
        """ 
        创建保存的文件
        """
        self.target_file = self.target_folder + "/" + task.input + ".md" 
        with open(self.target_file, "w") as f:
            pass
        return task

    async def execute_step(self, task_id: str, step_request: StepRequestBody) -> Step:
        # Firstly we get the task this step is for so we can access the task input
        task = await self.db.get_task(task_id)

        
        # Create a new step in the database
        # 需要注意到在db里面正式保存的是StepModel， 这里的返回结果试讲StepModel改为Step类，因此在这里无论如何怎么修改step，都不会影响原本保存的内容
        # Class step
        step = await self.db.create_step(
            task_id=task_id, input=step_request, is_last=True
        )
        """以下的注释为，获取step_list，_step.input为输入问题，_step.output为回答结果"""
        # step_list, temp = self.db._list_steps(task_id)
        # for _step in step_list:
        #     print(_step.input)
        #     print(_step.output)
        # Log the message
        LOG.info(f"\t✅ Final Step completed: {step.step_id} input: {step.input[:19]}")

        # Initialize the PromptEngine with the "gpt-3.5-turbo" model
        prompt_engine = PromptEngine("gpt-3.5-turbo")

        # Load the system and task prompts
        system_prompt = prompt_engine.load_prompt("system-format")

        # Initialize the messages list with the system prompt
        """ 构建messages请参考 https://help.openai.com/en/articles/7042661-chatgpt-api-transition-guide """
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        """ 装载对话记录,暂不使用 """
        # step_list, temp = self.db._list_steps(task_id)
        # for _step in step_list:
        #     messages.append({"role": "user", "content":_step.input})
        #     messages.append({"role": "assistant", "content":_step.output})

        # Define the task parameters
        task_kwargs = {
            "task": task.input,
            "abilities": self.abilities.list_abilities_for_prompt(),
        }

        # Load the task prompt with the defined task parameters
        task_prompt = prompt_engine.load_prompt("task-step", **task_kwargs)

        # Append the task prompt to the messages list
        messages.append({"role": "user", "content": task_prompt})
        
        try:
            # Define the parameters for the chat completion request
            chat_completion_kwargs = {
                "messages": messages,
                "model": "gpt-3.5-turbo",
            }
            # Make the chat completion request and parse the response
            """ chat_response的格式符合url: https://platform.openai.com/docs/api-reference/chat/object """
            chat_response = await chat_completion_request(**chat_completion_kwargs)
            # answer = json.loads(chat_response["choices"][0]["message"]["content"])
            answer = chat_response["choices"][0]["message"]["content"]

            # Log the answer for debugging purposes
            LOG.info(pprint.pformat(answer))

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            LOG.error(f"Unable to decode chat response: {chat_response}")
        except Exception as e:
            # Handle other exceptions
            LOG.error(f"Unable to generate chat response: {e}")

        # Extract the ability from the answer   
        # try:
        #     ability = answer["ability"]
        # except KeyError:
        #     ability = answer["abilities"]
        # except: 
        #     LOG.error(f"Fail to get the ability")

        # Run the ability and get the output
        # We don't actually use the output in this example
        # output = await self.abilities.run_ability(
        #     task_id, ability["name"], **ability["args"]
        # )

        # Set the step output to the "speak" part of the answer
        # step.output = answer["thoughts"]["speak"]
        step.output = answer
        """ 将结果保存至文件中 """
        with open(self.target_file, "a") as f:
            f.write("---------------------------\n")
            f.write("Question: " + step.input + "\n")
            f.write("Answer:\n" + step.output + "\n")
            f.write("---------------------------\n")
        """ 用于将结果进行回答进行保存 """
        self.db.change_step_output(task_id=task_id, step_id=step.step_id, output = answer)
        # Return the completed step
        return step
