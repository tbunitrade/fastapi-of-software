from fastapi import FastAPI
from enum import Enum

class ModelName(str, Enum):
    alexnet = "AlexNet"
    resnet = "ResNet"
    lenet = "LeNet"

app = FastAPI()

fake_items_db = [ {"item_name" : "Foo" }, {"item_name" : "Bar" }, {"item_name" : "Baz"} ]

@app.get("/items")
async def read_items( skip: int = 0, limit: int = 10 ):
    return fake_items_db[skip : skip + limit ]

# @app.get("/items/{item_id}")
# # async def read_item( item_id : int, q : str | None = None):
# #     if q:
# #         return { "item_id" : item_id, "q": q }
# #     return { "item_id" : item_id }
# async def read_item( item_id : str, q: str | None = None, short : bool = False):
#     item = { "item_id": item_id }
#     if q:
#         item.update( { "q": q })
#     if not short:
#         item.update(
#             {"description" :  "This is an amazing item that has a long description"}
#         )
#     return item
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = { " item_id" : item_id, "owner_id" : user_id }
    if q:
        item.update( {"q" : q})
    if not short:
        item.update(
            { "description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/")
async def root():
    return { "message" : "My admin area" }

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/items/{item_id}")
async def read_user_item( item_id: str, needy: str | None = None ):
    item = { "item_id" : item_id , "needy" : needy }
    return item

@app.get("/models/{model_name}")
async def get_model( model_name: ModelName ):
    if model_name is ModelName.alexnet:
        return { "model_name": model_name, "message" : "Deep learning FTW!" }
    if model_name.value == "lenet":
        return { "model_name": model_name, "message" : "LeCNN all the images"}

    return { "model_name": model_name, "message" : "Have some residuals" }


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return { "file_path": file_path }

