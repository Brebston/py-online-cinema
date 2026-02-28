from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from database import get_db
from database.models.movies import (
    MovieModel,
    GenreModel,
    DirectorModel,
    StarModel,
    user_favorites,
)
from database.models.accounts import UserModel
from schemas.movies import (
    MovieListResponseSchema,
    MovieListItemSchema,
    MovieDetailSchema,
)
from security.dependencies import get_current_user


router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/genres/")
async def list_genres_with_counts(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(GenreModel.id, GenreModel.name, func.count(MovieModel.id).label("movies_count"))
        .join(GenreModel.movies, isouter=True)
        .group_by(GenreModel.id)
        .order_by(GenreModel.name.asc())
    )
    res = await db.execute(stmt)
    return [{"id": row[0], "name": row[1], "movies_count": row[2]} for row in res.all()]


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),

    year: Optional[int] = None,
    min_imdb: Optional[float] = Query(None, ge=0, le=10),
    max_price: Optional[float] = None,
    search: Optional[str] = None,

    sort_by: str = Query("year", pattern="^(year|price|imdb|votes)$"),

    db: AsyncSession = Depends(get_db),
):
    stmt = select(MovieModel)

    if year:
        stmt = stmt.where(MovieModel.year == year)

    if min_imdb:
        stmt = stmt.where(MovieModel.imdb >= min_imdb)

    if max_price:
        stmt = stmt.where(MovieModel.price <= max_price)

    if search:
        search_term = f"%{search.lower()}%"
        stmt = (
            stmt.join(MovieModel.stars, isouter=True)
            .join(MovieModel.directors, isouter=True)
            .where(
                or_(
                    func.lower(MovieModel.name).like(search_term),
                    func.lower(MovieModel.description).like(search_term),
                    func.lower(StarModel.name).like(search_term),
                    func.lower(DirectorModel.name).like(search_term),
                )
            )
            .distinct()
        )

    sort_column = getattr(MovieModel, sort_by)
    stmt = stmt.order_by(sort_column.desc())

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    pages = ceil(total / size) if total else 1

    stmt = stmt.offset((page - 1) * size).limit(size)

    res = await db.execute(stmt)
    movies = res.scalars().all()

    return MovieListResponseSchema(
        items=[MovieListItemSchema.model_validate(m) for m in movies],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/{movie_id}/", response_model=MovieDetailSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)

    if not movie:
        raise HTTPException(404, "Movie not found")

    return MovieDetailSchema.model_validate(movie)


@router.get("/favorites/", response_model=MovieListResponseSchema)
async def get_favorite_movies(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    year: Optional[int] = None,
    min_imdb: Optional[float] = Query(None, ge=0, le=10),
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = Query("year", pattern="^(year|price|imdb|votes)$"),
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    stmt = (
        select(MovieModel)
        .join(user_favorites, user_favorites.c.movie_id == MovieModel.id)
        .where(user_favorites.c.user_id == user.id)
    )

    if year:
        stmt = stmt.where(MovieModel.year == year)
    if min_imdb:
        stmt = stmt.where(MovieModel.imdb >= min_imdb)
    if max_price:
        stmt = stmt.where(MovieModel.price <= max_price)

    if search:
        search_term = f"%{search.lower()}%"
        stmt = (
            stmt.join(MovieModel.stars, isouter=True)
            .join(MovieModel.directors, isouter=True)
            .where(
                or_(
                    func.lower(MovieModel.name).like(search_term),
                    func.lower(MovieModel.description).like(search_term),
                    func.lower(StarModel.name).like(search_term),
                    func.lower(DirectorModel.name).like(search_term),
                )
            )
            .distinct()
        )

    sort_column = getattr(MovieModel, sort_by)
    stmt = stmt.order_by(sort_column.desc())

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    pages = ceil(total / size) if total else 1
    stmt = stmt.offset((page - 1) * size).limit(size)

    res = await db.execute(stmt)
    movies = res.scalars().all()

    return MovieListResponseSchema(
        items=[MovieListItemSchema.model_validate(m) for m in movies],
        total=total,
        page=page,
        pages=pages,
    )


@router.post("/{movie_id}/favorite/")
async def add_to_favorites(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    await db.refresh(user)
    if movie not in user.favorites:
        user.favorites.append(movie)

    await db.commit()
    return {"message": "Added to favorites"}


@router.delete("/{movie_id}/favorite/")
async def remove_from_favorites(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    await db.refresh(user)
    if movie in user.favorites:
        user.favorites.remove(movie)
        await db.commit()

    return {"message": "Removed from favorites"}