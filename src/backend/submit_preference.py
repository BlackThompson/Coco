"""
Page 1
"""

import gradio as gr
import json
import re
import time


# Define the function to handle form submission
def save_preferences(
    user_name, drink_strength, taste_preferences, base_spirits, allergies
):
    # Function to remove text inside parentheses
    def remove_parentheses(text_list):
        return [re.sub(r"\（.*?\）", "", item) for item in text_list]

    # Clean the input data by removing parentheses
    taste_preferences = remove_parentheses(taste_preferences)
    base_spirits = remove_parentheses(base_spirits)
    allergies = remove_parentheses(allergies)

    # Create a dictionary with the selected options
    preferences = {
        "user_name": user_name,
        "drink_strength": drink_strength,
        "taste_preferences": taste_preferences,
        "base_spirits": base_spirits,
        "allergies": allergies,
        # "cocktail_type": cocktail_type,
    }

    # Save the preferences as JSON
    path = r"./temp/cocktail_preferences.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(preferences, f, ensure_ascii=False, indent=4)

    page1_hide = gr.update(visible=False)
    page2_show = gr.update(visible=True)

    return (
        "<div style='color:green; font-size: 20px; text-align: center'>提交成功！</div>",
        page1_hide,
        page2_show,
    )


# Create the Gradio interface
def page1_content():
    with gr.Column(visible=True) as page1:
        # with gr.Blocks(css="custom_style.css") as demo:
        gr.Markdown("# 🍸 Cocktail Preferences Form")

        # 提示用户填写表单,填写姓名
        user_name = gr.Textbox(
            label="您的称呼",
            placeholder="请输入您喜欢的称呼",
            lines=1,
            elem_classes=["form-group"],
        )

        # Define the form inputs
        drink_strength = gr.CheckboxGroup(
            [
                "无酒精或极低酒精度（0% - 5% ABV）",
                "轻度酒精（5% - 10% ABV）",
                "中度酒精（10% - 20% ABV）",
                "烈性酒精（20% - 30% ABV）",
                "超烈性酒精（ > 30% ABV）",
            ],
            label="1. 鸡尾酒的烈度(可多选)",
            elem_classes=["form-group"],
        )

        taste_preferences = gr.CheckboxGroup(
            [
                "清爽（通常含有柑橘类或草本植物的风味，如薄荷）",
                "甜（通常含有水果、糖浆或甜味利口酒的成分）",
                "酸（通常含有柑橘类果汁，如柠檬汁、酸橙汁）",
                "苦（通常含有苦精或其他苦味成分）",
                "强烈（通常由烈酒为主要成分）",
                "奶油或丝滑型（通常含有奶油、牛奶或蛋类成分，质地较为浓稠顺滑）",
                "辛辣型（通常含有香料、辣椒或姜，带来刺激性的口感）",
            ],
            label="2. 喜欢的口感(可多选)",
        )

        base_spirits = gr.CheckboxGroup(
            [
                "伏特加（Vodka）",
                "金酒（Gin）",
                "朗姆酒（Rum）",
                "龙舌兰（Tequila）",
                "威士忌（Whiskey）",
                "白兰地（Brandy）",
            ],
            label="3. 偏好的基酒类型(可多选)",
        )

        allergies = gr.CheckboxGroup(
            [
                "无",
                "奶制品",
                "坚果",
                "鸡蛋",
                "蜂蜜",
            ],
            label="4. 是否对某些成分过敏(可多选)",
        )

        # cocktail_type = gr.Radio(
        #     [
        #         "经典鸡尾酒（如玛格丽特、曼哈顿、莫吉托等，经过了时间的检验）",
        #         "创意特调（独属于你的鸡尾酒特调，你可以自己为他命名）",
        #     ],
        #     label="5. 偏好经典鸡尾酒还是创意特调(单选)",
        # )

        # Button to submit the form
        submit_btn = gr.Button(
            value="我完成啦:D 提交",
            size="lg",
        )

        # 使用 HTML 显示提交状态
        output = gr.HTML()

        # # Link the form submission to the function
        # submit_btn.click(
        #     save_preferences,
        #     [user_name, drink_strength, taste_preferences, base_spirits, allergies],
        #     output,
        # )

    return (
        page1,
        submit_btn,
        user_name,
        drink_strength,
        taste_preferences,
        base_spirits,
        allergies,
        output,
    )


if __name__ == "__main__":
    print("Launching the Gradio interface...")

    with gr.Blocks(fill_height=True, css=r"../static/css/custom_style.css") as demo:
        (
            page1,
            submit_btn_1,
            user_name,
            drink_strength,
            taste_preferences,
            base_spirits,
            allergies,
            output,
        ) = page1_content()

        submit_btn_1.click(
            save_preferences,
            [user_name, drink_strength, taste_preferences, base_spirits, allergies],
            output,
        )

    demo.launch()
