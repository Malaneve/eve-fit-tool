# evefit_gui/views/add_fit_dialog.py

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

from evefit_core.fit_models import Fit


class AddFitDialog(QDialog):
    """
    Dialog to add or edit an EFT fit.

    - If existing_fit is None  -> create new fit
    - If existing_fit is given -> edit that fit (pre-fills the EFT text)
    """

    def __init__(self, parent=None, existing_fit: Optional[Fit] = None):
        super().__init__(parent)

        self._result_fit: Optional[Fit] = None
        self._existing_fit = existing_fit

        if existing_fit is None:
            self.setWindowTitle("Add EFT Fit")
        else:
            self.setWindowTitle(f"Edit EFT Fit – {existing_fit.name}")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("EFT fit:"))

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("[Ship, Fit Name]\n...items...")
        if existing_fit is not None:
            self.text_edit.setPlainText(existing_fit.eft_text)
        layout.addWidget(self.text_edit)

        button_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_ok = QPushButton("Save" if existing_fit is not None else "Add")

        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self._on_ok_clicked)

        button_row.addStretch()
        button_row.addWidget(btn_cancel)
        button_row.addWidget(btn_ok)

        layout.addLayout(button_row)

    @property
    def result_fit(self) -> Optional[Fit]:
        return self._result_fit

    def _on_ok_clicked(self):
        raw = self.text_edit.toPlainText().strip()

        if not raw:
            QMessageBox.warning(self, "Invalid", "Please paste an EFT fit.")
            return

        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        if not lines:
            QMessageBox.warning(self, "Invalid", "Could not read any lines.")
            return

        header = lines[0]

        # Expect "[Ship, Fit Name]" or "[Ship]"
        if not (header.startswith("[") and header.endswith("]")):
            QMessageBox.warning(
                self,
                "Invalid header",
                "First line must be like:\n[Ship, Fit Name] or [Ship]",
            )
            return

        inside = header[1:-1]
        if "," in inside:
            ship, name = [x.strip() for x in inside.split(",", 1)]
        else:
            ship = inside.strip()
            name = ship

        if not ship:
            QMessageBox.warning(self, "Invalid header", "Ship name is empty.")
            return

        # Preserve id if we are editing, otherwise generate a new one
        if self._existing_fit is not None:
            fit_id = self._existing_fit.id
        else:
            fit_id = f"{ship}-{name}"

        self._result_fit = Fit(
            id=fit_id,
            name=name,
            ship_type=ship,
            eft_text=raw,
        )

        self.accept()
