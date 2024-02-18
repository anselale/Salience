from agentforge.agent import Agent


class ExecutionAgent(Agent):
    """
    An agent subclass for executing tasks or actions, inheriting all behaviors and properties of the Agent class.

    The ExecutionAgent class is a prime example of the easiness in creating agents. When an instance of
    ExecutionAgent is run, the system utilizes the class name ("ExecutionAgent") to locate and select the appropriate
    YAML file containing prompt templates. This automatic mapping between the agent class name and the prompt template
    YAML file allows for a convention-over-configuration approach, streamlining the process of prompt generation
    based on the agent's type.

    This mechanism ensures that each type of agent can have its unique set of prompt templates, defined in a
    corresponding YAML file, which are automatically used when rendering prompts for that agent.
    """
    pass
