#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""Test that survey data is accessed and served correctly"""

from itertools import islice
from unittest import TestCase

from SNData import csp, des, sdss


# Todo: Decide (and execute) whether to write test for table descriptions\
# Todo: Test of error when no data is available

class GeneralTests(TestCase):
    """Generic tests for a given survey"""

    def _test_empty_data(self, lim=float('inf')):
        """Test for empty tables in ``iter_data``

        Args:
            lim (int): Maximum number of tables to check (default: All tables)
        """

        for i, input_table in enumerate(self.module.iter_data()):
            if i >= lim:
                break

            obj_id = input_table.meta['obj_id']
            self.assertTrue(
                input_table,
                msg=f'Empty table for obj_id {obj_id}.')

    def _test_delete_data(self):
        """Test ``delete_module_data`` agrees with ``data_is_available``"""

        if not self.module.data_is_available():
            err_msg = f'No data found. Cannot test deletion.'
            raise RuntimeError(err_msg)

        self.module.delete_module_data()
        self.assertFalse(self.module.data_is_available())

    def _test_table_parsing(self):
        """Test no errors are raised by ``load_table`` when parsing args from
        ``get_available_tables``
        """

        table_names = self.module.get_available_tables()
        self.assertGreater(
            len(table_names), 0, f'No tables available for survey')

        err_msg = 'Empty table number {}'
        for table in table_names:
            print(table)
            try:
                table = self.module.load_table(table)

            except:
                self.fail(f'Cannot parse table {table}')

            self.assertTrue(table, err_msg.format(table))

    def _test_table_filtering(self, lim=None):
        """Test table filtering for ``iter_data``

        Args:
            lim (int): Maximum number of tables to check (default: All tables)
        """

        # Define ids to select on
        obj_ids = self.module.get_available_ids()[:lim]
        filter_ids = obj_ids[len(obj_ids) // 2:]

        # Create a test selection function
        def filter_func(data_table):
            return data_table.meta['obj_id'] in filter_ids

        # Check the selection function works
        iter_data = islice(
            self.module.iter_data(filter_func=filter_func), 0, lim)

        for table in iter_data:
            self.assertTrue(table.meta['obj_id'] in filter_ids)

    def _test_ids_are_sorted(self):
        """Test ``get_available_ids`` returns sorted ids"""

        obj_ids = self.module.get_available_ids()
        is_sorted = all(
            obj_ids[i] <= obj_ids[i + 1] for i in range(len(obj_ids) - 1))

        self.assertTrue(is_sorted)


class CSP_DR1(GeneralTests):
    """Tests for the csp.dr1 module"""

    @classmethod
    def setUpClass(cls):
        cls.module = csp.dr1
        cls.module.download_module_data()

    def test_0_empty_data(self):
        self._test_empty_data()

    def test_1_table_parsing(self):
        self._test_table_parsing()

    def test_2_table_filtering(self):
        self._test_table_filtering()

    def test_3_sorted_ids(self):
        self._test_ids_are_sorted()

    def test_4_delete_data(self):
        self._test_delete_data()


class CSP_DR3(GeneralTests):
    """Tests for the csp.dr3 module"""

    @classmethod
    def setUpClass(cls):
        cls.module = csp.dr3
        cls.module.download_module_data()

    def test_0_empty_data(self):
        self._test_empty_data()

    def test_1_table_parsing(self):
        self._test_table_parsing()

    def test_2_table_filtering(self):
        self._test_table_filtering()

    def test_3_sorted_ids(self):
        self._test_ids_are_sorted()

    def test_4_delete_data(self):
        self._test_delete_data()


class SDSS_Sako18(GeneralTests):
    """Tests for the sdss.sako18 module"""

    @classmethod
    def setUpClass(cls):
        cls.module = sdss.sako18
        cls.module.download_module_data()

    def test_0_empty_data(self):
        self._test_empty_data()

    def test_1_table_parsing(self):
        self._test_table_parsing()

    def test_2_table_filtering(self):
        self._test_table_filtering()

    def test_3_sorted_ids(self):
        self._test_ids_are_sorted()

    def test_4_delete_data(self):
        self._test_delete_data()


class DES_SN3YR(GeneralTests):
    """Tests for the des.SN3YR module"""

    @classmethod
    def setUpClass(cls):
        cls.module = des.sn3yr
        cls.module.download_module_data()

    def test_0_empty_data(self):
        self._test_empty_data()

    def test_1_table_parsing(self):
        self._test_table_parsing()

    def test_2_table_filtering(self):
        self._test_table_filtering()

    def test_3_sorted_ids(self):
        self._test_ids_are_sorted()

    def test_4_delete_data(self):
        self._test_delete_data()
