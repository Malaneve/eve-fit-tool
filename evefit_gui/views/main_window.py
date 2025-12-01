# evefit_gui/views/main_window.py

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QLabel,
    QToolBar,
    QComboBox,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from evefit_core.fit_engine import FitEngine
from evefit_core.fit_models import Fit, SkillProfile
from evefit_core.storage import load_fits, save_fits
from evefit_core.skills import load_skill_profiles

from .add_fit_dialog import AddFitDialog
from .manage_profiles_dialog import ManageProfilesDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EVE Fit Tool – Personal Planner")

        # Core engine
        self.engine = FitEngine()

        # Skill profiles
        self.skill_profiles = load_skill_profiles()
        self.active_skill_profile: SkillProfile = self.skill_profiles[0]

        # Load fits from disk; if none, start with some dummy fits
        loaded = load_fits()
        if loaded:
            self.fits = loaded
        else:
            self.fits = [
                Fit(
                    id="vni-1",
                    name="Dummy Vexor Navy",
                    ship_type="Vexor Navy Issue",
                    eft_text="[Vexor Navy Issue, Dummy]\n",
                ),
                Fit(
                    id="catalyst-1",
                    name="Dummy Catalyst",
                    ship_type="Catalyst",
                    eft_text="[Catalyst, Dummy]\n",
                ),
            ]

        # Filtered list for search
        self.filtered_fits = list(self.fits)

        self._build_ui()
        self._populate_fits()

    # -------------------------
    # UI Setup
    # -------------------------
    def _build_ui(self):
        # Toolbar
        toolbar = QToolBar("Main", self)
        self.addToolBar(toolbar)

        # Add fit
        action_add_fit = QAction("Add EFT Fit", self)
        action_add_fit.triggered.connect(self._on_add_fit)
        toolbar.addAction(action_add_fit)

        # Edit fit
        action_edit_fit = QAction("Edit", self)
        action_edit_fit.triggered.connect(self._on_edit_fit)
        toolbar.addAction(action_edit_fit)

        # Delete fit
        action_delete_fit = QAction("Delete", self)
        action_delete_fit.triggered.connect(self._on_delete_fit)
        toolbar.addAction(action_delete_fit)

        # Skill profile selector
        toolbar.addSeparator()
        toolbar.addWidget(QLabel(" Active profile: "))

        self.profile_combo = QComboBox()
        for profile in self.skill_profiles:
            self.profile_combo.addItem(profile.name, profile)
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        toolbar.addWidget(self.profile_combo)

        # Manage profiles
        action_manage_profiles = QAction("Manage profiles", self)
        action_manage_profiles.triggered.connect(self._on_manage_profiles)
        toolbar.addAction(action_manage_profiles)

        # Search bar
        toolbar.addSeparator()
        toolbar.addWidget(QLabel(" Search: "))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Name, ship, or EFT text...")
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        toolbar.addWidget(self.search_edit)

        # Main layout
        central = QWidget()
        layout = QHBoxLayout(central)

        # Left: fits list
        self.fit_list = QListWidget()
        self.fit_list.currentItemChanged.connect(self._on_fit_selected)

        # Right: stats panel
        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.label_title = QLabel("Select a fit")
        self.label_profile = QLabel(f"Profile: {self.active_skill_profile.name}")
        self.label_stats = QLabel("(stats will appear here)")
        self.label_stats.setWordWrap(True)

        right_layout.addWidget(self.label_title)
        right_layout.addWidget(self.label_profile)
        right_layout.addWidget(self.label_stats)
        right_layout.addStretch()

        layout.addWidget(self.fit_list, 1)
        layout.addWidget(right, 2)

        self.setCentralWidget(central)

    # -------------------------
    # Skill profile handling
    # -------------------------
    def _on_profile_changed(self, index: int):
        if index < 0:
            return
        profile = self.profile_combo.itemData(index)
        if isinstance(profile, SkillProfile):
            self.active_skill_profile = profile
            self.label_profile.setText(f"Profile: {profile.name}")

            current = self.fit_list.currentItem()
            if current is not None:
                self._on_fit_selected(current, None)

    def _reload_skill_profiles(self):
        current_name = self.active_skill_profile.name if self.active_skill_profile else None

        self.skill_profiles = load_skill_profiles()
        if not self.skill_profiles:
            self.active_skill_profile = SkillProfile(name="No skills (dummy)", skills={})
            self.skill_profiles = [self.active_skill_profile]

        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        selected_index = 0

        for i, profile in enumerate(self.skill_profiles):
            self.profile_combo.addItem(profile.name, profile)
            if profile.name == current_name:
                selected_index = i

        self.profile_combo.setCurrentIndex(selected_index)
        self.profile_combo.blockSignals(False)

        self.active_skill_profile = self.skill_profiles[selected_index]
        self.label_profile.setText(f"Profile: {self.active_skill_profile.name}")

    def _on_manage_profiles(self):
        dlg = ManageProfilesDialog(self)
        if dlg.exec():
            self._reload_skill_profiles()

    # -------------------------
    # Filtering
    # -------------------------
    def _on_search_text_changed(self, text: str):
        self._refresh_filtered_fits()

    def _refresh_filtered_fits(self):
        query = self.search_edit.text().strip().lower()
        if not query:
            self.filtered_fits = list(self.fits)
        else:
            filtered = []
            for fit in self.fits:
                if (
                    query in fit.name.lower()
                    or query in fit.ship_type.lower()
                    or query in fit.eft_text.lower()
                ):
                    filtered.append(fit)
            self.filtered_fits = filtered

        self._populate_fits()

    # -------------------------
    # Fit List
    # -------------------------
    def _populate_fits(self):
        self.fit_list.clear()

        for fit in self.filtered_fits:
            item = QListWidgetItem(fit.name)
            item.setData(Qt.UserRole, fit)
            self.fit_list.addItem(item)

    # -------------------------
    # Add Fit
    # -------------------------
    def _on_add_fit(self):
        dlg = AddFitDialog(self)
        if dlg.exec():
            new_fit = dlg.result_fit
            if new_fit:
                self.fits.append(new_fit)
                save_fits(self.fits)
                self._refresh_filtered_fits()

    # -------------------------
    # Edit Fit
    # -------------------------
    def _on_edit_fit(self):
        current_item = self.fit_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "No selection", "Select a fit to edit.")
            return

        fit: Fit = current_item.data(Qt.UserRole)

        dlg = AddFitDialog(self, existing_fit=fit)
        if not dlg.exec():
            return

        updated_fit = dlg.result_fit
        if updated_fit is None:
            return

        for idx, f in enumerate(self.fits):
            if f is fit or f.id == fit.id:
                self.fits[idx] = updated_fit
                break

        save_fits(self.fits)
        self._refresh_filtered_fits()
        self._select_fit_by_id(updated_fit.id)

    # -------------------------
    # Delete Fit
    # -------------------------
    def _on_delete_fit(self):
        current_item = self.fit_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "No selection", "Select a fit to delete.")
            return

        fit: Fit = current_item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self,
            "Delete fit",
            f"Are you sure you want to delete:\n\n{fit.name} – {fit.ship_type}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.fits = [f for f in self.fits if f is not fit and f.id != fit.id]
        save_fits(self.fits)

        self._refresh_filtered_fits()

        self.label_title.setText("Select a fit")
        self.label_stats.setText("(stats will appear here)")

    def _select_fit_by_id(self, fit_id: str):
        for i in range(self.fit_list.count()):
            item = self.fit_list.item(i)
            fit = item.data(Qt.UserRole)
            if isinstance(fit, Fit) and fit.id == fit_id:
                self.fit_list.setCurrentItem(item)
                break

    # -------------------------
    # Fit Selection
    # -------------------------
    def _on_fit_selected(self, current: QListWidgetItem, previous):
        if current is None:
            return

        fit: Fit = current.data(Qt.UserRole)
        evaluated = self.engine.evaluate_fit(fit, self.active_skill_profile)
        stats = evaluated.stats

        self.label_title.setText(f"{fit.name} – {fit.ship_type}")
        self.label_profile.setText(f"Profile: {self.active_skill_profile.name}")

        lines = [
            f"EHP: {stats.ehp:.1f}",
            f"DPS: {stats.dps:.1f}",
            f"Volley: {stats.volley:.1f}",
            f"Cap stable: {'Yes' if stats.cap_stable else 'No'}",
        ]

        if stats.cap_lasts_seconds is not None:
            lines.append(f"Cap lasts: {stats.cap_lasts_seconds:.0f} s")

        if stats.resist_profile:
            lines.append("")
            lines.append("Resists:")
            for dmg, val in stats.resist_profile.items():
                lines.append(f"  {dmg}: {val:.1f}%")

        if stats.misc:
            lines.append("")
            lines.append("Misc:")
            for key, val in stats.misc.items():
                lines.append(f"  {key}: {val}")

        self.label_stats.setText("\n".join(lines))
