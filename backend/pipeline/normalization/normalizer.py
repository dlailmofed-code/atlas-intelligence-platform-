"""
ATLAS Platform - Data Normalization Module

Handles normalization of dates, currencies, countries, languages, companies, people, and locations.
"""

import re
import unicodedata
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from backend.core.logging import get_logger
from backend.pipeline.types import PipelineRecord

logger = get_logger(__name__)


# Country name mappings
COUNTRY_MAPPINGS = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "great britain": "United Kingdom",
    "uae": "United Arab Emirates",
    "emirates": "United Arab Emirates",
    "ua": "Ukraine",
    "de": "Germany",
    "deutschland": "Germany",
    "fr": "France",
    "espana": "Spain",
    "spain": "Spain",
    "italia": "Italy",
    "italy": "Italy",
    "jp": "Japan",
    "chn": "China",
    "p.r.c.": "China",
    "p.r.china": "China",
    "in": "India",
    "brasil": "Brazil",
    "brazil": "Brazil",
    "ca": "Canada",
    "canada": "Canada",
    "au": "Australia",
    "australia": "Australia",
    "ru": "Russia",
    "russia": "Russia",
    "korea": "South Korea",
    "south korea": "South Korea",
    "rok": "South Korea",
}

# ISO country codes
ISO_COUNTRIES = {
    "AF": "Afghanistan",
    "AL": "Albania",
    "DZ": "Algeria",
    "AR": "Argentina",
    "AU": "Australia",
    "AT": "Austria",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BR": "Brazil",
    "CA": "Canada",
    "CN": "China",
    "CO": "Colombia",
    "HR": "Croatia",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "EG": "Egypt",
    "FI": "Finland",
    "FR": "France",
    "DE": "Germany",
    "GR": "Greece",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IN": "India",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IT": "Italy",
    "JP": "Japan",
    "KE": "Kenya",
    "KR": "South Korea",
    "KW": "Kuwait",
    "LB": "Lebanon",
    "MY": "Malaysia",
    "MX": "Mexico",
    "MA": "Morocco",
    "NL": "Netherlands",
    "NZ": "New Zealand",
    "NG": "Nigeria",
    "NO": "Norway",
    "PK": "Pakistan",
    "PE": "Peru",
    "PH": "Philippines",
    "PL": "Poland",
    "PT": "Portugal",
    "QA": "Qatar",
    "RO": "Romania",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "SG": "Singapore",
    "ZA": "South Africa",
    "ES": "Spain",
    "SE": "Sweden",
    "CH": "Switzerland",
    "TW": "Taiwan",
    "TH": "Thailand",
    "TR": "Turkey",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom",
    "US": "United States",
    "VN": "Vietnam",
}

# Currency mappings
CURRENCY_MAPPINGS = {
    "$": "USD",
    "us$": "USD",
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "€": "EUR",
    "eur": "EUR",
    "euro": "EUR",
    "£": "GBP",
    "gbp": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "¥": "JPY",
    "jpy": "JPY",
    "yuan": "CNY",
    "rmb": "CNY",
    "cny": "CNY",
    "₹": "INR",
    "inr": "INR",
    "rupee": "INR",
    "₩": "KRW",
    "krw": "KRW",
    "won": "KRW",
    "₽": "RUB",
    "rub": "RUB",
    "ruble": "RUB",
    "chf": "CHF",
    "franc": "CHF",
    "a$": "AUD",
    "aud": "AUD",
    "c$": "CAD",
    "cad": "CAD",
    "s$": "SGD",
    "sgd": "SGD",
    "hkd": "HKD",
    "thb": "THB",
    "zar": "ZAR",
    "mxn": "MXN",
    "brl": "BRL",
    "try": "TRY",
    "pln": "PLN",
    "sek": "SEK",
    "nok": "NOK",
    "dkk": "DKK",
    "nzd": "NZD",
}

# Language mappings
LANGUAGE_MAPPINGS = {
    "en": "English",
    "eng": "English",
    "english": "English",
    "es": "Spanish",
    "esp": "Spanish",
    "spanish": "Spanish",
    "español": "Spanish",
    "fr": "French",
    "fra": "French",
    "french": "French",
    "français": "French",
    "de": "German",
    "ger": "German",
    "german": "German",
    "deutsch": "German",
    "it": "Italian",
    "ita": "Italian",
    "italian": "Italian",
    "italiano": "Italian",
    "pt": "Portuguese",
    "por": "Portuguese",
    "portuguese": "Portuguese",
    "pt-BR": "Portuguese (Brazil)",
    "zh": "Chinese",
    "chi": "Chinese",
    "chinese": "Chinese",
    "ja": "Japanese",
    "jpn": "Japanese",
    "japanese": "Japanese",
    "ko": "Korean",
    "kor": "Korean",
    "korean": "Korean",
    "ar": "Arabic",
    "ara": "Arabic",
    "arabic": "Arabic",
    "ru": "Russian",
    "rus": "Russian",
    "russian": "Russian",
    "hi": "Hindi",
    "hin": "Hindi",
    "hindi": "Hindi",
    "nl": "Dutch",
    "dut": "Dutch",
    "dutch": "Dutch",
    "pl": "Polish",
    "pol": "Polish",
    "polish": "Polish",
    "tr": "Turkish",
    "tur": "Turkish",
    "turkish": "Turkish",
    "vi": "Vietnamese",
    "vie": "Vietnamese",
    "vietnamese": "Vietnamese",
    "th": "Thai",
    "tha": "Thai",
    "thai": "Thai",
}

# Common company suffixes
COMPANY_SUFFIXES = [
    "Inc.",
    "Inc",
    "Corporation",
    "Corp.",
    "Corp",
    "LLC",
    "Ltd.",
    "Ltd",
    "Limited",
    "Company",
    "Co.",
    "Co",
    "AG",
    "GmbH",
    "PLC",
    "SA",
    "NV",
    "BV",
    "Pte Ltd",
    "Private Limited",
    "LLP",
    "LP",
    "GP",
]


class DateNormalizer:
    """Normalizes date strings to ISO format."""
    
    DATE_PATTERNS = [
        # ISO formats
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        (r"\d{4}/\d{2}/\d{2}", "%Y/%m/%d"),
        (r"\d{8}", "%Y%m%d"),
        # US formats
        (r"\d{1,2}/\d{1,2}/\d{4}", "%m/%d/%Y"),
        (r"\d{1,2}-\d{1,2}-\d{4}", "%m-%d-%Y"),
        # European formats
        (r"\d{1,2}/\d{1,2}/\d{4}", "%d/%m/%Y"),  # Ambiguous, try both
        (r"\d{1,2}\.\d{1,2}\.\d{4}", "%d.%m.%Y"),
        # With time
        (r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", "%Y-%m-%dT%H:%M:%S"),
        (r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d+", "%Y-%m-%dT%H:%M:%S.%f"),
    ]
    
    RELATIVE_DATE_PATTERNS = {
        r"yesterday": -1,
        r"today": 0,
        r"tomorrow": 1,
        r"last\s+week": -7,
        r"next\s+week": 7,
        r"last\s+month": -30,
        r"next\s+month": 30,
        r"last\s+year": -365,
        r"next\s+year": 365,
    }
    
    def normalize_date(self, date_str: str | None) -> str | None:
        """Normalize a date string to ISO format."""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Try relative date patterns first
        for pattern, days in self.RELATIVE_DATE_PATTERNS.items():
            if re.search(pattern, date_str, re.IGNORECASE):
                from datetime import timedelta
                relative_date = datetime.now() + timedelta(days=days)
                return relative_date.strftime("%Y-%m-%d")
        
        # Try standard patterns
        for pattern, fmt in self.DATE_PATTERNS:
            match = re.search(pattern, date_str)
            if match:
                try:
                    dt = datetime.strptime(match.group(), fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        # Try common relative patterns
        match = re.search(
            r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago",
            date_str,
            re.IGNORECASE
        )
        if match:
            amount = int(match.group(1))
            unit = match.group(2).lower()
            
            from datetime import timedelta
            
            unit_map = {
                "second": timedelta(seconds=amount),
                "minute": timedelta(minutes=amount),
                "hour": timedelta(hours=amount),
                "day": timedelta(days=amount),
                "week": timedelta(weeks=amount),
                "month": timedelta(days=amount * 30),
                "year": timedelta(days=amount * 365),
            }
            
            if unit in unit_map:
                past_date = datetime.now() - unit_map[unit]
                return past_date.strftime("%Y-%m-%d")
        
        return date_str
    
    def parse_datetime(self, date_str: str | None) -> datetime | None:
        """Parse a date string to datetime object."""
        normalized = self.normalize_date(date_str)
        if normalized:
            try:
                return datetime.strptime(normalized, "%Y-%m-%d")
            except ValueError:
                pass
        return None


class CurrencyNormalizer:
    """Normalizes currency values."""
    
    def normalize_currency(
        self,
        value: str | float | int | None,
        currency_code: str | None = None,
    ) -> tuple[float | None, str | None]:
        """
        Normalize a currency value.
        
        Returns:
            Tuple of (numeric_value, currency_code)
        """
        if value is None:
            return None, currency_code
        
        # If already numeric
        if isinstance(value, (int, float)):
            return float(value), currency_code
        
        value_str = str(value).strip()
        
        # Extract currency code from value
        detected_currency = currency_code
        numeric_value = value_str
        
        # Try to detect currency from symbol/code
        for symbol, code in CURRENCY_MAPPINGS.items():
            if symbol in value_str.upper():
                detected_currency = code
                numeric_value = value_str.upper().replace(symbol, "").strip()
                break
        
        # Remove common formatting
        numeric_value = re.sub(r"[,$'\"\\]", "", numeric_value)
        numeric_value = re.sub(r"\s+[A-Z]{3}$", "", numeric_value)  # Remove trailing currency
        
        try:
            return float(numeric_value), detected_currency
        except ValueError:
            return None, detected_currency
    
    def format_currency(
        self,
        value: float | None,
        currency_code: str = "USD",
        include_symbol: bool = True,
    ) -> str | None:
        """Format a currency value for display."""
        if value is None:
            return None
        
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CNY": "¥",
            "INR": "₹",
            "KRW": "₩",
            "RUB": "₽",
        }
        
        symbol = symbols.get(currency_code, currency_code + " ")
        
        if currency_code == "JPY":
            formatted = f"{symbol}{int(value):,}"
        else:
            formatted = f"{symbol}{value:,.2f}"
        
        return formatted if include_symbol else formatted.replace(symbol, "").strip()


class CountryNormalizer:
    """Normalizes country names and codes."""
    
    def normalize_country(self, country: str | None) -> str | None:
        """Normalize a country name or code to full name."""
        if not country:
            return None
        
        country = country.strip()
        
        # Check direct ISO code mapping
        if country.upper() in ISO_COUNTRIES:
            return ISO_COUNTRIES[country.upper()]
        
        # Check common name mappings
        if country.lower() in COUNTRY_MAPPINGS:
            return COUNTRY_MAPPINGS[country.lower()]
        
        # Try to match against ISO country names
        for code, name in ISO_COUNTRIES.items():
            if country.lower() == name.lower():
                return name
        
        return country.title()
    
    def get_country_code(self, country: str | None) -> str | None:
        """Get the ISO country code for a country."""
        if not country:
            return None
        
        normalized = self.normalize_country(country)
        if not normalized:
            return None
        
        for code, name in ISO_COUNTRIES.items():
            if name.lower() == normalized.lower():
                return code
        
        return None


class LanguageNormalizer:
    """Normalizes language names and codes."""
    
    def normalize_language(self, language: str | None) -> str | None:
        """Normalize a language name or code to full name."""
        if not language:
            return None
        
        language = language.strip().lower()
        
        # Check direct mapping
        if language in LANGUAGE_MAPPINGS:
            return LANGUAGE_MAPPINGS[language]
        
        # Try to match against language names
        for code, name in LANGUAGE_MAPPINGS.items():
            if language == name.lower():
                return name
        
        return language.title()
    
    def get_language_code(self, language: str | None) -> str | None:
        """Get the ISO language code for a language."""
        if not language:
            return None
        
        normalized = self.normalize_language(language)
        if not normalized:
            return None
        
        for code, name in LANGUAGE_MAPPINGS.items():
            if name.lower() == normalized.lower():
                return code
        
        return None


class CompanyNormalizer:
    """Normalizes company names."""
    
    def normalize_company(self, company: str | None) -> str | None:
        """Normalize a company name."""
        if not company:
            return None
        
        company = company.strip()
        
        # Remove common suffixes
        for suffix in COMPANY_SUFFIXES:
            if company.endswith(f", {suffix}"):
                company = company[: -len(f", {suffix}")]
            elif company.endswith(f" {suffix}"):
                company = company[: -len(f" {suffix}")]
            elif company.endswith(suffix):
                company = company[: -len(suffix)]
        
        # Normalize spacing
        company = re.sub(r"\s+", " ", company)
        
        # Title case
        company = company.title()
        
        # Restore known acronyms
        acronyms = ["LLC", "LLC", "GmbH", "AG", "SA", "NV", "PLC", "LLP"]
        for acronym in acronyms:
            if acronym.lower() in company.lower():
                company = re.sub(
                    rf"\b{acronym.lower()}\b",
                    acronym,
                    company,
                    flags=re.IGNORECASE
                )
        
        return company.strip()
    
    def extract_company_name(self, text: str | None) -> str | None:
        """Extract company name from text."""
        if not text:
            return None
        
        # Look for patterns like "at Company Name"
        match = re.search(r"(?:at|@|of)\s+([A-Z][A-Za-z\s&]+(?:Inc|Corp|LLC|Ltd|Company)?)", text)
        if match:
            return self.normalize_company(match.group(1))
        
        # Take first capitalized phrase
        match = re.search(r"^([A-Z][A-Za-z\s&]+(?:Inc|Corp|LLC|Ltd|Company)?)", text)
        if match:
            return self.normalize_company(match.group(1))
        
        return None


class PersonNormalizer:
    """Normalizes person names."""
    
    def normalize_person(self, person: str | None) -> str | None:
        """Normalize a person name."""
        if not person:
            return None
        
        person = person.strip()
        
        # Remove titles
        titles = r"(?:Dr|Mr|Mrs|Ms|Miss|Prof|Professor|Sir|Madam|Lord|Lady)\.?\s*"
        person = re.sub(titles, "", person, flags=re.IGNORECASE)
        
        # Remove suffixes
        suffixes = r"(?:Jr|Sr|III|IV|V|II)\.?\s*$"
        person = re.sub(suffixes, "", person, flags=re.IGNORECASE)
        
        # Normalize spacing
        person = re.sub(r"\s+", " ", person)
        
        return person.strip()
    
    def extract_name_parts(self, name: str | None) -> dict[str, str | None]:
        """Extract first, middle, and last name parts."""
        if not name:
            return {"first": None, "middle": None, "last": None}
        
        normalized = self.normalize_person(name)
        if not normalized:
            return {"first": None, "middle": None, "last": None}
        
        parts = normalized.split()
        
        if len(parts) == 1:
            return {"first": parts[0], "middle": None, "last": None}
        elif len(parts) == 2:
            return {"first": parts[0], "middle": None, "last": parts[1]}
        else:
            return {"first": parts[0], "middle": " ".join(parts[1:-1]), "last": parts[-1]}


class LocationNormalizer:
    """Normalizes location data."""
    
    def normalize_location(
        self,
        location: str | None,
    ) -> dict[str, str | None]:
        """Normalize a location string."""
        if not location:
            return {"full": None, "city": None, "state": None, "country": None}
        
        location = location.strip()
        country_normalizer = CountryNormalizer()
        
        # Try to parse common formats
        # "City, State, Country"
        match = re.match(r"(.+?),\s*(.+?),\s*(.+)", location)
        if match:
            return {
                "full": location,
                "city": match.group(1).strip(),
                "state": match.group(2).strip(),
                "country": country_normalizer.normalize_country(match.group(3)),
            }
        
        # "City, Country"
        match = re.match(r"(.+?),\s*(.+)", location)
        if match:
            return {
                "full": location,
                "city": match.group(1).strip(),
                "state": None,
                "country": country_normalizer.normalize_country(match.group(2)),
            }
        
        return {"full": location, "city": None, "state": None, "country": None}


class DataNormalizer:
    """Main normalizer that coordinates all normalization operations."""
    
    def __init__(self):
        self.date_normalizer = DateNormalizer()
        self.currency_normalizer = CurrencyNormalizer()
        self.country_normalizer = CountryNormalizer()
        self.language_normalizer = LanguageNormalizer()
        self.company_normalizer = CompanyNormalizer()
        self.person_normalizer = PersonNormalizer()
        self.location_normalizer = LocationNormalizer()
    
    def normalize_record(self, record: PipelineRecord) -> dict[str, Any]:
        """Normalize all fields in a pipeline record."""
        data = record.deduplicated_data or record.cleaned_data or {}
        normalized = {}
        
        # Normalize dates
        date_fields = ["date", "published_at", "created_at", "updated_at", "timestamp"]
        for field in date_fields:
            if field in data:
                normalized[field] = self.date_normalizer.normalize_date(data[field])
        
        # Normalize country
        if "country" in data:
            normalized["country"] = self.country_normalizer.normalize_country(data["country"])
        
        # Normalize language
        if "language" in data:
            normalized["language"] = self.language_normalizer.normalize_language(data["language"])
        
        # Normalize company
        company_fields = ["company", "organization", "company_name"]
        for field in company_fields:
            if field in data and data[field]:
                normalized[field] = self.company_normalizer.normalize_company(data[field])
                break
        
        # Normalize person
        person_fields = ["author", "person", "creator", "by"]
        for field in person_fields:
            if field in data and data[field]:
                normalized[field] = self.person_normalizer.normalize_person(data[field])
                break
        
        # Normalize currency
        if "currency" in data:
            normalized["currency"] = self.currency_normalizer.normalize_currency(
                data.get("value") or data.get("amount"),
                data["currency"]
            )[1]
        
        if "value" in data or "amount" in data:
            value = data.get("value") or data.get("amount")
            normalized["value"], normalized["currency"] = self.currency_normalizer.normalize_currency(
                value, data.get("currency")
            )
        
        # Normalize location
        location_fields = ["location", "place", "venue"]
        for field in location_fields:
            if field in data:
                normalized[field] = self.location_normalizer.normalize_location(data[field])
                break
        
        # Copy remaining fields
        for key, value in data.items():
            if key not in normalized:
                normalized[key] = value
        
        return normalized


# Global normalizer instance
_normalizer: DataNormalizer | None = None


def get_normalizer() -> DataNormalizer:
    """Get the global data normalizer."""
    global _normalizer
    if _normalizer is None:
        _normalizer = DataNormalizer()
    return _normalizer
