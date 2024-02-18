from agentforge.agent import Agent
import uuid


class TaskCreationAgent(Agent):
    def parse_result(self):
        """
        Parses the agent's result, extracting tasks from YAML content, and orders them.

        This method processes the YAML-formatted result to retrieve a list of tasks, assigning an order to each task.
        If no tasks are found or the result is invalid, it logs an error and sets the result to an empty list.

        Raises:
            Exception: If parsing fails or no 'tasks' key is found, it logs an error and defaults the result to [].
        """
        try:
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)

            if parsed_yaml is None or 'tasks' not in parsed_yaml:
                self.logger.log("No valid 'tasks' key found in the YAML content", 'error')
                raise

            tasks = parsed_yaml['tasks']
            ordered_tasks = [{'Order': index + 1, 'Description': task} for index, task in enumerate(tasks)]
            self.result = ordered_tasks
        except ValueError as e:
            self.logger.log('Parsing Value Error', 'warning')
            self.logger.parsing_error(self.result, e)
            self.result = []
        except Exception as e:
            self.logger.parsing_error(self.result, e)
            self.result = []

    def save_result(self):
        """
        Overrides the save_result method to delegate task saving logic to the save_tasks method.

        Catches and logs any exceptions raised during the task saving process.
        """
        try:
            self.save_tasks(self.result)
        except Exception as e:
            self.logger.log(f"Error saving result: {e}", 'error')

    def save_tasks(self, task_list):
        """
        Saves a list of tasks to storage, assigning unique identifiers and default metadata to each.

        Parameters: task_list (list of dict): A list of tasks, where each task is a dictionary containing its order
        and description.

        Each task is saved with a unique List_ID and default status of "not completed". The entire Tasks collection
        is replaced with the new set of tasks.

        Raises:
            Exception: If there's an error during task saving, it logs the error.
        """
        try:
            collection_name = "Tasks"
            self.storage.delete_collection(collection_name)

            metadatas = [{"Status": "not completed",
                          "Order": task["Order"],
                          "Description": task["Description"],
                          "List_ID": str(uuid.uuid4())} for task in task_list]
            task_orders = [str(task["Order"]) for task in task_list]
            task_desc = [task["Description"] for task in task_list]

            params = {"collection_name": collection_name, "ids": task_orders, "data": task_desc, "metadata": metadatas}
            self.storage.save_memory(params)
        except Exception as e:
            self.logger.log(f"Error saving tasks: {e}", 'error')

    def build_output(self):
        """
        Intentionally left blank to indicate no additional output processing is required for this agent.

        This method is overridden without implementation, as the TaskCreationAgent's primary function is to parse
        and save tasks, not to generate a specific output format.
        """
        pass
