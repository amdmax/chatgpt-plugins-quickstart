import json
import os
import quart
import quart_cors
from quart import request

# app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")
app = quart.Quart(__name__)

# Keep track of todo's. Does not persist if Python session is restarted.
_developers = {}

@app.post("/clients/generate")
async def generate_client():
    request = await quart.request.get_json(force=True)
    language = request["language"]
    openapispecfile = request["spec_url"]
    os.system(f'npx @openapitools/openapi-generator-cli generate -i {openapispecfile} -g {language} -o ./output')
    return quart.Response(response='OK', status=200)

@app.post("/developers/<string:username>")
async def add_dev(username):
    request = await quart.request.get_json(force=True)
    name = request["name"]
    if name not in _developers:
        _developers[name] = []
    
    print(name)
    print(username)

    _developers[name].append(name)
    return quart.Response(response='OK', status=200)

@app.get("/developers/<string:username>")
async def get_developers(username):
    return quart.Response(response=json.dumps(_developers.get(username, [])), status=200)

@app.delete("/developers/<string:username>")
async def delete_dev(username):
    request = await quart.request.get_json(force=True)
    dev_idx = request["dev_id"]
    # fail silently, it's a simple plugin
    if 0 <= dev_idx < len(_developers[username]):
        _developers[username].pop(dev_idx)
    return quart.Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
