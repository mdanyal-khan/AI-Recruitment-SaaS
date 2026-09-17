from datetime import date, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.offer import OfferCreate


def test_offer_dates_are_valid():
    start_date = date.today() + timedelta(days=30)
    expiration_date = date.today() + timedelta(days=15)

    offer = OfferCreate(
        application_id=uuid4(),
        salary=100000,
        currency="USD",
        start_date=start_date,
        expiration_date=expiration_date,
    )

    assert offer.start_date >= offer.expiration_date


def test_offer_dates_invalid_when_expiration_after_start():
    start_date = date.today() + timedelta(days=10)
    expiration_date = date.today() + timedelta(days=20)

    with pytest.raises(ValidationError):
        OfferCreate(
            application_id=uuid4(),
            salary=100000,
            currency="USD",
            start_date=start_date,
            expiration_date=expiration_date,
        )
