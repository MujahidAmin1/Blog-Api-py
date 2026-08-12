from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostPatchPublished, PostResponse
from typing import Annotated, List
from app.utils.cloudinary import upload_image, delete_image
from app.utils.dependencies import get_current_user
from app.utils.limiter import limiter

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[PostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts
    

@router.get("/unpublished", response_model=List[PostResponse])
def get_unpublished_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.published == False)
    if not posts:
        raise HTTPException(status_code=404, detail="No unpublished posts")
    return posts


@router.get("/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post



# body.model_dump() converts your Pydantic model to a plain dict — then ** unpacks it into the Post() constructor
# db.add() stages the insert
# db.commit() writes to Postgres
# db.refresh(post) re-fetches the row so you get the DB-generated fields like id and created_at

@router.post("/", status_code=201, response_model=PostResponse)
@limiter.limit("10/hour")
def create_post(
    title: Annotated[str, Form()],
    content: Annotated[str, Form()],
    published: Annotated[bool, Form()] = False,
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    img_url = None
    image_public_id = None

    if image:
        contents = image.file.read()
        result = upload_image(contents)
        img_url = result["url"]
        image_public_id = result["public_id"]

    post = Post(
        title=title,
        content=content,
        published=published,
        img_url=img_url,
        image_public_id=image_public_id,
        user_id=current_user.id
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

# exclude_unset=True is important — it means only fields the client actually sent get updated, ignoring ones left out. That's how your PostUpdate partial fields work correctly.
# setattr(post, key, value) dynamically sets attributes on the model object — Python's equivalent of Object.assign().

@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, body: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(
        Post.id == id,
        Post.user_id == current_user.id
    ).first()
    # if post.user_id != current_user.id:
    # raise HTTPException(status_code=403)
    if not post:
      raise HTTPException(status_code=404, detail="Post not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)

    return post

@router.patch("/{id}/published", response_model=PostResponse)
def patch_published(id: int, body: PostPatchPublished, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(
        Post.id == id,
        Post.user_id == current_user.id
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    setattr(post, "published", body.published)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{id}", status_code=204)
def delete_post(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.image_public_id is not None:
        delete_image(str(post.image_public_id))

    db.delete(post)
    db.commit()


