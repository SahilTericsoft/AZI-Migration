"""Request schemas for the user service.

Field names are camelCase to match the legacy API payloads. Most update/list
fields are optional so a single endpoint can cover several legacy ones.
"""

from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ----------------------------------------------------------------- auth
class LoginIn(BaseModel):
    emailId: EmailStr
    password: str = Field(min_length=8)


class UserIdIn(BaseModel):
    userId: int


class VerifyPasswordIn(BaseModel):
    userId: int
    password: str = Field(min_length=8)


class ForgotPasswordIn(BaseModel):
    emailId: EmailStr
    newPassword: str = Field(min_length=8)
    sendEmail: bool = False  # True => also notify the user (legacy forgotManualPassword)


class EmailIn(BaseModel):
    emailId: EmailStr


# ----------------------------------------------------------------- users
class UserCreateIn(BaseModel):
    firstName: str
    lastName: str
    loginUserId: int  # who is creating the user
    password: str | None = Field(default=None, min_length=8)
    roleId: int | None = None
    roleCode: str | None = None
    emailId: EmailStr | None = None
    middleName: str | None = None
    mobileNumber: str | None = None
    mobileNumberCode: str | None = None
    secondaryMobileNumber: str | None = None
    faxNumber: str | None = None
    addressLine1: str | None = None
    addressLine2: str | None = None
    zipcode: str | None = None
    state: str | None = None
    city: str | None = None
    gender: str | None = None
    dateOfBirth: str | None = None
    designation: str | None = None
    specialityType: str | None = None
    npiNumber: str | None = None
    pTanNumber: str | None = None
    tinNumber: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    taxonomyDetails: Any | None = None
    isPhysician: bool = False
    isEmailVerified: bool = False
    isSameAddress: bool = False
    isActive: bool = True
    signature: str | None = None
    shouldSendEmail: bool = False


class UserListIn(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    roleId: int | None = None
    roleIds: list[int] | None = None
    roleCodes: list[str] | None = None
    gender: str | None = None
    genders: list[str] | None = None
    userIds: list[int] | None = None
    isPhysician: bool | None = None
    isActive: bool | None = None
    startDate: str | None = None
    endDate: str | None = None
    appliedAttributes: list[str] | None = None


class UserViewIn(BaseModel):
    userId: int | None = None
    emailId: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    npiNumber: str | None = None
    appliedAttributes: list[str] | None = None


class UserUpdateIn(BaseModel):
    # Target: one user (userId) or many (userIds = bulk edit).
    userId: int | None = None
    userIds: list[int] | None = None
    # Any user column may be supplied; extras are ignored against the model.
    model_config = {"extra": "allow"}


class UserValidateIn(BaseModel):
    emailId: str
    npiNumber: str | None = None


# --------------------------------------------------------- access control
class AclRule(BaseModel):
    module: str
    code: str
    feature: str | None = None
    isAccessible: bool | None = None


class AclModuleIn(BaseModel):
    # Add one module or many (bulk). `seed=True` loads the built-in default set.
    modules: list[dict[str, Any]] | None = None
    module: str | None = None
    feature: str | None = None
    code: str | None = None
    description: str | None = None
    apis: list[str] | None = None
    seed: bool = False


class RoleCreateIn(BaseModel):
    role: str
    aclRules: list[AclRule] = Field(default_factory=list)


class RolePermissionsIn(BaseModel):
    aclRules: list[AclRule]


class AssignUserRoleIn(BaseModel):
    roleId: int
    aclRules: list[AclRule] = Field(default_factory=list)
    isHybrid: bool | None = None
    isActive: bool | None = None


# ------------------------------------------------------------ static data
class GeoAddIn(BaseModel):
    address: list[dict[str, Any]]


class GeoDeleteIn(BaseModel):
    zipcodes: list[str]


class DropdownUpsertIn(BaseModel):
    title: str
    value: list[dict[str, Any]]


class DropdownDeleteIn(BaseModel):
    title: str
    codes: list[str]
