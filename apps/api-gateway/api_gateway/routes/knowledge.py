"""知识库相关路由"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.config import settings
from api_gateway.infrastructure.database import get_db
from api_gateway.infrastructure.models import KnowledgeDocumentModel, KnowledgeDocumentStatus
from api_gateway.models.schemas import (
    KnowledgeDocument as KnowledgeDocumentSchema,
    KnowledgeEmbeddingRequest,
    KnowledgeUploadResponse,
)
from api_gateway.presentation.dependencies import get_current_user

router = APIRouter(prefix="/v1/knowledge", tags=["Knowledge"])


def _to_schema(model: KnowledgeDocumentModel) -> KnowledgeDocumentSchema:
    """转换 ORM 模型为响应对象"""
    return KnowledgeDocumentSchema(
        id=str(model.id),
        filename=model.filename,
        display_name=model.display_name,
        size_bytes=model.size_bytes,
        status=model.status.value,
        chunk_count=model.chunk_count,
        embedding_model=model.embedding_model,
        created_at=model.created_at,
        updated_at=model.updated_at,
        error_message=model.error_message,
        metadata=model.metadata_json or None,
    )


@router.get("/documents", response_model=list[KnowledgeDocumentSchema], summary="文档列表")
async def list_documents(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeDocumentSchema]:
    """获取当前用户的知识库文档列表"""
    stmt = (
        select(KnowledgeDocumentModel)
        .where(KnowledgeDocumentModel.owner_id == current_user.id)
        .order_by(KnowledgeDocumentModel.updated_at.desc())
    )
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return [_to_schema(doc) for doc in documents]


@router.post(
    "/documents",
    response_model=KnowledgeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上传文档",
)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str | None = Form(default=None),
    embedding_model: str | None = Form(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeUploadResponse:
    """上传新的知识库文档"""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    try:
        meta_payload = json.loads(metadata) if metadata else None
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="metadata 必须是合法 JSON") from exc

    storage_root = Path(settings.KNOWLEDGE_STORAGE_ROOT)
    storage_root.mkdir(parents=True, exist_ok=True)

    document_id = str(uuid.uuid4())
    filename = Path(file.filename).name
    relative_path = Path(current_user.id) / f"{document_id}_{filename}"
    target_path = storage_root / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    contents = await file.read()
    size_bytes = len(contents)
    try:
        with target_path.open("wb") as out_file:
            out_file.write(contents)
    except OSError as exc:  # pragma: no cover - 文件系统错误
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="无法保存上传文件") from exc

    document = KnowledgeDocumentModel(
        id=document_id,
        owner_id=current_user.id,
        filename=filename,
        display_name=filename,
        size_bytes=size_bytes,
        status=KnowledgeDocumentStatus.UPLOADED,
        chunk_count=None,
        embedding_model=embedding_model,
        storage_path=str(relative_path),
        error_message=None,
        metadata_json=meta_payload,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return KnowledgeUploadResponse(document=_to_schema(document))


@router.post(
    "/documents/{document_id}/embed",
    response_model=KnowledgeDocumentSchema,
    summary="触发向量化",
)
async def trigger_embedding(
    document_id: str,
    payload: KnowledgeEmbeddingRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentSchema:
    """触发指定文档的向量生成（示例实现：立即标记为完成）"""
    stmt = select(KnowledgeDocumentModel).where(
        KnowledgeDocumentModel.id == document_id,
        KnowledgeDocumentModel.owner_id == current_user.id,
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    document.status = KnowledgeDocumentStatus.READY
    document.embedding_model = payload.embedding_model or document.embedding_model or "default"
    document.chunk_count = document.chunk_count or 0
    document.error_message = None
    document.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(document)

    return _to_schema(document)


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文档",
)
async def delete_document(
    document_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """删除指定文档并清理本地文件"""
    stmt = select(KnowledgeDocumentModel).where(
        KnowledgeDocumentModel.id == document_id,
        KnowledgeDocumentModel.owner_id == current_user.id,
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    file_path = Path(settings.KNOWLEDGE_STORAGE_ROOT) / document.storage_path
    try:
        if file_path.exists():
            file_path.unlink()
            # 清理空目录
            if not any(file_path.parent.iterdir()):
                file_path.parent.rmdir()
    except OSError:
        # 忽略文件系统清理错误
        pass

    await db.delete(document)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
