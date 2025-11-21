# conftest.py
import pytest
from TaskTonic import ttLedger


@pytest.fixture(autouse=True)
def reset_ledger():
    """
    Reset de Singleton Ledger voor en na elke test.
    Dit voorkomt dat IDs oplopen en essences uit vorige tests blijven hangen.
    """
    # Setup: Zorg dat we schoon beginnen
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

    yield

    # Teardown: Ruim op na de test
    if ttLedger._instance:
        # Forceer een clear van de interne lijsten indien nodig
        ttLedger._instance.records = []
        ttLedger._instance.essences = []
        ttLedger._instance.formula = None

    ttLedger._instance = None
    ttLedger._singleton_init_done = False