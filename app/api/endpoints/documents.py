from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_sync_db
from app.core.security import get_current_user, allow_authenticated
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services import document_service
from app.core.config import settings
from app.services.azure_blob_service import azure_blob_service
from fastapi.responses import StreamingResponse

router = APIRouter(dependencies=[Depends(allow_authenticated)])

@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    return document_service.create_document(
        db=db,
        document=document,
        uploaded_by_email=current_user.email,
        actor_id=current_user.o365_id or str(current_user.id)
    )

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    try:
        blob_name = azure_blob_service.upload_file(file.file, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    file_size = getattr(file, "size", 0)
    if not file_size:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

    document_data = DocumentCreate(
        title=title or file.filename,
        description=description,
        file_url=blob_name,
        file_type=file.content_type,
        file_size=file_size,
        project_id=project_id
    )

    return document_service.create_document(
        db=db,
        document=document_data,
        uploaded_by_email=current_user.email,
        actor_id=current_user.o365_id or str(current_user.id)
    )

@router.get("/", response_model=List[DocumentResponse])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = Query(None),
    file_type: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db)
):
    return document_service.get_documents(
        db,
        skip=skip,
        limit=limit,
        project_id=project_id,
        file_type=file_type
    )

@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(document_id: int, db: Session = Depends(get_sync_db)):
    db_document = document_service.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.get("/{document_id}/download")
def download_document(
    document_id: int, 
    inline: bool = Query(False),
    db: Session = Depends(get_sync_db)
):
    db_document = document_service.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        blob_chunks = azure_blob_service.download_file(db_document.file_url)
        props = azure_blob_service.get_blob_properties(db_document.file_url)
        media_type = props.content_settings.content_type or "application/octet-stream"
        
        disposition = "inline" if inline else "attachment"
        
        return StreamingResponse(
            blob_chunks, 
            media_type=media_type,
            headers={"Content-Disposition": f'{disposition}; filename="{db_document.title}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found in storage: {str(e)}")

@router.put("/{document_id}", response_model=DocumentResponse, dependencies=[Depends(allow_authenticated)])
def update_document(document_id: int, document: DocumentUpdate, db: Session = Depends(get_sync_db), current_user = Depends(allow_authenticated)):
    db_document = document_service.update_document(db, document_id=document_id, document_update=document, actor_id=current_user.o365_id or str(current_user.id))
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.delete("/{document_id}", status_code=204, dependencies=[Depends(allow_authenticated)])
def delete_document(document_id: int, db: Session = Depends(get_sync_db), current_user = Depends(allow_authenticated)):
    db_document = document_service.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    blob_name = db_document.file_url
    success = document_service.delete_document(db, document_id=document_id, actor_id=current_user.o365_id or str(current_user.id))
    
    if success and blob_name:
        azure_blob_service.delete_file(blob_name)
    elif not success:
        raise HTTPException(status_code=404, detail="Document not found")
