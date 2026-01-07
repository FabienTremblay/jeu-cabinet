import pytest

@pytest.mark.skipif(True, reason="Activer si l'idempotence par hook est conservée.")
def test_same_subphase_twice_no_double_effect(pm):
    e = pm.creer("minimal", "G-400", {"J1":"A","J2":"B"}, seed=10)
    e.demarrer_partie()
    val0 = e.axes["economique"].valeur
    e._run_subphase("monde")   # applique -2
    val1 = e.axes["economique"].valeur
    e._run_subphase("monde")   # ignoré (hook_skip)
    val2 = e.axes["economique"].valeur
    assert val1 == val0 - 2 and val2 == val1
