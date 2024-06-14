import pytest
from unittest.mock import MagicMock
import tkinter as tk
import tkinter.font

@pytest.fixture(autouse=True)
def mock_tk_main(monkeypatch):
    # Mock tk.Tk()
    mock_tk = MagicMock()
    monkeypatch.setattr(tk, 'Tk', mock_tk)
    monkeypatch.setattr(tkinter.font, 'Font', MagicMock())
    # Return the mocked instance
    main_instance = mock_tk.return_value
    return main_instance
