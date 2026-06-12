"""D2C router (PHI) — customer auth, addresses, carts, kit orders."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.d2c import controller as c
from services.d2c import schemas as s

router = APIRouter(prefix="/d2c")
CUS = ["d2c: customers"]
ADR = ["d2c: addresses"]
ORD = ["d2c: orders"]


# ---- customer auth (open: signup/login/forgot) -------------------------
@router.post("/customers/sign-up", tags=CUS)
def sign_up(body: s.SignUpIn, db: Session = Depends(get_db)):
    return c.CustomerController(db).sign_up(body.model_dump(exclude_unset=True))


@router.post("/customers/login", tags=CUS)
def login(body: s.LoginIn, db: Session = Depends(get_db)):
    return c.CustomerController(db).login(body.emailId, body.password)


@router.put("/customers/forgot-password", tags=CUS)
def forgot_password(body: s.ForgotPasswordIn, db: Session = Depends(get_db)):
    return c.CustomerController(db).forgot_password(body.emailId, body.newPassword)


# ---- customer records (protected + audited) ----------------------------
@router.post("/customers/list", tags=CUS)
def list_customers(
    body: ListIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.CustomerController(db, actor_id=actor).list(body)


@router.get("/customers/{customer_id}", tags=CUS)
def get_customer(
    customer_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.CustomerController(db, actor_id=actor).get(customer_id)


@router.put("/customers/{customer_id}", tags=CUS)
def edit_customer(
    customer_id: int,
    body: s.CustomerEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.CustomerController(db, actor_id=actor).update(
        customer_id, body.model_dump(exclude_unset=True)
    )


# ---- addresses (protected) ---------------------------------------------
@router.post("/addresses", tags=ADR)
def add_address(
    body: s.AddressCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.CustomerAddressController(db, actor_id=actor).add(body.model_dump(exclude_unset=True))


@router.get("/addresses/by-customer/{customer_id}", tags=ADR)
def addresses_by_customer(
    customer_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.CustomerAddressController(db, actor_id=actor).list_by_customer(customer_id)


@router.put("/addresses/{address_id}/make-default", tags=ADR)
def make_default_address(
    address_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.CustomerAddressController(db, actor_id=actor).make_default(address_id)


@router.put("/addresses/{address_id}", tags=ADR)
def edit_address(
    address_id: int,
    body: s.AddressEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.CustomerAddressController(db, actor_id=actor).update(
        address_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/addresses/{address_id}", tags=ADR)
def delete_address(
    address_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.CustomerAddressController(db, actor_id=actor).delete(address_id)


# ---- carts ----------------------------------------------------------------
@router.post("/carts", tags=["d2c: carts"])
def add_cart(body: s.CartCreate, db: Session = Depends(get_db)):
    return c.CustomerCartController(db).create(body.model_dump(exclude_unset=True))


# ---- kit orders (protected + audited) ----------------------------------
@router.post("/orders", tags=ORD)
def place_order(
    body: s.PlaceOrderIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.D2COrderController(db, actor_id=actor).place_order(body.model_dump(exclude_unset=True))


@router.get("/orders/by-customer/{customer_id}", tags=ORD)
def orders_by_customer(
    customer_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.D2COrderController(db, actor_id=actor).list_by_customer(customer_id)


@router.get("/orders/{order_id}", tags=ORD)
def get_order(order_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)):
    return c.D2COrderController(db, actor_id=actor).get(order_id)


@router.put("/orders/{order_id}", tags=ORD)
def edit_order(
    order_id: int,
    body: s.OrderEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.D2COrderController(db, actor_id=actor).update(
        order_id, body.model_dump(exclude_unset=True)
    )
