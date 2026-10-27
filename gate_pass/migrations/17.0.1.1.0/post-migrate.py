# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Reset all inward.operation records to 'entry' state.
    """
    cr.execute("UPDATE inward_operation SET state = 'entry'")
