import json

import pytest
from pydantic import ValidationError

from src.manager import Manager
from src.models import Parameters


def _write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def _create_test_parameters(tmp_path) -> Parameters:
    apartments_path = tmp_path / "apartments.json"
    tenants_path = tmp_path / "tenants.json"
    transfers_path = tmp_path / "transfers.json"
    bills_path = tmp_path / "bills.json"
    blacklist_path = tmp_path / "blacklist.json"

    _write_json(apartments_path, {
        "apart-test": {
            "key": "apart-test",
            "name": "Test Apartment",
            "location": "Testowa 1",
            "area_m2": 50.0,
            "rooms": {
                "room-1": {
                    "name": "Room 1",
                    "area_m2": 20.0
                }
            }
        }
    })

    _write_json(tenants_path, {
        "tenant-1": {
            "name": "Jan Nowak",
            "apartment": "apart-test",
            "room": "room-1",
            "rent_pln": 1500.0,
            "deposit_pln": 3000.0,
            "date_agreement_from": "2024-01-01",
            "date_agreement_to": "2024-12-31"
        },
        "tenant-2": {
            "name": "Adam Kowalski",
            "apartment": "apart-test",
            "room": "room-1",
            "rent_pln": 1400.0,
            "deposit_pln": 2800.0,
            "date_agreement_from": "2024-01-01",
            "date_agreement_to": "2024-12-31"
        }
    })

    _write_json(transfers_path, [])
    _write_json(bills_path, [])

    _write_json(blacklist_path, [
        {
            "name": "Jan Nowak",
            "reason": "Zaległości w płatnościach"
        },
        {
            "name": "Ewa Adamska",
            "reason": "Zniszczenie mieszkania"
        }
    ])

    return Parameters(
        apartments_json_path=str(apartments_path),
        tenants_json_path=str(tenants_path),
        transfers_json_path=str(transfers_path),
        bills_json_path=str(bills_path),
        blacklist_json_path=str(blacklist_path),
    )


def test_blacklisted_tenant_model_has_required_fields():
    from src.models import BlacklistedTenant

    blacklisted_tenant = BlacklistedTenant(
        name="Jan Nowak",
        reason="Zaległości w płatnościach"
    )

    assert blacklisted_tenant.name == "Jan Nowak"
    assert blacklisted_tenant.reason == "Zaległości w płatnościach"


def test_blacklisted_tenant_model_requires_reason():
    from src.models import BlacklistedTenant

    with pytest.raises(ValidationError):
        BlacklistedTenant(name="Jan Nowak")


def test_blacklisted_tenants_can_be_loaded_from_json_file(tmp_path):
    from src.models import BlacklistedTenant

    blacklist_path = tmp_path / "blacklist.json"

    _write_json(blacklist_path, [
        {
            "name": "Jan Nowak",
            "reason": "Zaległości w płatnościach"
        },
        {
            "name": "Ewa Adamska",
            "reason": "Zniszczenie mieszkania"
        }
    ])

    blacklist = BlacklistedTenant.from_json_file(str(blacklist_path))

    assert isinstance(blacklist, list)
    assert len(blacklist) == 2

    assert isinstance(blacklist[0], BlacklistedTenant)
    assert blacklist[0].name == "Jan Nowak"
    assert blacklist[0].reason == "Zaległości w płatnościach"

    assert isinstance(blacklist[1], BlacklistedTenant)
    assert blacklist[1].name == "Ewa Adamska"
    assert blacklist[1].reason == "Zniszczenie mieszkania"


def test_parameters_contains_blacklist_json_path():
    parameters = Parameters()

    assert hasattr(parameters, "blacklist_json_path")
    assert parameters.blacklist_json_path == "data/blacklist.json"


def test_manager_loads_blacklisted_tenants_from_file(tmp_path):
    parameters = _create_test_parameters(tmp_path)
    manager = Manager(parameters)

    assert hasattr(manager, "blacklisted_tenants")
    assert isinstance(manager.blacklisted_tenants, list)
    assert len(manager.blacklisted_tenants) == 2

    names = [tenant.name for tenant in manager.blacklisted_tenants]
    reasons = [tenant.reason for tenant in manager.blacklisted_tenants]

    assert "Jan Nowak" in names
    assert "Ewa Adamska" in names
    assert "Zaległości w płatnościach" in reasons
    assert "Zniszczenie mieszkania" in reasons


def test_manager_checks_if_tenant_is_blacklisted(tmp_path):
    parameters = _create_test_parameters(tmp_path)
    manager = Manager(parameters)

    assert manager.is_tenant_blacklisted("Jan Nowak") is True
    assert manager.is_tenant_blacklisted("Ewa Adamska") is True
    assert manager.is_tenant_blacklisted("Adam Kowalski") is False
    assert manager.is_tenant_blacklisted("Nieznany Najemca") is False