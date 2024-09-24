"""
Page 2
"""

import gradio as gr
import time
import json
import asyncio
import gradio as gr
import time
import base64
import os
from pydantic import BaseModel
from openai import OpenAI
from prompt import (
    conclusion_sys_prompt,
    generate_cocktail_sys_prompt,
    generate_cocktail_user_prompt,
    generate_pic_prompt,
    chat_system_prompt,
)
from openai import OpenAI
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv


env_path = r"..\.env"
load_dotenv(dotenv_path=env_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

coco_conversation_id = "asst_J1zKLuS5RQ6h3nABJTjPhEgN"
coco_gencocktail_id = "asst_CFva7BCM1jf2shOUzpeBlOzC"
coco_conversation = client.beta.assistants.retrieve(assistant_id=coco_conversation_id)
coco_gencocktail = client.beta.assistants.retrieve(assistant_id=coco_gencocktail_id)

custom_history = []
main_thread = client.beta.threads.create()


def _get_user_name():
    json_path = r".\temp\cocktail_preferences.json"
    with open(json_path, "r", encoding="utf-8") as f:
        preferences = json.load(f)
    return preferences["user_name"]


def submmit_message(history, message):
    pic_id_list = []
    text = ""

    for x in message["files"]:
        history.append(((x,), None))
        pic = client.files.create(
            file=open(x, "rb"),
            purpose="vision",
        )
        pic_id_list.append(pic.id)

    if message["text"] is None or message["text"] == "":
        text = None
    else:
        text = message["text"]
        history.append((text, None))

    custom_history.append(
        {
            "pic_id_list": pic_id_list,
            "user_text": text,
            "chatbot_text": None,
        }
    )
    return history, gr.MultimodalTextbox(value=None, interactive=True)


def chatbot_response(history):
    user_input = custom_history[-1]["user_text"]
    pic_id_list = custom_history[-1]["pic_id_list"]

    if user_input is not None:
        content_list = [{"type": "text", "text": user_input}]
    else:
        content_list = []
    for pic_id in pic_id_list:
        content_list.append({"type": "image_file", "image_file": {"file_id": pic_id}})

    # print(content_list)

    client.beta.threads.messages.create(
        thread_id=main_thread.id, role="user", content=content_list
    )

    with client.beta.threads.runs.stream(
        thread_id=main_thread.id,
        assistant_id=coco_conversation.id,
        instructions=chat_system_prompt(_get_user_name()),
    ) as stream:
        stream.until_done()
        thread_message = client.beta.threads.messages.list(thread_id=main_thread.id)
        bot_message = thread_message.data[0].content[0].text.value

    custom_history[-1]["chatbot_text"] = bot_message

    history[-1][1] = ""
    for character in bot_message:
        history[-1][1] += character
        time.sleep(0.01)
        yield history


def _combine_user_bot():
    combination = ""
    for i in range(len(custom_history)):
        if custom_history[i]["user_text"] is not None:
            combination += f"[Customer]: {custom_history[i]['user_text']}\n"
        combination += f"[Coco]: {custom_history[i]['chatbot_text']}\n"
    return combination


def _generate_conclusion():
    print("Generating conclusion...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": conclusion_sys_prompt},
            {"role": "user", "content": _combine_user_bot()},
        ],
    )

    print("Generating conclusion done!")

    class Conclusion(BaseModel):
        Emotion: str
        Summary: str

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Extract the emotion(s) of the [customer] and summarization of the chat history.",
            },
            {"role": "user", "content": response.choices[0].message.content},
        ],
        response_format=Conclusion,
    )

    print("Parsing conclusion done!")

    event = completion.choices[0].message.parsed

    return event.Emotion, event.Summary


def _generate_cocktail():
    all_pic_id_list = []
    for i in range(len(custom_history)):
        all_pic_id_list += custom_history[i]["pic_id_list"]

    mood, summary = _generate_conclusion()
    cocktail_user_prompt = generate_cocktail_user_prompt(mood, summary)
    cocktail_sys_prompt = generate_cocktail_sys_prompt()

    content_list = [{"type": "text", "text": cocktail_user_prompt}]
    for pic_id in all_pic_id_list:
        content_list.append({"type": "image_file", "image_file": {"file_id": pic_id}})

    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=content_list
    )
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=coco_gencocktail.id,
        instructions=cocktail_sys_prompt,
    ) as stream:
        stream.until_done()
        thread_message = client.beta.threads.messages.list(thread_id=thread.id)
        bot_message = thread_message.data[0].content[0].text.value

    return bot_message


# async def _extract_cocktial_details(bot_msg):
def _extract_cocktial_details(bot_msg):
    class CocktailDetails(BaseModel):
        name: str
        recipe: str
        preparation_steps: str
        reason: str

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Extract the <name>, <recipe>, <preparation_steps>, and <reason> from the description of the cocktail.",
            },
            {"role": "user", "content": bot_msg},
        ],
        response_format=CocktailDetails,
    )

    print("Parsing cocktail details done!")

    details = completion.choices[0].message.parsed
    return details.name, details.recipe, details.preparation_steps, details.reason


# async def _generate_picture(bot_msg):
def _generate_picture(bot_msg):
    pic_prompt = generate_pic_prompt(bot_msg)
    response = client.images.generate(
        model="dall-e-3",
        prompt=pic_prompt,
        size="1024x1024",
        quality="hd",
        n=1,
        response_format="b64_json",
    )
    image_base64 = response.data[0].b64_json
    image_data = base64.b64decode(image_base64)

    # 将二进制数据转换为图片
    image = Image.open(BytesIO(image_data))

    # 定义图片保存的目录
    save_dir = "../generated/cocktail_images"
    os.makedirs(save_dir, exist_ok=True)

    # 使用时间戳命名文件
    file_name = f"{time.time()}.png"
    file_path = os.path.join(save_dir, file_name)
    image.save(file_path)

    return file_path


# async def on_click():
def on_click():
    loading_gif_path = r"..\static\images\make_cocktail.gif"  # 替换为你的GIF路径
    yield (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(value="制作中🦙 请稍候..."),  # 更新 textbox1
        gr.update(value="制作中🦙 请稍候..."),  # 更新 textbox2
        gr.update(value="制作中🦙 请稍候..."),  # 更新 textbox3
        loading_gif_path,  # 更新 image_output 显示GIF
    )

    bot_msg = _generate_cocktail()
    name, recipe, preparation_steps, reason = _extract_cocktial_details(bot_msg)
    file_path = _generate_picture(bot_msg)
    name_recipe = name + "\n\n" + recipe

    yield (
        gr.update(),
        gr.update(),
        gr.update(value=name_recipe),  # 更新 textbox1
        gr.update(value=preparation_steps),  # 更新 textbox2
        gr.update(value=reason),  # 更新 textbox3
        file_path,  # 更新 image_output 显示生成的图片
    )

    # 保存用户所有信息
    json_path = r".\temp\cocktail_preferences.json"
    with open(json_path, "r", encoding="utf-8") as f:
        preferences = json.load(f)
    user_name = preferences["user_name"]
    info_dict = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "user_name": user_name,
        "user_preferences": preferences,
        "generated_cocktail": {
            "name": name,
            "recipe": recipe,
            "preparation_steps": preparation_steps,
            "reason": reason,
            "image": file_path,
        },
    }
    # 保存用户信息
    file_name = f"{user_name}_{time.time()}.json"
    save_path = os.path.join(r"..\generated\user_info", file_name)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(info_dict, f, ensure_ascii=False, indent=4)


def page2_content():
    # fill_height=True, css=r"../static/css/custom_style.css"
    with gr.Column(visible=False) as page2:
        chatbot = gr.Chatbot(
            label="Coco",
            bubble_full_width=True,
            scale=1,
            avatar_images=[
                r"..\static\images\user_avator.png",
                r"..\static\images\Coco_avator.png",
            ],
            likeable=False,
            value=[
                (
                    None,
                    f"你好{_get_user_name()}，我是你的调酒师Coco。最近过得怎么样呢？有什么想和我分享的吗？😺",
                )
            ],
        )
        chat_input = gr.MultimodalTextbox(
            interactive=True,
            placeholder="Enter message or upload image...",
            show_label=False,
            file_types=["image", "text"],
            # scale=1,
        )
        submit_btn = gr.Button(
            value="分享完毕 开始调酒:D",
        )

    return (
        page2,
        chatbot,
        chat_input,
        submit_btn,
    )


if __name__ == "__main__":
    with gr.Blocks(fill_height=True, css=r"../static/css/custom_style.css") as demo:
        page2, chatbot, chat_input, submit_btn_2 = page2_content()
        chat_msg = chat_input.submit(
            submmit_message,
            [chatbot, chat_input],
            [chatbot, chat_input],
            queue=False,
            show_progress="hidden",
        )
        bot_msg = chat_msg.then(
            chatbot_response,
            chatbot,
            chatbot,
            show_progress="hidden",
        )
        submit_btn_2.click(on_click, None, None)
    demo.launch()
