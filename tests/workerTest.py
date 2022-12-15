import os
import klsframe.klsframe.worker as klsworker


def test_export_import():
    _file = 'tmp.json'
    dummy = [
        {'view_assets': {
            "name_col": (-1, -1),
            "secondary_id_col": (-1, -1),
            "ip_col": (-1, -1),
            "numof_comp_col": (-1, -1),
            "numof_vulns_col": (-1, -1),
            "edit_button": (-1, -1),
            "next_page_button": (-1, -1),
            "search_bar": (-1, -1),
            "delete_button": (-1, -1),
            "confirm_deletion_button": (-1, -1)
        }},
        {'asset_components': {
            "name_col": (-1, -1),
            "cpe_col": (-1, -1),
            "port_col": (-1, -1)
        }},
        {'asset_details': {
            "name_field": (-1, -1),
            "client_id_field": (-1, -1),
            "secondary_id_field": (-1, -1),
            "asset_type_field": (-1, -1),
            "ip_field": (-1, -1),
            "purpose_field": (-1, -1),
            "description_field": (-1, -1)
        }}
    ]
    gui = klsworker.GUILayout().load(dummy)
    print("DEBUG 1", gui.to_json())
    gui.local_save(_file)
    gui2 = klsworker.GUILayout.load(_file)
    print("DEBUG 2", gui2.to_json())
    os.remove(_file)
    assert gui == gui2
