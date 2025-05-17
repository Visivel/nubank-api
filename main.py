import fastapi
import aiofiles
import os
import uvicorn
import json
import random
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

app = fastapi.FastAPI()

app.mount("/imagens", StaticFiles(directory="imagens"), name="imagens")

sites = Jinja2Templates(directory="sites")

tempsenha = None

@app.get("/")
async def root():
    try:
        imagens = os.listdir("imagens")
        if not imagens:
            return JSONResponse(
                status_code=404,
                content={"message": "nenhuma imagem encontrada"}
            )
        
        random.seed()
        imagem = random.choice(imagens)
        
        async with aiofiles.open(f"imagens/{imagem}", mode="rb") as f:
            return fastapi.responses.Response(
                await f.read(),
                media_type=f"image/{imagem.split('.')[-1]}"
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"erro pra pegar a imagem: {str(e)}"}
        )

@app.get("/admin")
async def admin(request: Request):
    try:
        if not tempsenha:
            return RedirectResponse(url="/login")
        
        imagens = os.listdir("imagens")
        
        return sites.TemplateResponse("index.html", {
            "request": request,
            "imagens": imagens,
            "senha": tempsenha
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"erro no admin: {str(e)}"}
        )

@app.get("/login")
async def login_get(request: Request):
    return sites.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, senha: str = Form(...)):
    try:
        config_senha = json.load(open("config.json")).get("senha")
        if senha == config_senha:
            global tempsenha
            tempsenha = senha
            return RedirectResponse(url="/admin", status_code=303)
        else:
            return sites.TemplateResponse("login.html", {
                "request": request,
                "error": "erro ao fazer login"
            })
    except Exception as e:
        return sites.TemplateResponse("login.html", {
            "request": request,
            "error": "erro ao fazer login"
        })

# Sim eu deixei esse endpoint aqui caso um dia precise
@app.post("/remover")
async def remover(senha: str = Form(...), imagem: str = Form(...)):
    if senha != tempsenha:
        return JSONResponse(
            status_code=401,
            content={"message": "senha invalida"}
        )
    
    if imagem not in os.listdir("imagens"):
        return JSONResponse(
            status_code=404,
            content={"message": "imagem nao encontrada"}
        )
    
    os.remove(f"imagens/{imagem}")
    
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/login")
async def login_get(request: Request):
    return sites.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, senha: str = Form(...)):
    try:
        config_senha = json.load(open("config.json")).get("senha")
        if senha == config_senha:
            global tempsenha
            tempsenha = senha
            return RedirectResponse(url="/", status_code=303)
        else:
            return sites.TemplateResponse("login.html", {
                "request": request,
                "error": "Senha incorreta"
            })
    except Exception as e:
        return sites.TemplateResponse("login.html", {
            "request": request,
            "error": "erro ao fazer login"
        })

# @app.post("/remover")
# async def remover(request: Request):
#     try:
#         form = await request.form()
        
#         if not form.get("senha") or not form.get("imagem"):
#             return JSONResponse(
#                 status_code=400,
#                 content={"message": "senha e imagem sao obrigatorios"}
#             )
        
#         if form.get("senha") != tempsenha:
#             return JSONResponse(
#                 status_code=401,
#                 content={"message": "senha invalida"}
#             )
        
#         if form.get("imagem") not in os.listdir("imagens"):
#             return JSONResponse(
#                 status_code=404,
#                 content={"message": "imagem nao encontrada"}
#             )
        
#         os.remove(f"imagens/{form.get("imagem")}")
        
#         return RedirectResponse(url="/", status_code=303)
#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={"message": f"erro ao remover: {str(e)}"}
#         )

@app.get("/upload")
async def upload_get(request: Request):
    if not tempsenha:
        return RedirectResponse(url="/login")
    return sites.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_post(request: Request):
    if not tempsenha:
        return RedirectResponse(url="/login")
    
    try:
        form = await request.form()
        
        if not form.get("senha") or not form.get("file"):
            return sites.TemplateResponse("upload.html", {
                "request": request,
                "error": "voce nao inseriu a senha/arquivo"
            })
        
        if form.get("senha") != tempsenha:
            return sites.TemplateResponse("upload.html", {
                "request": request,
                "error": "Senha incorreta"
            })
        
        arquivo = os.path.join("imagens", form.get("file").filename)
        async with aiofiles.open(arquivo, 'wb') as f:
            content = await form.get("file").read()
            await f.write(content)
        
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"erro no upload: {str(e)}"}
        )

    # @app.post("/remover")
    # async def remover(senha: str = Form(...), imagem: str = Form(...)):
    #     if senha != tempsenha:
    #         return JSONResponse(
    #             status_code=401,
    #             content={"message": "senha invalida"}
    #         )
        
    #     if imagem not in os.listdir("imagens"):
    #         return JSONResponse(
    #             status_code=404,
    #             content={"message": "imagem nao encontrada"}
    #         )
        
    #     os.remove(f"imagens/{imagem}")
        
    #     return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
