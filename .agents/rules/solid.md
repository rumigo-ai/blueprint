# SOLID principles

Activation: always when writing or refactoring code

| Letter | Rule in this repo |
|--------|-------------------|
| **S** | Routes ≠ auth ≠ DB ≠ models. One module, one reason to change. |
| **O** | Add features via new route/lib modules; avoid editing `clerk.py`/`db.py` for every endpoint. |
| **L** | `*Create`/`*Update` schemas stay compatible with base field types. |
| **I** | Depend on `ClerkIdentityDep` + `get_session`, not a god context object. |
| **D** | High-level routes depend on abstractions (`Depends`); libs never import routes. |

## Layering

```text
✅ route → Depends → lib/auth + lib/db → models
❌ route → new Clerk + new Engine + raw SQL + business rules
```

## Example

```python
# ✅ GOOD
@router.post("/me", response_model=User)
async def create_me(
    body: MeCreateRequest,
    identity: ClerkIdentityDep,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    ...

# ❌ BAD
@router.post("/me")
async def create_me(request: Request):
    clerk = Clerk(bearer_auth=os.environ["CLERK_SECRET_KEY"])
    engine = create_async_engine(os.environ["DATABASE_URL"])
    ...
```

When adding code, ask: “If Clerk changes, must this file change?” If yes and the file is not `lib/auth/clerk.py`, you violated SRP.
