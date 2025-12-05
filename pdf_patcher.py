import fitz
import json

def inspect_page(pdf_path, page_num=0):
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        layout_info = []
        for b in blocks:
            if "lines" in b:
                text_snippet = ""
                try:
                    text_snippet = b["lines"][0]["spans"][0]["text"]
                except:
                    pass
                
                layout_info.append({
                    "rect": [round(x, 1) for x in b["bbox"]],
                    "text_snippet": text_snippet[:30] + "..."
                })
        return json.dumps(layout_info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error inspecting page: {e}"

def clear_area(pdf_path, page_num, rect):
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()
        
        doc.save(pdf_path, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP)
        return f"Cleared area {rect}"
    except Exception as e:
        return f"Error clearing area: {e}"

def draw_text_absolute(pdf_path, page_num, x, y, text, fontsize=11, fontname="helv", color=(0,0,0)):
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        page.insert_text(
            fitz.Point(x, y),
            text,
            fontsize=fontsize,
            fontname=fontname,
            color=color
        )
        
        doc.save(pdf_path, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP)
        return f"Wrote '{text}' at ({x}, {y})"
    except Exception as e:
        return f"Error drawing text: {e}"

def apply_layout_change(action, args):
    path = "resume.pdf"
    
    if "args" in args:
        args = args["args"]

    try:
        if action == "inspect":
            return inspect_page(path)
        elif action == "clear":
            return clear_area(path, 0, args["rect"])
        elif action == "draw":
            c = args.get("color", [0,0,0])
            x = float(args["x"])
            y = float(args["y"])
            fs = float(args["fontsize"])
            
            return draw_text_absolute(path, 0, x, y, args["text"], fs, args.get("fontname", "helv"), c)
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Error in apply_layout_change: {e} | Args: {args}"