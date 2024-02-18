from agentforge.agent import Agent


class StatusAgent(Agent):
    def log_task_results(self, task, text_to_append):
        """
        Appends the results of a task to a file, including task details and any additional text provided.

        Parameters:
            task (dict): A dictionary containing task details such as its description.
            text_to_append (str): The text to be appended to the file, typically the task's result or output.

        This method attempts to open (or create if not existing) a "task_results.txt" file in the "./Results" directory
        and append the provided task details and text to it, separated by a predefined separator for readability.
        """
        try:
            filename = "./Results/task_results.txt"
            separator = "\n\n\n\n---\n\n\n\n"
            task_to_append = "\nTask: " + task['description'] + "\n\n"
            with open(filename, "a") as file:
                file.write(separator + task_to_append + text_to_append)
        except Exception as e:
            self.logger.log(f"Error logging task results: {e}", 'error')

    def parse_result(self):
        """
        Parses the result of an agent operation, expected to be in YAML format, extracting the task's status and reason.

        This method processes the YAML content to retrieve the task's status and reason for that status. It constructs
        a structured representation of the task and its outcome, which is then stored in the agent's result attribute.
        If the task is completed, it logs the task's results using the `log_task_results` method.

        Raises:
            Exception: If parsing fails or no valid YAML content is found, it logs an error and sets the result to an
            empty dictionary.
        """
        try:
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)

            if parsed_yaml is None:
                self.logger.log("No valid YAML content found in the result:", 'error')
                raise

            status = parsed_yaml.get("status", "").lower().strip()
            reason = parsed_yaml.get("reason", "").strip()

            task = {
                "task_id": self.data['current_task']['id'],
                "description": self.data['current_task']['metadata']['Description'],
                "status": status,
                "order": self.data['current_task']['metadata']['Order'],
            }

            if status == "completed":
                self.log_task_results(task, self.data['task_result'])

            self.result = {
                "task": task,
                "status": status,
                "reason": reason,
            }
        except ValueError as e:
            self.logger.log('Parsing Value Error', 'warning')
            self.logger.parsing_error(self.result, e)
            self.result = {}
        except Exception as e:
            self.logger.parsing_error(self.result, e)
            self.result = {}

    def save_status(self):
        """
        Saves the task's status, along with its description and order, to a specified collection in storage.

        This method constructs parameters for saving the task's current status to the storage system, encapsulating
        the task's ID, description, status, and order into a structured format suitable for storage.
        """
        try:
            status = self.result["status"]
            task_id = self.result["task"]["task_id"]
            text = self.result["task"]["description"]
            task_order = self.result["task"]["order"]

            params = {
                'collection_name': "Tasks",
                'ids': [task_id],
                'data': [text],
                'metadata': [{"Status": status, "Description": text, "Order": task_order}]
            }

            self.storage.save_memory(params)
        except Exception as e:
            self.logger.log(f"Error in saving status: {e}", 'error')

    def save_result(self):
        """
        Overrides the save_result method from the Agent class to specifically handle saving the task's status.

        This method encapsulates the logic for saving the task's status by invoking the `save_status` method, providing
        a specialized implementation for handling task status updates and storage.
        """
        try:
            self.save_status()
        except Exception as e:
            self.logger.log(f"Error saving result: {e}", 'error')
