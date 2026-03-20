from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class PropertyEditor(QScrollArea):
    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.container)

    def clear_editor(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def bind(self, obj: Any, on_change: Callable[[], None]) -> None:
        self.clear_editor()
        if obj is None:
            self.layout.addWidget(QLabel("No selection"))
            return
        card = QFrame()
        card.setObjectName("panel")
        form = QFormLayout(card)
        title = QLabel(f"{obj.__class__.__name__} Inspector")
        title.setObjectName("sectionLabel")
        self.layout.addWidget(title)
        self.layout.addWidget(card)

        if not is_dataclass(obj):
            fallback = QLabel(str(obj))
            self.layout.addWidget(fallback)
            return

        for field_def in fields(obj):
            name = field_def.name
            value = getattr(obj, name)
            widget: QWidget
            if isinstance(value, bool):
                box = QCheckBox()
                box.setChecked(value)
                box.stateChanged.connect(lambda _state, n=name, b=box: self._set_value(obj, n, b.isChecked(), on_change))
                widget = box
            elif isinstance(value, int) and not isinstance(value, bool):
                spin = QSpinBox()
                spin.setRange(-999999, 999999)
                spin.setValue(value)
                spin.valueChanged.connect(lambda v, n=name: self._set_value(obj, n, v, on_change))
                widget = spin
            elif isinstance(value, float):
                spin = QDoubleSpinBox()
                spin.setRange(-999999.0, 999999.0)
                spin.setDecimals(2)
                spin.setValue(value)
                spin.valueChanged.connect(lambda v, n=name: self._set_value(obj, n, float(v), on_change))
                widget = spin
            elif isinstance(value, list):
                edit = QPlainTextEdit(", ".join(str(item) for item in value))
                edit.textChanged.connect(lambda n=name, e=edit: self._set_value(obj, n, [p.strip() for p in e.toPlainText().split(',') if p.strip()], on_change))
                edit.setMaximumHeight(80)
                widget = edit
            else:
                if name.endswith("type") or name.endswith("mode"):
                    combo = QComboBox()
                    combo.setEditable(True)
                    combo.addItems([str(value)])
                    combo.setCurrentText(str(value))
                    combo.currentTextChanged.connect(lambda text, n=name: self._set_value(obj, n, text, on_change))
                    widget = combo
                elif "notes" in name or "description" in name:
                    edit = QPlainTextEdit(str(value))
                    edit.textChanged.connect(lambda n=name, e=edit: self._set_value(obj, n, e.toPlainText(), on_change))
                    edit.setMaximumHeight(90)
                    widget = edit
                else:
                    line = QLineEdit(str(value))
                    line.textChanged.connect(lambda text, n=name: self._set_value(obj, n, text, on_change))
                    widget = line
            form.addRow(name.replace("_", " ").title(), widget)
        self.layout.addStretch(1)

    def _set_value(self, obj: Any, field_name: str, value: Any, on_change: Callable[[], None]) -> None:
        setattr(obj, field_name, value)
        on_change()
