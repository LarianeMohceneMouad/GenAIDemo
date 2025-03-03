import os
from dotenv import load_dotenv
from azure.ai.inference.aio import ChatCompletionsClient
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion
from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
import asyncio


load_dotenv()  
AZURE_SEARCH_SERVICE = os.getenv("AISEARCH_API_ENDPOINT_2")
AZURE_OPENAI_ACCOUNT = os.getenv("AZURE_OPENAI_ACCOUNT")
AZURE_DEPLOYMENT_MODEL = os.getenv("DEPLOYMENT_NAME")
AZURE_COGNITIVE_SERVICES_RESOURCE = os.getenv("AZURE_COGNITIVE_SERVICES_RESOURCE")

async def main():
    chat_completion_service = AzureAIInferenceChatCompletion(
    ai_model_id=AZURE_DEPLOYMENT_MODEL,
    client=ChatCompletionsClient(
        endpoint=f"{str(AZURE_OPENAI_ACCOUNT).strip('/')}/openai/deployments/{AZURE_DEPLOYMENT_MODEL}",
        credential=DefaultAzureCredential(),
        credential_scopes=[AZURE_COGNITIVE_SERVICES_RESOURCE],
    ),
    )

    chat_prompt_execution_settings=AzureAIInferenceChatPromptExecutionSettings(
        extra_body={  
        "data_sources": [  
            {  
                "type": "azure_search",  
                "parameters": {  
                    "endpoint": AZURE_SEARCH_SERVICE,  
                    "index_name": "hotels-sample-index",  
                    "authentication": {  
                        "type": "system_assigned_managed_identity"  
                    }  
                }  
            }  
        ]
        }
    )
    chat_history = ChatHistory()
    chat_history.add_system_message("You are a friendly assistant that recommends hotels based on activities and amenities Answer the query using only the sources provided below in a friendly and concise bulleted manner. Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below.")
    
    while True:
        print("\n")
        chat_history.add_user_message(input("User:> "))
        response = chat_completion_service.get_streaming_chat_message_content(
            chat_history=chat_history,
            settings=chat_prompt_execution_settings,
        )

        chunks = []
        async for chunk in response:
            chunks.append(chunk)

        full_response = sum(chunks[1:], chunks[0])
        print(full_response)
        chat_history.add_message(full_response)
            

if __name__ == "__main__":
    asyncio.run(main())