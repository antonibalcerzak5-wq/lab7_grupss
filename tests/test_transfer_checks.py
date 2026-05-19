import pytest

from src.models import Tenant, Transfer, Parameters
from src.manager import Manager


def test_detect_unassigned_transfer():
    
    manager = Manager(Parameters())
    manager.tenants = {}
    manager.transfers = [
        Transfer(amount_pln=100.0, date="2024-01-01", settlement_year=2024, settlement_month=1, tenant="missing-tenant", type=None)
    ]

    errors = manager.find_transfer_errors()

    assert any(
        err.get('type') == 'unassigned_tenant' and err.get('transfer') == manager.transfers[0]
        for err in errors
    )


def test_detect_transfer_outside_agreement():
    
    manager = Manager(Parameters())

    manager.tenants = {
        "tenant-1": Tenant(
            name="Alice",
            apartment="apart-1",
            room="",
            rent_pln=1000.0,
            deposit_pln=0.0,
            date_agreement_from="2020-01-01",
            date_agreement_to="2022-12-31",
        )
    }

    manager.transfers = [
        Transfer(amount_pln=1000.0, date="2023-01-15", settlement_year=2023, settlement_month=1, tenant="tenant-1", type=None)
    ]

    errors = manager.find_transfer_errors()

    assert any(
        err.get('type') == 'transfer_outside_agreement' and err.get('transfer') == manager.transfers[0]
        for err in errors
    )
