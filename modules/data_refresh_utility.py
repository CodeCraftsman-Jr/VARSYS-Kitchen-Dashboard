
"""
Data Refresh Utility
Manually refresh data in widgets
"""

def refresh_widget_data(widget):
    """Refresh data in any widget that supports it"""
    try:
        if hasattr(widget, 'refresh_all_data'):
            widget.refresh_all_data()
            print(f"Data refreshed for {widget.__class__.__name__}")
            return True
        else:
            print(f"Widget {widget.__class__.__name__} does not support data refresh")
            return False
    except Exception as e:
        print(f"Error refreshing data for {widget.__class__.__name__}: {e}")
        return False

def refresh_all_widgets(main_window):
    """Refresh data in all widgets in the main window"""
    refreshed_count = 0
    
    # Get all widgets from the main window
    for i in range(main_window.tabs.count()):
        widget = main_window.tabs.widget(i)
        if refresh_widget_data(widget):
            refreshed_count += 1
    
    print(f"Refreshed data in {refreshed_count} widgets")
    return refreshed_count
