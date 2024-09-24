"""
Page 3
"""

import gradio as gr
import time
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import json
import asyncio
import base64
from pydantic import BaseModel
from prompt import generate_pic_prompt


# 预定义的 Textbox 内容
textbox1_content = "UwU"
textbox2_content = "TwT"
textbox3_content = "QwQ"


def page3_content():
    with gr.Blocks(css=".scroll-hide { height: 100%; !important }") as demo:
        with gr.Row(equal_height=True, visible=False) as page3:
            # gr.Image 用于显示生成的图片
            image_output = gr.Image(label="🍸", type="filepath")

            # 预定义的三个 Textbox
            textbox1 = gr.Textbox(
                label="配方", value=textbox1_content, lines=20, show_copy_button=True
            )
            textbox2 = gr.Textbox(label="制作步骤", value=textbox2_content, lines=20)
            textbox3 = gr.Textbox(label="制作缘由", value=textbox3_content, lines=20)
    return page3, image_output, textbox1, textbox2, textbox3
