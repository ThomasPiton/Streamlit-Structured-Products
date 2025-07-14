from abc import ABC, abstractmethod

class BaseWrapper(ABC):
    """
    Abstract base class for financial instrument wrappers.

    Each subclass must implement the `price()` method, which returns the
    instrument's fair value or market value based on internal logic.
    """

    @abstractmethod
    def price(self, **kwargs):
        """
        Compute the price of the instrument.
        """
        pass