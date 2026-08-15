
import os

from forgesteel_warehouse.utils.patreon_api import PatreonUser


def has_warehouse_access(patreon_user: PatreonUser | None):
    if patreon_user is not None \
        and patreon_user.forgesteel is not None \
        and patreon_user.forgesteel.patron is True:
        return True
    
    owner_id = os.getenv("PATREON_OWNER_ID")
    if patreon_user is not None \
        and owner_id is not None \
        and patreon_user.id == owner_id:
        return True

    return False
