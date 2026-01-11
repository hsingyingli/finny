from uuid import UUID

from fastapi import APIRouter, Query

from app.api.v1.endpoints.tags.schemas import TagCreate, TagResponse, TagUpdate
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas.common import ApiResponse, EmptyResponse
from app.services.tag_service import TagService

router = APIRouter()


@router.post("")
async def create_tag(
    request: TagCreate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TagResponse]:
    """Create a new tag."""
    service = TagService(session)
    tag = await service.create(current_user_id, request)
    return ApiResponse(data=tag, message="Tag created successfully")


@router.get("")
async def get_tags(
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[list[TagResponse]]:
    """Get all tags sorted by usage count."""
    service = TagService(session)
    tags = await service.get_all(current_user_id)
    return ApiResponse(data=tags)


@router.get("/search")
async def search_tags(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    query: str = Query(...),
) -> ApiResponse[list[TagResponse]]:
    """Search tags by name."""
    service = TagService(session)
    tags = await service.search(current_user_id, query)
    return ApiResponse(data=tags)


@router.get("/batch")
async def get_tags_batch(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    ids: list[UUID] = Query(...),
) -> ApiResponse[list[TagResponse]]:
    """Get multiple tags by IDs."""
    service = TagService(session)
    tags = await service.get_by_ids(current_user_id, ids)
    return ApiResponse(data=tags)


@router.get("/{tag_id}")
async def get_tag(
    tag_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TagResponse]:
    """Get a single tag."""
    service = TagService(session)
    tag = await service.get_by_id(current_user_id, tag_id)
    return ApiResponse(data=tag)


@router.put("/{tag_id}")
async def update_tag(
    tag_id: UUID,
    request: TagUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TagResponse]:
    """Update a tag."""
    service = TagService(session)
    tag = await service.update(current_user_id, tag_id, request)
    return ApiResponse(data=tag, message="Tag updated successfully")


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[EmptyResponse]:
    """Delete a tag."""
    service = TagService(session)
    await service.delete(current_user_id, tag_id)
    return ApiResponse(data=EmptyResponse(), message="Tag deleted successfully")
