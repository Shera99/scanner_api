from datetime import datetime

from pydantic import BaseModel

from src.core.utils.case import camel_to_snake, snake_to_camel


class CamelCaseModel(BaseModel):
    class Config:
        alias_generator = snake_to_camel
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True


class SnakeCaseModel(BaseModel):
    class Config:
        alias_generator = camel_to_snake
        populate_by_name = True
        from_attributes = True
