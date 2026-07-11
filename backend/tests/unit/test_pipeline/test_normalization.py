"""
Tests for data normalization.
"""

import pytest

from backend.pipeline.normalization import (
    CompanyNormalizer,
    CountryNormalizer,
    CurrencyNormalizer,
    DataNormalizer,
    DateNormalizer,
    LanguageNormalizer,
    LocationNormalizer,
    PersonNormalizer,
)


class TestDateNormalizer:
    """Tests for DateNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return DateNormalizer()

    def test_normalize_iso_date(self, normalizer):
        """Test ISO date normalization."""
        result = normalizer.normalize_date("2024-01-15")
        assert result == "2024-01-15"

    def test_normalize_slash_date(self, normalizer):
        """Test slash-separated date normalization."""
        result = normalizer.normalize_date("01/15/2024")
        assert result is not None

    def test_normalize_invalid_date(self, normalizer):
        """Test invalid date returns original."""
        result = normalizer.normalize_date("not-a-date")
        assert result is not None

    def test_normalize_none(self, normalizer):
        """Test None input returns None."""
        result = normalizer.normalize_date(None)
        assert result is None

    def test_parse_datetime(self, normalizer):
        """Test datetime parsing."""
        result = normalizer.parse_datetime("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15


class TestCurrencyNormalizer:
    """Tests for CurrencyNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return CurrencyNormalizer()

    def test_normalize_numeric(self, normalizer):
        """Test numeric value normalization."""
        value, currency = normalizer.normalize_currency(100.50)
        assert value == 100.50
        assert currency is None

    def test_normalize_usd_symbol(self, normalizer):
        """Test USD symbol normalization."""
        value, currency = normalizer.normalize_currency("$1,234.56")
        assert value == 1234.56
        assert currency == "USD"

    def test_normalize_eur_symbol(self, normalizer):
        """Test EUR symbol normalization."""
        value, currency = normalizer.normalize_currency("€1,234.56")
        assert value == 1234.56
        assert currency == "EUR"

    def test_normalize_none(self, normalizer):
        """Test None input."""
        value, currency = normalizer.normalize_currency(None)
        assert value is None
        assert currency is None

    def test_format_currency(self, normalizer):
        """Test currency formatting."""
        result = normalizer.format_currency(1234.56, "USD")
        assert "$" in result
        assert "1,234.56" in result


class TestCountryNormalizer:
    """Tests for CountryNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return CountryNormalizer()

    def test_normalize_usa(self, normalizer):
        """Test USA normalization."""
        result = normalizer.normalize_country("USA")
        assert result == "United States"

    def test_normalize_us(self, normalizer):
        """Test US normalization."""
        result = normalizer.normalize_country("US")
        assert result == "United States"

    def test_normalize_uk(self, normalizer):
        """Test UK normalization."""
        result = normalizer.normalize_country("UK")
        assert result == "United Kingdom"

    def test_normalize_germany(self, normalizer):
        """Test Germany normalization."""
        result = normalizer.normalize_country("DE")
        assert result == "Germany"

    def test_normalize_none(self, normalizer):
        """Test None input."""
        result = normalizer.normalize_country(None)
        assert result is None

    def test_get_country_code(self, normalizer):
        """Test country code extraction."""
        code = normalizer.get_country_code("United States")
        assert code == "US"


class TestLanguageNormalizer:
    """Tests for LanguageNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return LanguageNormalizer()

    def test_normalize_english(self, normalizer):
        """Test English normalization."""
        result = normalizer.normalize_language("en")
        assert result == "English"

    def test_normalize_spanish(self, normalizer):
        """Test Spanish normalization."""
        result = normalizer.normalize_language("es")
        assert result == "Spanish"

    def test_normalize_chinese(self, normalizer):
        """Test Chinese normalization."""
        result = normalizer.normalize_language("zh")
        assert result == "Chinese"

    def test_normalize_none(self, normalizer):
        """Test None input."""
        result = normalizer.normalize_language(None)
        assert result is None


class TestCompanyNormalizer:
    """Tests for CompanyNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return CompanyNormalizer()

    def test_normalize_basic(self, normalizer):
        """Test basic company normalization."""
        result = normalizer.normalize_company("Apple Inc.")
        assert result is not None

    def test_normalize_with_suffix(self, normalizer):
        """Test company with suffix."""
        result = normalizer.normalize_company("Microsoft Corporation")
        assert result is not None

    def test_normalize_none(self, normalizer):
        """Test None input."""
        result = normalizer.normalize_company(None)
        assert result is None


class TestPersonNormalizer:
    """Tests for PersonNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return PersonNormalizer()

    def test_normalize_basic(self, normalizer):
        """Test basic person normalization."""
        result = normalizer.normalize_person("John Smith")
        assert result == "John Smith"

    def test_remove_title(self, normalizer):
        """Test title removal."""
        result = normalizer.normalize_person("Dr. Jane Doe")
        assert "Dr." not in result

    def test_normalize_none(self, normalizer):
        """Test None input."""
        result = normalizer.normalize_person(None)
        assert result is None

    def test_extract_name_parts(self, normalizer):
        """Test name part extraction."""
        parts = normalizer.extract_name_parts("John Smith")
        assert parts["first"] == "John"
        assert parts["last"] == "Smith"


class TestLocationNormalizer:
    """Tests for LocationNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return LocationNormalizer()

    def test_normalize_city_state_country(self, normalizer):
        """Test city, state, country format."""
        result = normalizer.normalize_location("New York, NY, USA")
        assert result["city"] == "New York"
        assert result["state"] == "NY"
        assert result["country"] == "United States"

    def test_normalize_city_country(self, normalizer):
        """Test city, country format."""
        result = normalizer.normalize_location("Paris, France")
        assert result["city"] == "Paris"
        assert result["country"] == "France"

    def test_normalize_none(self, normalizer):
        """Test None input."""
        result = normalizer.normalize_location(None)
        assert result["full"] is None


class TestDataNormalizer:
    """Tests for main DataNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return DataNormalizer()

    def test_date_normalization(self, normalizer):
        """Test date field normalization."""
        from uuid import uuid4

        from backend.pipeline.types import PipelineRecord, PipelineStage, SourceType

        record = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.WEB,
            stage=PipelineStage.COLLECTED,
            cleaned_data={
                "date": "2024-01-15",
                "title": "Test",
            },
        )

        result = normalizer.normalize_record(record)
        assert "date" in result

    def test_country_normalization(self, normalizer):
        """Test country field normalization."""
        from uuid import uuid4

        from backend.pipeline.types import PipelineRecord, PipelineStage, SourceType

        record = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.WEB,
            stage=PipelineStage.COLLECTED,
            cleaned_data={
                "country": "US",
                "title": "Test",
            },
        )

        result = normalizer.normalize_record(record)
        assert result.get("country") == "United States"
