import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CertificationSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MovieBaseSchema(BaseModel):
    name: str = Field(..., max_length=255)
    year: int = Field(..., ge=1888)
    time: int = Field(..., gt=0)
    imdb: float = Field(..., ge=0, le=10)
    votes: int = Field(..., ge=0)

    meta_score: Optional[float] = Field(None, ge=0, le=100)
    gross: Optional[float] = Field(None, ge=0)

    description: str
    price: float = Field(..., ge=0)

    certification_id: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int):
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year + 1:
            raise ValueError("Invalid release year")
        return value

    model_config = {"from_attributes": True}


class MovieCreateSchema(MovieBaseSchema):
    genres: List[int]
    directors: List[int]
    stars: List[int]


class MovieUpdateSchema(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = Field(None, ge=1888)
    time: Optional[int] = Field(None, gt=0)
    imdb: Optional[float] = Field(None, ge=0, le=10)
    votes: Optional[int] = Field(None, ge=0)

    meta_score: Optional[float] = Field(None, ge=0, le=100)
    gross: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)

    certification_id: Optional[int] = None
    genres: Optional[List[int]] = None
    directors: Optional[List[int]] = None
    stars: Optional[List[int]] = None

    model_config = {"from_attributes": True}


class MovieListItemSchema(BaseModel):
    id: int
    uuid: uuid.UUID
    name: str
    year: int
    imdb: float
    price: float

    model_config = {"from_attributes": True}


class MovieDetailSchema(BaseModel):
    id: int
    uuid: uuid.UUID

    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]

    description: str
    price: float

    certification: CertificationSchema
    genres: List[GenreSchema]
    directors: List[DirectorSchema]
    stars: List[StarSchema]

    model_config = {"from_attributes": True}


class MovieListResponseSchema(BaseModel):
    items: List[MovieListItemSchema]
    total: int
    page: int
    pages: int

    model_config = {"from_attributes": True}