from src.displayer.displayer_manager import *

class DisplayFactory:
    def __init__(self, display: str = None, **args):
        self.display = display.upper() if display else None  # Toujours en majuscules pour éviter les erreurs
        self.args = args

    def render(self):
        """Crée et affiche la bonne visualisation selon la valeur de display."""
        if self.display == "DISPLAY_TEST_V1":
            DisplayIndexLevel(**self.args).render()

        elif self.display == "DISPLAY_TEST_V2":
            DisplayIndexLevelVsBenchmark(**self.args).render()

        else:
            raise ValueError(f"DisplayFactory: Unknown display type '{self.display}'")
