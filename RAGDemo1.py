import os
from openai import AzureOpenAI  
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  
  
endpoint = os.getenv("ENDPOINT_URL", "https://aoai-lm-demo.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
  
# Initialize Azure OpenAI client with Entra ID authentication  
cognitiveServicesResource = os.getenv('AZURE_COGNITIVE_SERVICES_RESOURCE', 'https://cognitiveservices.azure.com/')  
token_provider = get_bearer_token_provider(  
    DefaultAzureCredential(),  
    f'{cognitiveServicesResource}.default'  
)  

client = AzureOpenAI(
    azure_endpoint=endpoint,  
    azure_ad_token_provider=token_provider,  
    api_version='2024-05-01-preview',  
)
session_history=[
    {"role": "system", "content": "You are a helpful assistant that will answer the questions accurately according "
                                  "to the resources provided and make sure to add the reference at the end this way "
                                  "[Document Name + The original text provided for grounding the answer]"}
]

def get_answer(question):
    session_history.append({"role": "user", "content": question})

    completion = client.chat.completions.create(  
    model=deployment,  
    messages=session_history,  
    max_tokens=800,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,  
    stop=None,  
    extra_body={  
        "data_sources": [  
            {  
                "type": "azure_search",  
                "parameters": {  
                    "endpoint": os.environ["AISEARCH_API_ENDPOINT"],  
                    "index_name": "index40",  
                    "authentication": {  
                        "type": "system_assigned_managed_identity"  
                    }  
                }  
            }  
        ]
        }  
    )
    role = completion.choices[0].message.role
    answer = completion.choices[0].message.content
    print(f"{role}: {answer}")
    session_history.append({"role": role, "content": answer})

while True:
    get_answer(input("Your question: "))

