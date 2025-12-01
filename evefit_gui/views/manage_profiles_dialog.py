# evefit_gui/views/manage_profiles_dialog.py

from typing import List

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QInputDialog,
)

from evefit_core.fit_models import SkillProfile
from evefit_core.skills import (
    load_skill_profiles,
    save_skill_profile,
    delete_skill_profile,
    rename_skill_profile,
)


class ManageProfilesDialog(QDialog):
    """
    Simple dialog to manage skill profiles (characters):
    - Add
    - Rename
    - Delete
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Manage Profiles")
        self.profiles: List[SkillProfile] = load_skill_profiles()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Profiles:"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_rename = QPushButton("Rename")
        self.btn_delete = QPushButton("Delete")
        self.btn_close = QPushButton("Close")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_rename.clicked.connect(self._on_rename)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_close.clicked.connect(self.accept)

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_rename)
        btn_row.addWidget(self.btn_delete)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_close)

        layout.addLayout(btn_row)

        self._populate_list()

    # -------------------------
    # Helpers
    # -------------------------
    def _populate_list(self):
        self.list_widget.clear()
        for profile in self.profiles:
            self.list_widget.addItem(profile.name)

    def _get_selected_index(self) -> int:
        row = self.list_widget.currentRow()
        return row

    # -------------------------
    # Actions
    # -------------------------
    def _on_add(self):
        name, ok = QInputDialog.getText(self, "Add profile", "Profile name:")
        if not ok or not name.strip():
            return

        name = name.strip()

        # Check duplicate
        if any(p.name == name for p in self.profiles):
            QMessageBox.warning(self, "Duplicate", "A profile with this name already exists.")
            return

        profile = SkillProfile(name=name, skills={})
        save_skill_profile(profile)
        self.profiles = load_skill_profiles()
        self._populate_list()

    def _on_rename(self):
        idx = self._get_selected_index()
        if idx < 0 or idx >= len(self.profiles):
            QMessageBox.information(self, "No selection", "Select a profile to rename.")
            return

        current_profile = self.profiles[idx]

        new_name, ok = QInputDialog.getText(
            self, "Rename profile", "New name:", text=current_profile.name
        )
        if not ok:
            return

        new_name = new_name.strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid name", "Name cannot be empty.")
            return

        if new_name == current_profile.name:
            return

        # Check duplicates
        if any(p.name == new_name for p in self.profiles):
            QMessageBox.warning(self, "Duplicate", "A profile with this name already exists.")
            return

        rename_skill_profile(current_profile.name, new_name)
        self.profiles = load_skill_profiles()
        self._populate_list()

    def _on_delete(self):
        idx = self._get_selected_index()
        if idx < 0 or idx >= len(self.profiles):
            QMessageBox.information(self, "No selection", "Select a profile to delete.")
            return

        profile = self.profiles[idx]

        reply = QMessageBox.question(
            self,
            "Delete profile",
            f"Are you sure you want to delete profile:\n\n{profile.name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        delete_skill_profile(profile.name)
        self.profiles = load_skill_profiles()
        self._populate_list()
