import os
from agentforge.utils.storage_interface import StorageInterface
from agentforge.utils.functions.Logger import Logger

from termcolor import colored, cprint
from colorama import init
init(autoreset=True)


class TaskHandling:
    """
    A class responsible for handling task-related operations, including retrieving the current task,
    organizing tasks by order, logging tasks, and displaying the task list to the user.

    Attributes:
        logger (Logger): Logger instance for logging messages and errors.
        storage (StorageInterface): StorageInterface instance for accessing storage operations.
    """

    def __init__(self):
        """
        Initializes the TaskHandling class, setting up logger and storage interface instances.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = StorageInterface()

    def get_current_task(self):
        """
        Retrieves the current task from the storage, prioritizing tasks that have not been completed yet.

        Returns: dict or None: The current task as a dictionary if available, or None if an error occurs or no tasks
        are pending.
        """
        try:
            ordered_list = self.get_ordered_task_list()

            current_task = None
            # iterate over sorted_metadatas
            for i, metadata in enumerate(ordered_list['metadatas']):
                # check if the Task Status is not completed
                if metadata['Status'] == 'not completed':
                    current_task = {'id': ordered_list['ids'][i], 'document': ordered_list['documents'][i],
                                    'metadata': metadata}
                    break  # break the loop as soon as we find the first not_completed task

            return current_task
        except Exception as e:
            self.logger.log(f"Error in fetching current task: {e}", 'error')
            return None

    def get_ordered_task_list(self):
        """
        Fetches and orders tasks by their specified order from the storage.

        Returns:
            dict: A dictionary containing ordered lists of task IDs, embeddings, documents, and metadata.
                  Returns an empty structure if an error occurs.
        """
        try:
            # Load Tasks
            self.storage.storage_utils.select_collection("Tasks")

            task_collection = self.storage.storage_utils.load_collection({'collection_name': "Tasks",
                                                                          'include': ["documents", "metadatas"]})

            # first, pair up 'ids', 'documents' and 'metadatas' for sorting
            paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'], task_collection['metadatas']))

            # sort the paired up tasks by 'Order' in 'metadatas'
            sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['Order'])

            # split the sorted tasks back into separate lists
            sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

            # create the ordered results dictionary
            ordered_list = {'ids': list(sorted_ids),
                            'embeddings': task_collection['embeddings'],
                            'documents': list(sorted_documents),
                            'metadatas': list(sorted_metadatas)}

            return ordered_list
        except Exception as e:
            self.logger.log(f"Error in fetching ordered task list: {e}", 'error')
            return {'ids': [], 'embeddings': [], 'documents': [], 'metadatas': []}

    def log_tasks(self, tasks):
        """
        Logs the given tasks to a designated file.

        Parameters:
            tasks (str): The tasks information to log.

        Raises:
            Exception: If an error occurs during the file operation.
        """
        try:
            filename = "./Results/task_results.txt"

            if not os.path.exists("./Results"):
                os.makedirs("./Results")

            with open(filename, "a") as file:
                file.write(tasks)
        except Exception as e:
            self.logger.log(f"Error in logging tasks: {e}", 'error')

    def show_task_list(self, desc):
        """
        Displays a list of tasks to the user, along with the objective and status of each task.

        Parameters:
            desc (str): A description to display along with the task list.

        Returns:
            str: A string representation of the task list and objective.

        Raises:
            Exception: If an error occurs while fetching or displaying the task list.
        """
        try:
            selected_persona = self.storage.config.data['settings']['system']['Persona']
            objective = self.storage.config.data['personas'][selected_persona]['Objective']
            self.storage.storage_utils.select_collection("Tasks")

            task_collection = self.storage.storage_utils.collection.get()
            task_list = task_collection["metadatas"]

            # Sort the task list by task order
            task_list.sort(key=lambda x: x["Order"])
            result = f"Objective: {objective}\n\nTasks:\n"

            cprint(f"\n***** {desc} - TASK LIST *****\nObjective: {objective}", 'blue', attrs=['bold'])

            for task in task_list:
                task_order = task["Order"]
                task_desc = task["Description"]
                task_status = task["Status"]

                if task_status == "completed":
                    status_text = colored("completed", 'green')
                else:
                    status_text = colored("not completed", 'red')

                print(f"{task_order}: {task_desc} - {status_text}")
                result = result + f"\n{task_order}: {task_desc}"

            cprint(f"*****", 'blue', attrs=['bold'])

            self.log_tasks(result)

            return result
        except Exception as e:
            self.logger.log(f"Error in showing task list: {e}", 'error')
            return ""
