import pytest
from src.manager import Manager
from src.models import Parameters, Transfer

def test_transfer_validation_out_of_bounds():
    manager = Manager(Parameters())
    
    manager.transfers = [
        Transfer(amount_pln=5.0, date="2023-01-01", settlement_year=2023, settlement_month=1, tenant="Jan Kowalski", type="rent"),
        Transfer(amount_pln=1500.0, date="2023-01-02", settlement_year=2023, settlement_month=1, tenant="Anna Nowak", type="rent"),
        Transfer(amount_pln=10000.0, date="2023-01-03", settlement_year=2023, settlement_month=1, tenant="Piotr Wisniewski", type="rent"),
    ]
    
    manager.min_transfer_amount = 10.0
    manager.max_transfer_amount = 5000.0
    
    invalid_transfers = manager.get_invalid_transfers()
    
    assert len(invalid_transfers) == 2
    assert manager.transfers[0] in invalid_transfers
    assert manager.transfers[2] in invalid_transfers
    assert manager.transfers[1] not in invalid_transfers
