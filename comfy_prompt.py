import json
import requests
import time
import os
import cv2

PROMPT_FILE = "prompt.json"
OUTPUT_DIR = "/home/tst/comfy-ui/ComfyUI/output"

# Variable to keep track of the last image modification time globally
last_img_time = 0

# Initialize last_img_time to the latest image time from the folder if images exist
def initialize_last_img_time():
    global last_img_time
    try:
        files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
            reverse=True
        )

        if files:
            img_path = os.path.join(OUTPUT_DIR, files[0])
            last_img_time = os.path.getmtime(img_path)
            print(f"✅ Last image time initialized to: {last_img_time}")
        else:
            print("⚠️ No images found in the output folder.")
    except Exception as e:
        print("❌ Error initializing last image time:", e)

def send_prompt(user_prompt):
    try:
        with open(PROMPT_FILE, "r") as f:
            workflow = json.load(f)

        # Update the prompt text in CLIPTextEncode
        for node_id, node in workflow["prompt"].items():
            if node["class_type"] == "CLIPTextEncode" and "text" in node["inputs"]:
                node["inputs"]["text"] = user_prompt
                break

        response = requests.post("http://127.0.0.1:8188/prompt", json=workflow)

        if response.status_code == 200:
            print("✅ Prompt submitted. Waiting for generation...")
            wait_for_image()
        else:
            print("❌ Error from ComfyUI:", response.text)

    except Exception as e:
        print("❌ Error:", e)

def wait_for_image():
    global last_img_time  # Use the global variable

    while True:
        try:
            files = sorted(
                [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")],
                key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
                reverse=True
            )

            if files:
                img_path = os.path.join(OUTPUT_DIR, files[0])
                img_time = os.path.getmtime(img_path)

                # If the image is newly modified, display it
                if img_time > last_img_time:
                    last_img_time = img_time  # Update the last image modification time
                    img = cv2.imread(img_path)
                    if img is not None:
                        cv2.imshow("Generated Image", img)
                        print("🖼️ Displaying latest image:", img_path)
                        cv2.waitKey(0)  # Wait until key press
                        cv2.destroyAllWindows()
                        break  # Exit the loop after showing the image
                else:
                    print("⏳ Waiting for new image...")

        except Exception as e:
            print("❌ Error loading image:", e)

        time.sleep(1)  # Wait 1 second before checking again

if __name__ == "__main__":
    # Initialize last_img_time before starting
    initialize_last_img_time()

    while True:
        user_prompt = input("📝 Enter your prompt: ")
        send_prompt(user_prompt)
