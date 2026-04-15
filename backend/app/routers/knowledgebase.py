from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import KBArticle, KBCategory, User, UserRole
from app.dependencies import get_current_user
from app import schemas

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])

# --- Categories ---

@router.post("/categories", response_model=schemas.KBCategoryResponse, status_code=201)
def create_category(
    cat_in: schemas.KBCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    new_cat = KBCategory(
        tenant_id=current_user.tenant_id,
        name=cat_in.name,
        description=cat_in.description,
        icon=cat_in.icon
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.get("/categories", response_model=List[schemas.KBCategoryResponse])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(KBCategory).filter(KBCategory.tenant_id == current_user.tenant_id).all()

# --- Articles ---

@router.post("/articles", response_model=schemas.KBArticleResponse, status_code=201)
def create_article(
    art_in: schemas.KBArticleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Verify category exists
    cat = db.query(KBCategory).filter(
        KBCategory.id == art_in.category_id,
        KBCategory.tenant_id == current_user.tenant_id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    new_art = KBArticle(
        tenant_id=current_user.tenant_id,
        category_id=art_in.category_id,
        title=art_in.title,
        content=art_in.content,
        is_published=art_in.is_published,
        created_by=current_user.id
    )
    db.add(new_art)
    db.commit()
    db.refresh(new_art)
    return new_art

@router.get("/articles", response_model=List[schemas.KBArticleResponse])
def list_articles(
    category_id: Optional[int] = Query(None),
    only_published: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(KBArticle).filter(KBArticle.tenant_id == current_user.tenant_id)
    
    if category_id:
        query = query.filter(KBArticle.category_id == category_id)
    
    if only_published and current_user.role == UserRole.CLIENT:
        query = query.filter(KBArticle.is_published == True)
        
    return query.all()

@router.get("/articles/{article_id}", response_model=schemas.KBArticleResponse)
def get_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(KBArticle).filter(
        KBArticle.id == article_id,
        KBArticle.tenant_id == current_user.tenant_id
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    if not article.is_published and current_user.role == UserRole.CLIENT:
         raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Increment view count
    article.view_count += 1
    db.commit()
    db.refresh(article)
    
    return article
