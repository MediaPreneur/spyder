# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Control widgets used by ShellWidget"""

# Third-party imports
from qtpy.QtCore import Qt, QUrl, Signal
from qtpy.QtGui import QColor, QDesktopServices, QTextFrameFormat
from qtpy.QtWidgets import QApplication, QTextEdit

# Local imports
from spyder.utils.palette import QStylePalette
from spyder.utils.qthelpers import restore_keyevent
from spyder.widgets.calltip import CallTipWidget
from spyder.widgets.mixins import (BaseEditMixin, GetHelpMixin,
                                   TracebackLinksMixin)


class ControlWidget(TracebackLinksMixin, GetHelpMixin,
                    QTextEdit, BaseEditMixin):
    """
    Subclass of QTextEdit with features from Spyder's mixins to use as the
    control widget for IPython widgets
    """
    QT_CLASS = QTextEdit
    visibility_changed = Signal(bool)
    sig_go_to_error_requested = Signal(str)
    focus_changed = Signal()

    sig_help_requested = Signal(dict)
    """
    This signal is emitted to request help on a given object's `name`.

    help_data: dict
        Example `{'name': str, 'ignore_unknown': bool}`.
    """

    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        BaseEditMixin.__init__(self)
        TracebackLinksMixin.__init__(self)
        GetHelpMixin.__init__(self)

        self.calltip_widget = CallTipWidget(self, hide_timer_on=False)
        self.found_results = []

        # To not use Spyder calltips obtained through the monitor
        self.calltips = False

        # To detect anchors and make them clickable
        self.anchor = None

    # ---- Public methods ----------------------------------------------------
    def insert_horizontal_ruler(self):
        """
        Insert a horizontal ruler with the appropriate color according
        to our theme in the current cursor position.

        We have to do this because html hr elements can't be stylized
        in QTextEdit.

        Taken from https://stackoverflow.com/a/50016969/438386
        """
        ruler = QTextFrameFormat()
        ruler.setHeight(1)
        ruler.setWidth(10000)
        ruler.setBackground(QColor(QStylePalette.COLOR_TEXT_1))
        cursor = self.textCursor()
        cursor.insertFrame(ruler)

    # ---- Private methods ---------------------------------------------------
    def _key_paren_left(self, text):
        """ Action for '(' """
        self.current_prompt_pos = self.parentWidget()._prompt_pos
        if self.get_current_line_to_cursor():
            last_obj = self.get_last_obj()
            if last_obj and not last_obj.isdigit():
                self.show_object_info(last_obj)
        self.insert_text(text)

    # ---- Qt methods --------------------------------------------------------
    def showEvent(self, event):
        """Reimplement Qt Method"""
        self.visibility_changed.emit(True)

    def keyPressEvent(self, event):
        """Reimplement Qt Method - Basic keypress event handler"""
        event, text, key, ctrl, shift = restore_keyevent(event)
        if (key == Qt.Key_ParenLeft and not self.has_selected_text()
                and self.help_enabled and not self.parent()._reading):
            self._key_paren_left(text)
        else:
            # Let the parent widget handle the key press event
            QTextEdit.keyPressEvent(self, event)

    def focusInEvent(self, event):
        """Reimplement Qt method to send focus change notification"""
        self.focus_changed.emit()
        return super(ControlWidget, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """Reimplement Qt method to send focus change notification"""
        self.focus_changed.emit()
        return super(ControlWidget, self).focusOutEvent(event)

    def mouseMoveEvent(self, event):
        """Detect anchors and change cursor shape accordingly."""
        self.anchor = self.anchorAt(event.pos())
        if self.anchor:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        else:
            QApplication.restoreOverrideCursor()
        super(ControlWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Ooen anchors when clicked."""
        if self.anchor:
            QDesktopServices.openUrl(QUrl(self.anchor))
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.anchor = None
        else:
            super(ControlWidget, self).mouseReleaseEvent(event)


class PageControlWidget(QTextEdit, BaseEditMixin):
    """
    Subclass of QTextEdit with features from Spyder's mixins.BaseEditMixin to
    use as the paging widget for IPython widgets
    """
    QT_CLASS = QTextEdit
    visibility_changed = Signal(bool)
    show_find_widget = Signal()
    focus_changed = Signal()

    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        BaseEditMixin.__init__(self)
        self.found_results = []

    def showEvent(self, event):
        """Reimplement Qt Method"""
        self.visibility_changed.emit(True)

    def keyPressEvent(self, event):
        """Reimplement Qt Method - Basic keypress event handler"""
        event, text, key, ctrl, shift = restore_keyevent(event)

        if key == Qt.Key_Slash and self.isVisible():
            self.show_find_widget.emit()
        else:
            # Let the parent widget handle the key press event
            QTextEdit.keyPressEvent(self, event)

    def focusInEvent(self, event):
        """Reimplement Qt method to send focus change notification"""
        self.focus_changed.emit()
        return super(PageControlWidget, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """Reimplement Qt method to send focus change notification"""
        self.focus_changed.emit()
        return super(PageControlWidget, self).focusOutEvent(event)
