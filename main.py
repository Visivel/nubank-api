import fastapi
import aiofiles
import os
import random
import uvicorn

app = fastapi.FastAPI()

@app.get("/")
async def root():
    imagens = os.listdir("imagens")
    imagem = random.choice(imagens)

    async with aiofiles.open(f"imagens/{imagem}", mode="rb") as f:
        return fastapi.responses.Response(await f.read(), media_type=f"image/{imagem.split('.')[-1]}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)