from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from map_editor.map_scene import MapScene, MapView
from models.project import ExperienceProject, LayoutItem
from widgets.property_editor import PropertyEditor


class MapPage(QWidget):
    def __init__(self, project_getter, on_changed):
        super().__init__()
        self.project_getter = project_getter
        self.on_changed = on_changed
        self.selected_item: LayoutItem | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        title = QLabel("Layout / Map Designer")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Design spatial layouts, place rooms/zones, and align programming objects against a floorplan or concept image.")
        subtitle.setStyleSheet("color: #8fa7ba;")
        root.addWidget(title)
        root.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.add_item_btn = QPushButton("Create Layout Item")
        self.import_bg_btn = QPushButton("Import Background")
        self.clear_bg_btn = QPushButton("Clear Background")
        self.zoom_out_btn = QPushButton("-")
        self.zoom_in_btn = QPushButton("+")
        self.zoom_reset_btn = QPushButton("100%")
        self.fit_btn = QPushButton("Fit View")
        self.zoom_label = QLabel("Zoom: 100%")
        self.bg_visible = QCheckBox("Background Visible")
        self.bg_lock = QCheckBox("Lock Background")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(55)
        self.opacity_slider.setMaximumWidth(140)
        self.opacity_label = QLabel("Opacity")

        for widget in [self.add_item_btn, self.import_bg_btn, self.clear_bg_btn, self.zoom_out_btn, self.zoom_in_btn, self.zoom_reset_btn, self.fit_btn, self.zoom_label]:
            toolbar.addWidget(widget)
        toolbar.addSpacing(10)
        toolbar.addWidget(self.bg_visible)
        toolbar.addWidget(self.bg_lock)
        toolbar.addWidget(self.opacity_label)
        toolbar.addWidget(self.opacity_slider)
        toolbar.addStretch(1)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.item_list = QListWidget()
        self.item_list.setMinimumWidth(220)
        self.item_list.currentRowChanged.connect(self.select_item_by_row)
        self.scene = MapScene(self._item_moved, self._scene_selection_changed)
        self.view = MapView(self.scene)
        self.view.zoom_changed.connect(self._update_zoom_label)
        self.inspector = PropertyEditor()
        splitter.addWidget(self.item_list)
        splitter.addWidget(self.view)
        splitter.addWidget(self.inspector)
        splitter.setSizes([240, 980, 340])
        root.addWidget(splitter, 1)

        self.add_item_btn.clicked.connect(self.add_item)
        self.import_bg_btn.clicked.connect(self.import_background)
        self.clear_bg_btn.clicked.connect(self.clear_background)
        self.zoom_in_btn.clicked.connect(self.view.zoom_in)
        self.zoom_out_btn.clicked.connect(self.view.zoom_out)
        self.zoom_reset_btn.clicked.connect(self.view.reset_zoom)
        self.fit_btn.clicked.connect(self.view.fit_scene)
        self.bg_visible.toggled.connect(self._background_controls_changed)
        self.bg_lock.toggled.connect(self._background_controls_changed)
        self.opacity_slider.valueChanged.connect(self._background_controls_changed)

    def refresh(self, project: ExperienceProject) -> None:
        selected_id = self.selected_item.id if self.selected_item else None
        self.item_list.blockSignals(True)
        self.item_list.clear()
        for item in project.layout_items:
            self.item_list.addItem(f"{item.name} [{item.item_type}]")
        self.item_list.blockSignals(False)
        self.bg_visible.blockSignals(True)
        self.bg_lock.blockSignals(True)
        self.opacity_slider.blockSignals(True)
        self.bg_visible.setChecked(project.layout_canvas.background_visible)
        self.bg_lock.setChecked(project.layout_canvas.background_locked)
        self.opacity_slider.setValue(int(project.layout_canvas.background_opacity * 100))
        self.bg_visible.blockSignals(False)
        self.bg_lock.blockSignals(False)
        self.opacity_slider.blockSignals(False)
        self.scene.load_project(project.layout_items, project.layout_canvas)
        if project.layout_canvas.last_zoom_percent != self.view.zoom_percent:
            self.view.reset_zoom()
            self.view.set_zoom_percent(project.layout_canvas.last_zoom_percent)
        if project.layout_items:
            target_row = next((idx for idx, item in enumerate(project.layout_items) if item.id == selected_id), 0)
            self.item_list.setCurrentRow(target_row)
            self.scene.select_item(project.layout_items[target_row].id)
        else:
            self.selected_item = None
            self.inspector.bind(None, self.on_changed)

    def add_item(self) -> None:
        project = self.project_getter()
        item = LayoutItem(name=f"Item {len(project.layout_items) + 1}", item_type="Room", x=80 + len(project.layout_items) * 35, y=80 + len(project.layout_items) * 28)
        project.layout_items.append(item)
        self.selected_item = item
        self.on_changed()
        self.refresh(project)

    def select_item_by_row(self, row: int) -> None:
        project = self.project_getter()
        self.selected_item = project.layout_items[row] if 0 <= row < len(project.layout_items) else None
        self.scene.select_item(self.selected_item.id if self.selected_item else None)
        self.inspector.bind(self.selected_item, self._inspector_changed)

    def _scene_selection_changed(self, item: LayoutItem | None) -> None:
        self.selected_item = item
        if item is None:
            self.inspector.bind(None, self.on_changed)
            return
        for row, candidate in enumerate(self.project_getter().layout_items):
            if candidate.id == item.id:
                self.item_list.blockSignals(True)
                self.item_list.setCurrentRow(row)
                self.item_list.blockSignals(False)
                break
        self.inspector.bind(self.selected_item, self._inspector_changed)

    def _inspector_changed(self) -> None:
        project = self.project_getter()
        if self.selected_item is not None:
            self.scene.refresh_item(self.selected_item)
            for row, item in enumerate(project.layout_items):
                if item.id == self.selected_item.id and self.item_list.item(row) is not None:
                    self.item_list.item(row).setText(f"{item.name} [{item.item_type}]")
        self.on_changed()

    def _item_moved(self, item: LayoutItem) -> None:
        self.selected_item = item
        self.project_getter().layout_canvas.last_zoom_percent = self.view.zoom_percent
        self.on_changed()

    def import_background(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Layout Background", "", "Images (*.png *.jpg *.jpeg)")
        if not path:
            return
        project = self.project_getter()
        project.layout_canvas.background_image = path
        project.layout_canvas.background_visible = True
        project.layout_canvas.fit_background_to_canvas = True
        self.on_changed()
        self._reload_scene_only(project)
        self.view.fit_scene()

    def clear_background(self) -> None:
        project = self.project_getter()
        project.layout_canvas.background_image = ""
        self.on_changed()
        self._reload_scene_only(project)

    def _background_controls_changed(self) -> None:
        project = self.project_getter()
        project.layout_canvas.background_visible = self.bg_visible.isChecked()
        project.layout_canvas.background_locked = self.bg_lock.isChecked()
        project.layout_canvas.background_opacity = self.opacity_slider.value() / 100.0
        self.on_changed()
        self._reload_scene_only(project)

    def _update_zoom_label(self, zoom_percent: int) -> None:
        self.zoom_label.setText(f"Zoom: {zoom_percent}%")
        self.project_getter().layout_canvas.last_zoom_percent = zoom_percent

    def _reload_scene_only(self, project: ExperienceProject) -> None:
        self.scene.load_project(project.layout_items, project.layout_canvas)
        self.scene.select_item(self.selected_item.id if self.selected_item else None)
