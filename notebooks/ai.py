import os
from dotenv import load_dotenv
load_dotenv()
import openai
import re

openai.api_key = os.environ["OPENAI_API_KEY"]

def __extract_sql_code(markdown_string: str) -> str:
    # Regex pattern to match SQL code blocks
    pattern = r"```[\w\s]*sql\n([\s\S]*?)```|```([\s\S]*?)```"

    # Find all matches in the markdown string
    matches = re.findall(pattern, markdown_string, re.IGNORECASE)

    # Extract the SQL code from the matches
    sql_code = []
    for match in matches:
        sql = match[0] if match[0] else match[1]
        sql_code.append(sql.strip())

    if len(sql_code) == 0:
        if '\n\n\n' in markdown_string:
            return markdown_string.split('\n\n\n')[-1]
            
        return markdown_string

    return sql_code[0]

def send_to_openai_chat(model, message_log) -> str:    
    response = openai.ChatCompletion.create(model=model, messages=message_log, max_tokens=500, stop=None, temperature=0.7)
    
    for choice in response.choices:
        if "text" in choice:
            return __extract_sql_code(choice.text)
            
    return __extract_sql_code(response.choices[0].message.content)

import vertexai
from vertexai.language_models import CodeGenerationModel

vertexai.init(project=os.environ['GCP_PROJECT'], location=os.environ['GCP_REGION'])

def send_to_vertexai(message_log) -> str:
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 2048
    }
    model = CodeGenerationModel.from_pretrained("code-bison@001")
    response = model.predict(
        prefix = message_log,
        **parameters
    )

    sql = response.text

    return __extract_sql_code(sql)

import replicate

def send_to_replicate(message_log) -> str:
    output = replicate.run(
        "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
        input={"prompt": message_log}
    )
    # The replicate/llama-2-70b-chat model can stream output as it's running.
    # The predict method returns an iterator, and you can iterate over that output.

    result = ""
    for item in output:
        # https://replicate.com/replicate/llama-2-70b-chat/versions/2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1/api#output-schema
        result += item

    sql = result

    return __extract_sql_code(sql)
