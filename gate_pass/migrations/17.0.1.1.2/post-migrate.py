# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Reset all outward.gate.entry records to 'entry' state.
    """
    # Check if table exists to avoid errors on fresh install (though fresh install skips migration usually)
    cr.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'outward_gate_entry'")
    if cr.fetchone()[0]:
        cr.execute("UPDATE outward_gate_entry SET state = 'entry'")
