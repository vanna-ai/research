def get_system_prompt(character_limit, ddl_list: list[str] = [], doc_list: list[str] = [], question_answer_list: list[dict] = []) -> str:
    initial_prompt = "The user provides a question and you provide SQL. You will only respond with SQL code and not with any explanations.\n\nRespond with only SQL code. Do not answer with any explanations -- just the code.\n"

    if len(ddl_list) > 0:
        initial_prompt += f"\nYou may use the following DDL statements as a reference for what tables might be available. Use responses to past questions also to guide you:\n\n"

        for ddl in ddl_list:
            if len(initial_prompt) < character_limit: # Add DDL if it fits
                initial_prompt += f"{ddl}\n\n"

    if len(doc_list) > 0:
        initial_prompt += f"The following information may or may not be useful in constructing the SQL to answer the question\n"

        for doc in doc_list:
            if len(initial_prompt) < character_limit: # Add Documentation if it fits
                initial_prompt += f"{doc}\n\n"

    if len(question_answer_list) > 0:
        initial_prompt += f"Here are some sample question and known correct SQL:\n\n"

        for question in question_answer_list:
            if len(initial_prompt) < character_limit:
                initial_prompt += f"{question['question']}\n\n{question['sql']}\n\n"

    return initial_prompt

def get_message_log_prompt(character_limit, question: str, ddl_list: list[str] = [], doc_list: list[str] = [], question_answer_list: list[dict] = []) -> list:
    messages = [ 
        {"role": "system", "content": get_system_prompt(character_limit, ddl_list=ddl_list, doc_list=doc_list)}, 
    ]

    for question_answer in question_answer_list:
        messages.append({"role": "user", "content": question_answer["question"]})
        messages.append({"role": "assistant", "content": question_answer["sql"]})

    messages.append({"role": "user", "content": question})
    
    return messages

def get_single_message_prompt(character_limit, question: str, ddl_list: list[str] = [], doc_list: list[str] = [], question_answer_list: list[dict] = []) -> str:
    msg = get_system_prompt(character_limit, ddl_list=ddl_list, doc_list=doc_list, question_answer_list=question_answer_list)

    msg += f"\n\n{question}"

    return msg