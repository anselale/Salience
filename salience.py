from agentforge.modules.ActionExecution import Action
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from CustomAgents.ExecutionAgent import ExecutionAgent
from CustomAgents.TaskCreationAgent import TaskCreationAgent
from CustomAgents.StatusAgent import StatusAgent
from CustomAgents.SummarizationAgent import SummarizationAgent
from agentforge.utils.functions.Logger import Logger
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface

from Utilities.TaskHandling import TaskHandling
import uuid


def id_generator(data):
    return [str(i + 1) for i in range(len(data))]


def metadata_builder(order, details):
    return {
        "Status": "not completed",
        "Description": details.strip(),
        "List_ID": str(uuid.uuid4()),
        "Order": order + 1  # assuming Name is passed in details for Tasks
    }


class Salience:

    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)

        try:
            self.data = {}
            self.task = {}
            self.context = {}
            self.feedback = {}
            self.reason = {}
            self.selected_action = {}

            self.frustration_step = 0.1
            self.min_frustration = 0.7
            self.max_frustration = 1
            self.frustration = self.min_frustration

            self.functions = Functions()
            self.config_data = self.functions.agent_utils.config.data
            self.persona = self.config_data['settings']['configuration']['Persona']

            self.storage = StorageInterface().storage_utils
            self.init_storage()

            self.task_handling = TaskHandling()

            self.summarization_agent = SummarizationAgent()
            self.action_execution = Action()
            self.action_selection = ActionSelectionAgent()
            self.exec_agent = ExecutionAgent()
            self.task_creation_agent = TaskCreationAgent()
            self.status_agent = StatusAgent()

            self.init_settings_and_objectives()
        except Exception as e:
            self.logger.log(f"Initialization error: {e}", 'error')
            raise  # Optionally re-raise the exception after logging

    def init_settings_and_objectives(self):
        self.action_selection.set_threshold(self.frustration)
        self.action_selection.set_number_of_results(10)
        self.set_objective()

    def init_storage(self):
        tasks = self.config_data['personas'][self.persona]['Tasks']
        storage = {'Tasks': tasks}

        [self.prefill_storage(key, value) for key, value in storage.items()]

    def prefill_storage(self, collection_name, data):
        try:
            ids = id_generator(data)

            metadata = [metadata_builder(i, item) for i, item in enumerate(data)]

            description = [meta['Description'] for meta in metadata]

            save_params = {
                "collection_name": collection_name,
                "ids": ids,
                "data": description,
                "metadata": metadata,
            }

            self.storage.save_memory(save_params)
        except Exception as e:
            self.logger.log(f"Error in prefill_storage: {e}", 'error')

    def prepare_objective(self):
        while True:
            user_input = input("\nDefine Objective (leave empty to use defaults): ")
            if user_input.lower() == '':
                return None
            else:
                self.config_data['personas'][self.persona]['Objective'] = user_input
                return user_input

    def run(self):
        try:
            self.log_start()
            self.load_data_from_storage()
            self.summarize_task()
            self.check_for_actions()
            self.log_results()
        except Exception as e:
            self.logger.log(f"Run error: {e}", 'error')

    def loop(self):
        try:
            while True:
                self.display_task_list()
                self.fetch_context()
                self.fetch_feedback()
                self.run()
                self.determine_status()
                self.handle_frustration()
        except KeyboardInterrupt:
            self.logger.log("Loop interrupted by user", 'info')
        except Exception as e:
            self.logger.log(f"Loop error: {e}", 'error')

    def check_for_actions(self):
        self.select_action()

        if self.selected_action:
            self.execute_action()
        else:
            self.execute_task()

    def execute_action(self):
        try:
            task = self.task_handling.get_current_task()['document']
            action_results = self.action_execution.run(task=task, action=self.selected_action, context=self.reason)
            formatted_results = self.format_action_results(action_results)

            self.task['execution_results'] = {
                "task_result": formatted_results,
                "current_task": self.data['current_task'],
                "context": self.context,
                "Order": self.data['Order']
            }
        except Exception as e:
            self.logger.log(f"Execute action error: {e}", 'error')

    @staticmethod
    def format_action_results(action_results):
        formatted_strings = []
        for key, value in action_results.items():
            formatted_string = f"{key}:\n{value}\n\n---\n"
            formatted_strings.append(formatted_string)

        return "\n".join(formatted_strings).strip('---\n')

    @staticmethod
    def get_feedback_from_status_results(status):
        if status is not None:
            completed = status['status']

            if 'not completed' in completed:
                result = status['reason']
            else:
                result = None

            return result

    def select_action(self):
        self.selected_action = None

        task = self.task_handling.get_current_task()['document']
        self.selected_action = self.action_selection.run(task=task, feedback=self.feedback)

        if self.selected_action:
            result = f"{self.selected_action['Name']}: {self.selected_action['Description']}"
            self.logger.log_result(result, 'Action Selected')

    def determine_current_task(self):
        self.data['current_task'] = self.task_handling.get_current_task()
        if self.data['current_task'] is None:
            self.logger.log("Task list has been completed!!!", 'info')
            quit()

    def determine_status(self):
        self.task['status_result'] = self.status_agent.run(**self.task['execution_results'])
        self.display_status_result()

    def display_status_result(self):
        status = self.task['status_result']['status']
        reason = self.task['status_result']['reason']
        result = f"Status: {status}\n\nReason: {reason}"
        self.logger.log_result(result, 'Status Result')

    def display_execution_results(self):
        task_result = self.task['execution_results']['task_result']
        self.logger.log_result(task_result, 'Execution Results')

    def display_task_list(self):
        self.task_handling.show_task_list('Salience')

    def execute_task(self):
        task_result = self.exec_agent.run(summary=self.data['summary'],
                                          context=self.context,
                                          feedback=self.feedback)

        self.task['execution_results'] = {
            "task_result": task_result,
            "current_task": self.data['current_task'],
            "context": self.context,
            "Order": self.data['Order']
        }

        self.display_execution_results()

    def fetch_ordered_task_list(self):
        self.data['ordered_list'] = self.task_handling.get_ordered_task_list()

    def fetch_context(self):
        self.context = self.get_feedback_from_status_results(self.task.get('status_result'))

    def fetch_feedback(self):
        self.feedback = self.functions.user_interface.get_user_input()

    # noinspection PyTypeChecker
    def frustrate(self):
        if self.frustration < self.max_frustration:
            self.frustration += self.frustration_step
            self.frustration = min(self.frustration, self.max_frustration)
            self.action_selection.set_threshold(self.frustration)
            print("\nIncreased Frustration Level!")
        else:
            print(f"\nMax Frustration Level Reached: {self.frustration}")

    def handle_frustration(self):
        self.reason = None
        status = self.task['status_result']['status']
        self.reason = self.task['status_result']['reason']
        if status != 'completed':
            self.frustrate()
        else:
            self.frustration = self.min_frustration
            self.action_selection.set_threshold(self.frustration)

    def load_data_from_storage(self):
        try:
            self.load_results()
            self.fetch_ordered_task_list()
            self.determine_current_task()
            self.prepare_ordered_results()
        except KeyError as e:
            self.logger.log(f"Data loading error (key missing): {e}", 'error')
        except Exception as e:
            self.logger.log(f"General data loading error: {e}", 'error')

    def load_results(self):
        results = self.storage.load_collection({'collection_name': "Results", 'include': ["documents"]})
        self.data['result'] = results['documents'][0] if results['documents'] else "No results found"

    def log_results(self):
        self.logger.log(f"Execution Results: {self.task['execution_results']}", 'debug')
        self.logger.log(f"Agent Done!", 'info')

    def log_start(self):
        self.logger.log(f"Running Agent ...", 'debug')

    def prepare_ordered_results(self):
        self.data['task_ids'] = self.data['ordered_list']['ids']
        self.data['Order'] = self.data['current_task']["metadata"]["Order"]

    def set_objective(self):
        objective = self.prepare_objective()
        if objective is not None:
            self.task_creation_agent.run()

    def summarize_task(self):
        task = self.data['current_task']['document']
        self.data['summary'] = self.summarization_agent.run(query=task)
        if self.data['summary'] is not None:
            self.logger.log_result(self.data['summary'], 'Summary Agent Results')
        return self.data['summary']


if __name__ == '__main__':
    Salience().loop()
