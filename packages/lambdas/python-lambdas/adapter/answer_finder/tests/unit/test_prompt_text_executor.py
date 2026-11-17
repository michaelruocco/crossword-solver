from unittest.mock import Mock

from crossword_solver_adapter_answer_finder.bedrock_conversation_config import DefaultBedrockConversationConfig
from crossword_solver_adapter_answer_finder.prompt_text_executor import PromptTextExecutor


def test_executes_prompt_with_bedrock_converse():
    client = Mock()
    client.converse.return_value = {"output": {"message": {"content": [{"text": "1A|CAT|90"}]}}}
    config = DefaultBedrockConversationConfig()
    executor = PromptTextExecutor(client, config, "test-model")

    response = executor.execute("Find candidates")

    assert response == "1A|CAT|90"
    client.converse.assert_called_once_with(
        modelId="test-model",
        messages=[{"role": "user", "content": [{"text": "Find candidates"}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 2048},
    )
