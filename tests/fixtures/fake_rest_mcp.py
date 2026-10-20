"""Offline subprocess fixture implementing the relevant upstream MCP contract."""
import json
import sys

for line in sys.stdin:
    message = json.loads(line)
    if "id" not in message:
        continue
    method = message["method"]
    if method == "initialize":
        data = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                "serverInfo": {"name": "fixture", "version": "1"}}
    elif method == "tools/list":
        data = {"tools": [{"name": "get_task", "inputSchema": {"type": "object"}}]}
    else:
        data = {"content": [{"type": "text", "text": json.dumps({"id": message["params"]["arguments"]["task_id"]})}]}
    print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": data}), flush=True)
