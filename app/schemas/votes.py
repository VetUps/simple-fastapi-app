from pydantic import BaseModel, ConfigDict

class Vote(BaseModel):
    user_id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)
    