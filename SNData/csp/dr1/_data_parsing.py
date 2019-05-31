#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""This module defines functions for accessing locally available data files."""

from glob import glob
from pathlib import Path

import numpy as np
from astropy.io import ascii
from astropy.table import Column, Table, vstack

from . import _meta as meta
from ._data_download import _raise_for_data
from ... import _utils as utils


def get_available_tables():
    """Get numbers of available tables for this survey / data release"""

    table_nums = []
    for f in meta.table_dir.rglob('table*.dat'):
        table_nums.append(int(f.stem.lstrip('table')))

    return table_nums


def load_table(table_num):
    """Load a table from the data paper for this survey / data

    Args:
        table_num (int): The published table number
    """

    _raise_for_data()

    readme_path = meta.table_dir / 'ReadMe'
    table_path = meta.table_dir / f'table{table_num}.dat'
    if not table_path.exists:
        raise ValueError(f'Table {table_num} is not available.')

    return ascii.read(str(table_path), format='cds', readme=str(readme_path))


def get_available_ids():
    """Return a list of target object ids for the current survey

    Returns:
        A list of object ids as strings
    """

    _raise_for_data()

    files = glob(str(meta.spectra_dir / 'SN*.dat'))
    ids = ('20' + Path(f).name.split('_')[0].lstrip('SN') for f in files)
    return list(set(ids))


def get_data_for_id(obj_id):
    """Returns data for a given object id

    No data cuts are applied to the returned data. See ``get_available_ids()``
    for a list of available id values.

    Args:
        obj_id (str): The ID of the desired object

    Returns:
        An astropy table of data for the given ID
    """

    _raise_for_data()

    out_table = Table(
        names=['date', 'wavelength', 'flux', 'epoch', 'wavelength_range',
               'telescope', 'instrument'],
        dtype=[float, float, float, float, 'U3', 'U3', 'U2']
    )

    files = meta.spectra_dir.rglob(f'SN{obj_id[2:]}_*.dat')
    if not files:
        raise ValueError(f'No data found for obj_id {obj_id}')

    for f in files:
        spectral_data = Table.read(
            f, format='ascii', names=['wavelength', 'flux'])

        # Get meta data for observation
        file_comments = spectral_data.meta['comments']
        redshift = float(file_comments[1].lstrip('Redshift: '))
        max_date = float(file_comments[2].lstrip('JDate_of_max: '))
        obs_date = float(file_comments[3].lstrip('JDate_of_observation: '))
        epoch = float(file_comments[4].lstrip('Epoch: '))
        _, _, wrange, telescope, instrument = f.stem.split('_')

        date_col = Column(data=np.full(len(spectral_data), obs_date), name='date')
        epoch_col = Column(data=np.full(len(spectral_data), epoch), name='epoch')
        wr_col = Column(data=np.full(len(spectral_data), wrange), name='wavelength_range')
        tel_col = Column(data=np.full(len(spectral_data), telescope), name='telescope')
        inst_col = Column(data=np.full(len(spectral_data), instrument), name='instrument')
        spectral_data.add_columns([date_col, epoch_col, wr_col, tel_col, inst_col])

        out_table = vstack([out_table, spectral_data])

    out_table.meta['redshift'] = redshift
    out_table.meta['JDate_of_max'] = max_date
    out_table.meta['obj_id'] = obj_id

    return out_table


def iter_data(verbose=False):
    """Iterate through all available targets and yield data tables

    An optional progress bar can be formatted by passing a dictionary of tqdm
    arguments.

    Args:
        verbose (bool, dict): Optionally display progress bar while iterating

    Yields:
        Astropy tables
    """

    iterable = utils.build_pbar(get_available_ids(), verbose)
    for id_val in iterable:
        data_table = get_data_for_id(id_val)
        if data_table:
            yield data_table
