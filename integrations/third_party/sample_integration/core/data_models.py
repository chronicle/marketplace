from dataclasses import dataclass

from TIPCommon.types import SingleJson


@dataclass(frozen=True, slots=True)
class BaseRate:
    base: str
    date: str
    rates: SingleJson

    def json(self) -> SingleJson:
        return {"base": self.base, "rates": self.rates}

    def to_csv(self) -> list[SingleJson]:
        return [
            {"Currency": symbol, "Value": value} for symbol, value in self.rates.items()
        ]


@dataclass(frozen=True, slots=True)
class DailyRates:
    date: str
    exchange_rates: list[BaseRate]

    def json(self) -> SingleJson:
        return {
            "date": self.date,
            "exchange_rates": [rate.json() for rate in self.exchange_rates],
        }
