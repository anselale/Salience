from agentforge.agent import Agent


class SummarizationAgent(Agent):
    def run(self, text=None, query=None):
        """
        Executes the summarization process based on either a direct text input or a query to fetch relevant text.

        If a query is provided, it executes a search to fetch relevant text and then summarizes it. If direct text
        is provided, it proceeds to summarize that text directly.

        Parameters:
            text (str, optional): The text to be summarized directly.
            query (str, optional): A query string to fetch relevant text for summarization.

        Returns:
            str or None: The summarized text if successful, or None if an error occurs during the process.
        """
        try:
            if query:
                return self.run_query(query)
            else:
                return self.summarize(text)
        except Exception as e:
            self.logger.log(f"Error Running Summarization Agent: {e}", 'error')
            return None

    def run_query(self, query):
        """
        Fetches text based on a query and then summarizes it.

        Parameters:
            query (str): The query string used to fetch relevant text for summarization.

        Returns:
            str or None: The summarized text if successful, or None if an error occurs during the process.
        """
        try:
            text = self.get_search_results(query)
            if text:
                return self.summarize(text)
        except Exception as e:
            self.logger.log(f"Error running query: {e}", 'error')
            return None

    def get_search_results(self, query):
        """
        Performs a search query against a stored collection of results and fetches relevant text.

        Parameters:
            query (str): The query string to search for relevant documents.

        Returns:
            str or None: A concatenated string of search results if successful, or None if an error occurs.
        """
        try:
            params = {'collection_name': "Results", 'query': query}
            search_results = self.storage.query_memory(params, 5).get('documents')

            text = None
            if search_results:
                text = "\n".join(search_results[0])

            return text
        except Exception as e:
            self.logger.log(f"Error fetching search results: {e}", 'error')
            return None

    def summarize(self, text):
        """
        Summarizes the provided text.

        Parameters:
            text (str): The text to be summarized.

        Returns:
            str or None: The summarized text if successful, or None if an error occurs during summarization.
        """
        try:
            return super().run(text=text)
        except Exception as e:
            self.logger.log(f"Error summarizing text: {e}", 'error')
            return None

    def build_output(self):
        """
        Parses the summarization result and extracts the summary from it.

        This method attempts to parse the result (expected to be in YAML format) and extract the 'summary' field as
        the output. If parsing fails, it defaults to using the raw result as the output.
        """
        try:
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)
            self.output = parsed_yaml.get("summary", "").lower().strip()
        except Exception as e:
            self.logger.parsing_error(self.result, e)
            self.output = self.result
