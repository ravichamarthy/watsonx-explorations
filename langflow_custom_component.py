# Import base class for creating custom LangFlow components
from langflow.custom.custom_component.component import Component
# Import input and output types for defining component interfaces
from langflow.io import MessageTextInput, Output
# Import Data schema for returning structured results
from langflow.schema.data import Data

# Imports from IBM watsonx.governance SDK
from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.metrics import ContextRelevanceMetric
from ibm_watsonx_gov.entities.enums import TaskType, MetricGroup
from ibm_watsonx_gov.evaluators import MetricsEvaluator
from ibm_watsonx_gov.metrics import AnswerRelevanceMetric
from ibm_watsonx_gov.metrics import FaithfulnessMetric
from ibm_watsonx_gov.metrics import TextGradeLevelMetric
from ibm_watsonx_gov.metrics import TextReadingEaseMetric

import pandas as pd

# IBM watsonx.governance credentials (replace with your own)
WATSONX_APIKEY = "[Your IBM Cloud API Key]"
WXG_SERVICE_INSTANCE_ID = "[Your IBM watsonx.governance Service Instance ID]"

# Configuration for mapping flow inputs to evaluation fields
config = GenAIConfiguration(
    input_fields=["question"],   # user query
    context_fields=["context"],  # retrieved context
    output_fields=["answer"],    # LLM generated response
    reference_fields=[]          # (optional) ground truth references
)

# List of metrics to evaluate on question, context, and answer
metrics = [
    AnswerRelevanceMetric(),     # how relevant is the answer to the question
    FaithfulnessMetric(),        # is the answer grounded in the context
    ContextRelevanceMetric(),    # is the retrieved context relevant to the question
    TextGradeLevelMetric(),      # readability grade level
    TextReadingEaseMetric(),     # readability ease score
]

'''
Define a custom LangFlow component

This custom component takes the question, retrieved context, and generated answer as inputs, 
and uses the IBM watsonx.governance SDK to compute evaluation metrics such as answer relevance, 
faithfulness, context relevance, and readability. The results are returned as structured data back 
into the LangFlow pipeline, making it easy to automatically assess the quality of each response.
'''
class CustomComponent(Component):
    # Component metadata
    display_name = "Check Relevance Metrics"
    description = "Compute Relevance metrics based on the question, retrieved context, and the generated answer."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "code"
    name = "CustomComponent"

    # Define component inputs
    inputs = [
        MessageTextInput(
            name="context",
            display_name="context",     # retrieved context from vector DB
            info="The context that is retrieved from vector DB",
            value="Receving input",
            tool_mode=True,
        ),
        MessageTextInput(
            name="input_value",     # user's input question
            display_name="question",
            info="The question that is sent by the user",
            value="Receving input",
            tool_mode=True,
        ),
        MessageTextInput(
            name="answer",      # LLM generated answer
            display_name="answer",
            info="The answer that is retrieved from LLM",
            value="Receving input",
            tool_mode=True,
        ),        
    ]

    # Define component output
    outputs = [
        Output(display_name="Relevance Metrics", name="relevance_metrics", method="build_output"),
    ]

    # Main function to compute metrics
    def build_output(self) -> Data:
        
        # Authenticate with watsonx.governance
        credentials = Credentials(api_key=WATSONX_APIKEY,
                          service_instance_id=WXG_SERVICE_INSTANCE_ID)

        # Initialize evaluator with credentials and configuration
        evaluator = MetricsEvaluator(
            api_client=APIClient(credentials=credentials),
            configuration=config,
        )        
        
        # Build a dataframe with single row: {question, context, answer}
        input_df = pd.DataFrame([{"question": self.input_value, "context": self.context, "answer": self.answer}])

        # Run evaluation using selected metrics
        evaluation_results = evaluator.evaluate(
            data=input_df,
            metrics=metrics,
        )        
        
        # Convert results to a DataFrame, then to JSON
        evaluation_results_df = evaluation_results.to_df()
        json_obj = evaluation_results_df.to_dict(orient="records")[0]
        
        # Wrap results into a LangFlow Data object for output
        data = Data(data=json_obj)
        self.status = data
        return data