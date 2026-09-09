from pydantic import BaseModel

class Vote(BaseModel):
    user_id: int
    post_id: int