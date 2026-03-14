from pydantic import BaseModel


class SecondaryBase(BaseModel):
    def json_(self):
        return self.model_dump(mode="json")
