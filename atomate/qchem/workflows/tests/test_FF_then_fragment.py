# coding: utf-8

from __future__ import division, print_function, unicode_literals, absolute_import

import os
import unittest

from fireworks import FWorker
from fireworks.core.rocket_launcher import rapidfire
from atomate.utils.testing import AtomateTest
from pymatgen.core import Molecule
from pymatgen.io.qchem.inputs import QCInput
from atomate.qchem.powerups import use_fake_qchem
from atomate.qchem.workflows.base.FF_then_fragment import get_wf_FF_then_fragment

__author__ = "Samuel Blau"
__copyright__ = "Copyright 2018, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Samuel Blau"
__email__ = "samblau1@gmail.com"
__status__ = "Alpha"
__date__ = "6/1/18"
__credits__ = "Brandon Wood, Shyam Dwaraknath"


module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(module_dir, "..", "..", "..", "common", "test_files")


class TestFFthenfragment(AtomateTest):
    def test_FF_then_fragment(self):
        # location of test files
        test_FF_then_fragment_files = os.path.join(module_dir, "..", "..",
                                            "test_files", "FF_then_fragment_wf")
        # define starting molecule and workflow object
        initial_qcin = QCInput.from_file(
            os.path.join(test_FF_then_fragment_files, "block", "launcher_first",
                         "mol.qin.opt_0"))
        initial_mol = initial_qcin.molecule
        real_wf = get_wf_FF_then_fragment(molecule=initial_mol)
        # use powerup to replace run with fake run
        ref_dirs = {
            "first_FF":
            os.path.join(test_FF_then_fragment_files, "block", "launcher_first"),
            "fragment and FF_opt":
            os.path.join(test_FF_then_fragment_files, "block", "launcher_second")
        }
        fake_wf = use_fake_qchem(real_wf, ref_dirs)
        self.lp.add_wf(fake_wf)
        rapidfire(
            self.lp,
            fworker=FWorker(env={"db_file": os.path.join(db_dir, "db.json")}))

        wf_test = self.lp.get_wf_by_fw_id(1)
        self.assertTrue(
            all([s == "COMPLETED" for s in wf_test.fw_states.values()]))

        first_FF = self.get_task_collection().find_one({
            "task_label":
            "first_FF"
        })
        self.assertEqual(first_FF["calcs_reversed"][0]["input"]["solvent"],
                         None)
        self.assertEqual(first_FF["num_frequencies_flattened"], 0)


if __name__ == "__main__":
    unittest.main()
