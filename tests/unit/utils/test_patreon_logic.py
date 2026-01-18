from forgesteel_warehouse.utils.patreon_api import PatreonUser, PatronState, PatronTier
from forgesteel_warehouse.utils.patreon_logic import has_warehouse_access


def test_has_warehouse_access_None():
    user = None

    result = has_warehouse_access(user)
    assert result == False


def test_has_warehouse_access_patron():
    user = PatreonUser(
        id='1234',
        forgesteel=PatronState(
            patron=True,
            tiers=[
                PatronTier(
                    id='54321',
                    title='Forge Steel'
                )
            ]
        )
    )

    result = has_warehouse_access(user)
    assert result == True


def test_has_warehouse_access_non_patron():
    user = PatreonUser(
        id="1234",
        forgesteel=PatronState(
            patron=False, tiers=[]
        ),
    )

    result = has_warehouse_access(user)
    assert result == False
