#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qt Effects Utility
Provides Qt-native shadow and visual effects to replace unsupported CSS properties
"""

from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsBlurEffect, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class QtEffects:
    """Utility class for applying Qt-native visual effects"""
    
    @staticmethod
    def add_text_shadow(widget: QWidget, 
                       offset_x: float = 1.0, 
                       offset_y: float = 1.0, 
                       blur_radius: float = 2.0, 
                       color: str = "rgba(0,0,0,0.3)") -> QGraphicsDropShadowEffect:
        """
        Add text shadow effect to a widget (replaces CSS text-shadow)
        
        Args:
            widget: The widget to apply shadow to
            offset_x: Horizontal shadow offset
            offset_y: Vertical shadow offset
            blur_radius: Shadow blur radius
            color: Shadow color (CSS color string)
        
        Returns:
            QGraphicsDropShadowEffect: The created shadow effect
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(offset_x, offset_y)
        shadow.setBlurRadius(blur_radius)
        
        # Parse color string
        shadow_color = QtEffects._parse_color(color)
        shadow.setColor(shadow_color)
        
        widget.setGraphicsEffect(shadow)
        return shadow
    
    @staticmethod
    def add_box_shadow(widget: QWidget,
                      offset_x: float = 0.0,
                      offset_y: float = 2.0,
                      blur_radius: float = 8.0,
                      color: str = "rgba(0,0,0,0.1)") -> QGraphicsDropShadowEffect:
        """
        Add box shadow effect to a widget (replaces CSS box-shadow)
        
        Args:
            widget: The widget to apply shadow to
            offset_x: Horizontal shadow offset
            offset_y: Vertical shadow offset
            blur_radius: Shadow blur radius
            color: Shadow color (CSS color string)
        
        Returns:
            QGraphicsDropShadowEffect: The created shadow effect
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(offset_x, offset_y)
        shadow.setBlurRadius(blur_radius)
        
        # Parse color string
        shadow_color = QtEffects._parse_color(color)
        shadow.setColor(shadow_color)
        
        widget.setGraphicsEffect(shadow)
        return shadow
    
    @staticmethod
    def add_hover_shadow(widget: QWidget,
                        normal_blur: float = 4.0,
                        hover_blur: float = 12.0,
                        color: str = "rgba(0,0,0,0.15)") -> QGraphicsDropShadowEffect:
        """
        Add a shadow effect that can be modified for hover states
        
        Args:
            widget: The widget to apply shadow to
            normal_blur: Normal state blur radius
            hover_blur: Hover state blur radius
            color: Shadow color
        
        Returns:
            QGraphicsDropShadowEffect: The created shadow effect
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(normal_blur)
        
        shadow_color = QtEffects._parse_color(color)
        shadow.setColor(shadow_color)
        
        widget.setGraphicsEffect(shadow)
        
        # Store hover blur for later use
        widget.setProperty("normal_blur", normal_blur)
        widget.setProperty("hover_blur", hover_blur)
        widget.setProperty("shadow_effect", shadow)
        
        return shadow
    
    @staticmethod
    def add_focus_glow(widget: QWidget,
                      blur_radius: float = 8.0,
                      color: str = "rgba(59, 130, 246, 0.5)") -> QGraphicsDropShadowEffect:
        """
        Add a glow effect for focus states
        
        Args:
            widget: The widget to apply glow to
            blur_radius: Glow blur radius
            color: Glow color
        
        Returns:
            QGraphicsDropShadowEffect: The created glow effect
        """
        glow = QGraphicsDropShadowEffect()
        glow.setOffset(0, 0)  # No offset for glow
        glow.setBlurRadius(blur_radius)
        
        glow_color = QtEffects._parse_color(color)
        glow.setColor(glow_color)
        
        widget.setGraphicsEffect(glow)
        return glow
    
    @staticmethod
    def remove_effect(widget: QWidget):
        """Remove any graphics effect from a widget"""
        widget.setGraphicsEffect(None)
    
    @staticmethod
    def _parse_color(color_string: str) -> QColor:
        """
        Parse CSS color string to QColor
        
        Args:
            color_string: CSS color string (rgba, hex, etc.)
        
        Returns:
            QColor: Parsed color
        """
        color_string = color_string.strip()
        
        if color_string.startswith('rgba('):
            # Parse rgba(r, g, b, a)
            values = color_string[5:-1].split(',')
            if len(values) == 4:
                r = int(values[0].strip())
                g = int(values[1].strip())
                b = int(values[2].strip())
                a = float(values[3].strip())
                return QColor(r, g, b, int(a * 255))
        
        elif color_string.startswith('rgb('):
            # Parse rgb(r, g, b)
            values = color_string[4:-1].split(',')
            if len(values) == 3:
                r = int(values[0].strip())
                g = int(values[1].strip())
                b = int(values[2].strip())
                return QColor(r, g, b)
        
        elif color_string.startswith('#'):
            # Parse hex color
            return QColor(color_string)
        
        else:
            # Try to parse as named color
            return QColor(color_string)
        
        # Fallback to black
        return QColor(0, 0, 0, 76)  # 30% opacity black
    
    @staticmethod
    def create_button_shadow_states(button: QWidget):
        """
        Create shadow effects for button states (normal, hover, pressed)
        This replaces CSS box-shadow hover effects
        """
        # Normal state shadow
        normal_shadow = QtEffects.add_box_shadow(
            button, 
            offset_y=1, 
            blur_radius=3, 
            color="rgba(0,0,0,0.1)"
        )
        
        # Store references for state changes
        button.setProperty("normal_shadow", normal_shadow)
        
        # Connect to hover events if possible
        if hasattr(button, 'enterEvent'):
            original_enter = button.enterEvent
            original_leave = button.leaveEvent
            
            def enhanced_enter_event(event):
                # Enhance shadow on hover
                shadow = button.property("shadow_effect")
                if shadow:
                    shadow.setBlurRadius(6)
                    shadow.setOffset(0, 3)
                original_enter(event)
            
            def enhanced_leave_event(event):
                # Restore normal shadow
                shadow = button.property("shadow_effect")
                if shadow:
                    shadow.setBlurRadius(3)
                    shadow.setOffset(0, 1)
                original_leave(event)
            
            button.enterEvent = enhanced_enter_event
            button.leaveEvent = enhanced_leave_event


# Convenience functions for common effects
def add_title_shadow(label_widget):
    """Add shadow to title labels (replaces text-shadow: 1px 1px 2px rgba(0,0,0,0.3))"""
    return QtEffects.add_text_shadow(label_widget, 1, 1, 2, "rgba(0,0,0,0.3)")

def add_button_hover_shadow(button_widget):
    """Add hover shadow to buttons (replaces box-shadow hover effects)"""
    return QtEffects.add_hover_shadow(button_widget, 4, 8, "rgba(37, 99, 235, 0.3)")

def add_card_shadow(card_widget):
    """Add subtle shadow to cards and containers"""
    return QtEffects.add_box_shadow(card_widget, 0, 2, 4, "rgba(0,0,0,0.1)")

def add_focus_ring(input_widget):
    """Add focus ring to input widgets"""
    return QtEffects.add_focus_glow(input_widget, 6, "rgba(59, 130, 246, 0.4)")

def apply_modern_effects_to_widget(widget, widget_type="default"):
    """
    Apply modern Qt effects to replace CSS shadows

    Args:
        widget: The widget to apply effects to
        widget_type: Type of widget ("button", "card", "title", "input")
    """
    try:
        if widget_type == "button":
            add_button_hover_shadow(widget)
        elif widget_type == "card":
            add_card_shadow(widget)
        elif widget_type == "title":
            add_title_shadow(widget)
        elif widget_type == "input":
            add_focus_ring(widget)
        else:
            # Default subtle shadow
            QtEffects.add_box_shadow(widget, 0, 1, 3, "rgba(0,0,0,0.1)")
    except Exception as e:
        # Silently fail if effects can't be applied
        pass

def enhance_ui_with_effects(parent_widget):
    """
    Automatically enhance UI elements with Qt effects
    Recursively applies effects to child widgets based on their type
    """
    try:
        from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QLineEdit, QComboBox

        # Find and enhance buttons
        buttons = parent_widget.findChildren(QPushButton)
        for button in buttons:
            if not button.graphicsEffect():  # Don't override existing effects
                apply_modern_effects_to_widget(button, "button")

        # Find and enhance cards/frames
        frames = parent_widget.findChildren(QFrame)
        for frame in frames:
            if not frame.graphicsEffect():
                apply_modern_effects_to_widget(frame, "card")

        # Find and enhance input fields
        inputs = parent_widget.findChildren(QLineEdit) + parent_widget.findChildren(QComboBox)
        for input_widget in inputs:
            if not input_widget.graphicsEffect():
                apply_modern_effects_to_widget(input_widget, "input")

    except Exception as e:
        # Silently fail if enhancement can't be applied
        pass
