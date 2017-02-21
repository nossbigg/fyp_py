from __future__ import absolute_import

import unittest

from controller.database_utils import get_collectionname_from_source_path


class ImportServiceUtilsTest(unittest.TestCase):
    dirname = "C:\\rootdir\\subdir"

    def test_get_collectionname_from_source_path(self):
        v = get_collectionname_from_source_path(self.dirname)
        self.assertEqual(v, "subdir")

    def test_get_collectionname_from_source_path_keep_only_valid_chars(self):
        v = get_collectionname_from_source_path(self.dirname + "#$")
        self.assertEqual(v, "subdir")

