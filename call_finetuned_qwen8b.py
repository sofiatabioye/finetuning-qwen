# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("image-to-text", model="sophy/qwen3-vl-8b-referral-forms")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
            {"type": "text", "text": "What animal is on the candy?"}
        ]
    },
]

messages2 = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/sophy/referrals-image-to-json-chat/resolve/main/images/2WW form%20for%20suspected%20colon%20cancer%20IOV21_page_1.png"},
            {"type": "text", "text": "Extract the referral form data with their bounding boxes in JSON format?"}
        ]
    }
]

# For local images, use "image" key (not "path") with the file path as a string
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": "images/2WW form for suspected colon cancer IOV21_page_1.png"},  # Use "image" key, not "path"
            {"type": "text", "text": "Extract the referral form data with their bounding boxes in JSON format?"}
        ]
    }
]

# Alternative: Load as PIL Image first (more explicit)
# from PIL import Image
# image = Image.open("images/2WW form for suspected colon cancer IOV21_page_1.png").convert("RGB")
# messages = [
#     {
#         "role": "user",
#         "content": [
#             {"type": "image", "image": image},  # PIL Image object
#             {"type": "text", "text": "Extract the referral form data with their bounding boxes in JSON format?"}
#         ]
#     }
# ]
# For image-to-text pipeline with messages, pass messages directly
result = pipe(messages)
print(result)

# Or use messages2 for the referral form
# result2 = pipe(messages2)
# print(result2)