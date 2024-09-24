import gradio as gr
from submit_preference import save_preferences, page1_content
from coco_chatbot import submmit_message, chatbot_response, on_click, page2_content
from generate_cocktail import page3_content

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

    (
        page2,
        chatbot,
        chat_input,
        submit_btn_2,
    ) = page2_content()

    (
        page3,
        image_output,
        textbox1,
        textbox2,
        textbox3,
    ) = page3_content()

    # page1提交
    submit_btn_1.click(
        save_preferences,
        [user_name, drink_strength, taste_preferences, base_spirits, allergies],
        [output, page1, page2],
    )

    # page2对话
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
    bot_msg.then(
        lambda: gr.MultimodalTextbox(interactive=True),
        None,
        [chat_input],
    )

    submit_btn_2.click(
        on_click,
        None,
        [page2, page3, textbox1, textbox2, textbox3, image_output],
    )

if __name__ == "__main__":
    demo.launch()
