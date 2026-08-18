#!/usr/bin/env python3
"""列出 IMA 全部知识库及其收藏条目（含子文件夹递归），输出 JSON。"""
import json, subprocess, sys

SKILL = "/home/scapegoat/.codebuddy/skills/ima-skills/ima_api.cjs"

def call(path, body):
    r = subprocess.run(["node", SKILL, path, json.dumps(body, ensure_ascii=False)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{path} failed: {r.stderr.strip()}")
    return json.loads(r.stdout.strip())

resp = call("openapi/wiki/v1/search_knowledge_base", {"query":"","cursor":"","limit":20})
kbs = resp["data"]["info_list"]
print(f"知识库数量: {len(kbs)}", file=sys.stderr)

result = {}
for kb in kbs:
    kb_id = kb["kb_id"]; kb_name = kb["kb_name"]
    items = []
    def walk(folder_id=None):
        cursor = ""
        while True:
            body = {"knowledge_base_id": kb_id, "cursor": cursor, "limit": 50}
            if folder_id:
                body["folder_id"] = folder_id
            d = call("openapi/wiki/v1/get_knowledge_list", body)["data"]
            for it in d.get("knowledge_list", []):
                it["_kb"] = kb_name
                items.append(it)
                if it.get("media_type") == 99:  # folder
                    walk(it.get("media_id"))
            if d.get("is_end"):
                break
            cursor = d.get("next_cursor", "")
            if not cursor:
                break
    try:
        walk()
    except Exception as e:
        print(f"  [warn] {kb_name}: {e}", file=sys.stderr)
    result[kb_name] = {"kb_id": kb_id, "count": len(items), "items": items}
    print(f"  {kb_name}: {len(items)} 条", file=sys.stderr)

with open("/home/AI/Obsidian/知识库/肆 • 机构观点/_ima_kb_items.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("已保存 _ima_kb_items.json", file=sys.stderr)
