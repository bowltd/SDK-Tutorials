from openai import OpenAI

assistant_id = "asst_NdK71s1NYEAbuSz3ewkN0tAY"

client = OpenAI()
response = client.beta.assistants.delete(assistant_id)
print(response)