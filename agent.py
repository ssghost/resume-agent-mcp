import os
import json
import subprocess
from openai import OpenAI
from pdf_patcher import apply_layout_change

client = OpenAI(
    base_url="http://localhost:11234/v1", 
    api_key="sk-local-no-key-needed"
)

def main():
    print("Agent Started (Layout Master Mode)")
    
    system_prompt = """
    You are a PDF Layout Editor. You manipulate PDF elements by coordinates.
    
    TOOLS:
    1. apply_layout_change("inspect", {}) 
       - Returns a list of text blocks with their coordinates [x0, y0, x1, y1].
       - USE THIS FIRST to find where text is located.
       
    2. apply_layout_change("clear", {"rect": [x0, y0, x1, y1]})
       - White-out (erase) a specific rectangular area.
       
    3. apply_layout_change("draw", {"x": 100, "y": 200, "text": "Hello", "fontsize": 12})
       - Write text at specific coordinates.
       
    WORKFLOW for "Change Font Size" or "Modify Style":
    1. Inspect page to get coordinates of the target text.
    2. Clear the area (use the coordinates found in step 1).
    3. Draw the text again at the same coordinates with new fontsize/style.
    
    WORKFLOW for "Delete Block":
    1. Inspect page.
    2. Clear the area of that block.
    """

    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']: break
            
            messages.append({"role": "user", "content": user_input})

            for _ in range(5): 
                print("Thinking...", end="", flush=True)
                
                try:
                    completion = client.chat.completions.create(
                        model="default",
                        messages=messages,
                        temperature=0.1,
                        stop=["<|end_of_text|>", "<|im_end|>"]
                    )
                except Exception as e:
                    print(f"\nError: {e}")
                    break

                response_text = completion.choices[0].message.content.strip()
                print("\r", end="")

                tool_call = None
                try:
                    clean_text = response_text.replace("```json", "").replace("```", "").strip()
                    if clean_text.startswith("{") and clean_text.endswith("}"):
                        tool_call = json.loads(clean_text)
                except:
                    pass

                if tool_call:
                    tool_name = tool_call.get("tool") 
                    
                    func_name = tool_name
                    args = tool_call.get("args", {})

                    if func_name == "apply_layout_change":
                        action = args.get("action") or args.get("0") 
                        real_args = args.get("args") or args
                        
                        print(f"Executing: {action} {real_args}")
                        result = apply_layout_change(action, real_args)
                    else:
                        result = "Error: Please use apply_layout_change tool."

                    display_result = str(result)[:300] + "..." if len(str(result)) > 300 else str(result)
                    print(f"Result: {display_result}")

                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({"role": "user", "content": f"Tool Output: {result}\nProceed."})
                    continue
                
                else:
                    print(f"Agent: {response_text}")
                    messages.append({"role": "assistant", "content": response_text})
                    break

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()