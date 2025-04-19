from langchain_core.language_models import BaseLanguageModel
from langchain_core.outputs import Generation, LLMResult
from langchain_core.messages import AIMessage
from typing import List, Optional, Any
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

class FakeLLM(BaseLanguageModel):
    @property
    def _llm_type(self) -> str:
        return "fake-llm"

    def _generate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> LLMResult:
        return LLMResult(generations=[[Generation(text="(FakeLLM Response)")]])

    def predict(self, text: str, **kwargs) -> str:
        return "(FakeLLM prediction)"

    def predict_messages(self, messages: List[Any], **kwargs) -> AIMessage:
        return AIMessage(content="(FakeLLM message prediction)")

    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs) -> Any:
        return "(FakeLLM invoked result)"


    def generate_prompt(self, prompts: List[str], **kwargs) -> LLMResult:
        return LLMResult(generations=[[Generation(text="(FakeLLM generated prompt)")]])

    def agenerate_prompt(self, prompts: List[str], **kwargs) -> LLMResult:
        return self.generate_prompt(prompts)

    def apredict(self, text: str, **kwargs) -> str:
        return self.predict(text)

    def apredict_messages(self, messages: List[Any], **kwargs) -> AIMessage:
        return self.predict_messages(messages)
