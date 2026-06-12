# User Service

Migrated from the old **GkUserService** (6 controllers) into **4 router files**,
consolidating ~50 legacy endpoints into **30**. One process serves it as part of
the monorepo (mounted at `/user-service`).

## What this folder contains

| File | Purpose |
| ---- | ------- |
| `models.py` | The 9 ORM tables (Users, Roles, Tokens, ACLModulesMappings, RoleAclModels, UserAclModels, StateCityStaticData, UserStaticData, SystemConfigs). Names/types match the live DB. |
| `schemas.py` | Pydantic request bodies (camelCase, matching legacy payloads). |
| `auth.py` | Login / session / password / system-config routes. |
| `users.py` | User create / list / view / update / delete / validate. |
| `access_control.py` | Roles + ACL modules + role-permission + user-permission routes. |
| `acl_seed.py` | Default ACL module catalog (seed data). |
| `static_data.py` | Geo reference data + dropdown sets. |
| `utils.py` | Small local helpers (`to_dict`, `ok`, `paginate`, internal-id generator). |
| `router.py` | Aggregates the 4 routers; included by `main.py`. |

## Conventions

- **Success** responses use `{ "message": ..., "data": ... }`.
- **Errors** use FastAPI's `{ "detail": ... }` (string, or `{field: [msgs]}` for
  validation conflicts). Body-validation failures return **422**.
- Passwords: bcrypt (legacy `bcryptjs` hashes still verify). JWT: HS256.

## Endpoints

Base path: `/user-service`

### Auth (`/auth`)
| Method | Path | Purpose | Replaces (legacy) |
| --- | --- | --- | --- |
| POST | `/auth/login` | Authenticate, issue JWT, return user + access modules | `POST /login` |
| GET | `/auth/check-login` | Validate `Authorization: Bearer` session | `GET /checkLogin` |
| POST | `/auth/logout` | `{userId}` — drop the user's tokens | `GET /logout` |
| POST | `/auth/verify-password` | `{userId, password}` re-check | `POST /verifyPassword` |
| PUT | `/auth/forgot-password` | `{emailId, newPassword, sendEmail?}` | `forgotPassword` + `forgotManualPassword` |
| POST | `/auth/forgot-password/send-mail` | `{emailId}` send reset link | `POST /sendForgotPasswordMail` |
| POST | `/auth/end-session` | `{userId}` soft-expire sessions | `POST /user/:id/endUserSession` |
| GET | `/auth/system-config` | list, or one via `?id=` | `systemConfig` + `systemConfigView` |

### Users (`/users`)
| Method | Path | Purpose | Replaces |
| --- | --- | --- | --- |
| POST | `/users` | Create a user (role optional, auto-password, internalUserId) | `add` + `addUser` |
| POST | `/users/list` | List/search; paginates when `page`/`limit` given | `list` + `listLite` |
| POST | `/users/view` | View one by id/email/name/npi | `GET /:id/view` + `POST /view` |
| PUT | `/users` | Update: single (`userId`) or bulk (`userIds`); `toggle` flips active; `signature` bumps count | `edit` + `bulkEdit` + `toggle` + `add/edit/updateSignature` |
| DELETE | `/users/{id}` | Delete user + clear its UserAcl | `delete` |
| POST | `/users/validate` | Email/NPI uniqueness check | `validateUser` |

### Access control (`/access-control`)
| Method | Path | Purpose | Replaces |
| --- | --- | --- | --- |
| POST | `/access-control/modules` | Add module(s); `{seed:true}` loads defaults | `addAclModuleMappingData` + `addAclModuleMappingRawData` |
| GET | `/access-control/modules` | List ACL modules | `getAclModuleMappingData` |
| POST | `/access-control/roles` | Create role + its permissions | `addNewRole` |
| GET | `/access-control/roles` | List (`?search`, `?page/limit`) or one (`?roleId`) | `role/list` + `role/listLite` + `role/:id/view` |
| PUT | `/access-control/roles/{id}/permissions` | Replace a role's permissions | `addAccess` + `addBulkRoleAclModule` |
| GET | `/access-control/roles/{id}/permissions` | A role's permissions | `listAccess` |
| PUT | `/access-control/users/{id}/role` | Assign role + permissions (sets a password if none) | `addUserRole` |
| GET | `/access-control/users/{id}/permissions` | A user's permissions | `getUserRoleAclModule` |

### Static data (`/static-data`)
| Method | Path | Purpose | Replaces |
| --- | --- | --- | --- |
| GET | `/static-data/geo?type=cities\|states\|county\|zipcodes\|all` | Geo lookups (paginated) | `getCities` + `getStates` + `getCounty` + `getZipcode` + `getCityListLite` + `listLite` |
| GET | `/static-data/geo/zipcode/{zipcode}` | Single zipcode row (incl. timezone) | `getTimezoneOfZipcode` |
| POST | `/static-data/geo` | `{address: [...]}` add rows | `addAddress` |
| DELETE | `/static-data/geo` | `{zipcodes: [...]}` delete | `deleteAddress` |
| GET | `/static-data/dropdowns/{title}` | Dropdown options by title | `view` + `prefix` + `suffix` + `maritalStatus` |
| POST | `/static-data/dropdowns` | Create a dropdown set | RaceEthnicity `add` |
| PUT | `/static-data/dropdowns` | Append options (rejects duplicate codes) | RaceEthnicity `edit` |
| DELETE | `/static-data/dropdowns` | Remove options by code | RaceEthnicity `delete` |

## Deferred (other services, not yet migrated)
- **Email side-effects** (new-user credentials, password reset mail) — TODO until the email service migrates.
- **Login enrichment** (facility/lab/location details by role) — TODO until those services migrate.

## Tests

`backend/tests/test_user_service.py` — 27 tests against a real Postgres DB,
one+ per endpoint (success + key error paths).

```bash
cd backend && source .venv/bin/activate
createdb azi_user_test            # one-time (or set TEST_DATABASE_URL)
python -m pytest
```
