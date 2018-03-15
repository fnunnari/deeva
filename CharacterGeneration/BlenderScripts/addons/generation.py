# Deeva - Character Generation Platform
# Copyright (C) 2018 Fabrizio Nunnari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pandas

from typing import List
from typing import Tuple
from typing import Optional


class AttributesTable:
    """Support class to load and manage attributes.

    Sample table format:
    id,name,type,min,max,labels
    277,Cheeks_Mass,nc,0.2,0.8,N/A
    287,Chin_Prominence,nc,0.0,1.0,N/A
    300,Eyebrows_Angle,nc,0.0,1.0,N/A
    323,Eyes_Size,nc,0.1,1.0,N/A
    """

    def __init__(self, table_filename):

        self._table = pandas.read_csv(filepath_or_buffer=table_filename)
        self._table.set_index('id', inplace=True)
        # print(self._table)

    def attributes_count(self) -> int:
        return len(self._table)

    def attribute_ids(self) -> List[int]:
        return [int(i) for i in self._table.index]

    def attribute_names(self) -> List[str]:
        return [s for s in self._table['name']]

    def attribute_name(self, attr_id: int) -> str:
        return self._table.loc[attr_id]['name']

    def attribute_range(self, attr_id: int) -> Tuple[float, float]:
        entry = self._table.loc[attr_id]
        return entry['min'], entry['max']


class IndividualsTable:
    """Support class to load and manage individuals of a generation.

    Sample table format:
    id,277-Cheeks_Mass,287-Chin_Prominence,300-Eyebrows_Angle,323-Eyes_Size
    1,0.35000000000000003,1.0,0.5,0.775
    2,0.5750000000000001,0.75,0.875,0.55
    3,0.42500000000000004,0.75,0.625,0.6625
    """

    def __init__(self, individuals_filename):
        self._table = pandas.read_csv(filepath_or_buffer=individuals_filename)  # type: pandas.DataFrame
        self._table.set_index('id', inplace=True)

    def count(self) -> int:
        return len(self._table)

    def ids(self) -> List[int]:
        return [int(i) for i in self._table.index]

    def attribute_values(self, individual_id: int) -> List[float]:
        attrib_values = self._table.loc[individual_id]
        return [float(a) for a in attrib_values]


def create_random_individuals(attributes_table: AttributesTable,
                              num_individuals: int,
                              out_filename: str,
                              random_segments: Optional[int]=None) -> None:
    import random

    attr_ids = attributes_table.attribute_ids()
    attr_names = attributes_table.attribute_names()

    header = ['id'] + ["{}-{}".format(index, name) for index, name in zip(attr_ids, attr_names)]

    with open(out_filename, 'w') as outfile:
        header_line = ','.join(header)
        outfile.write(header_line)
        outfile.write("\n")

        for i in range(num_individuals):

            entry = ['']

            for attr_id in attributes_table.attribute_ids():
                low, hi = attributes_table.attribute_range(attr_id=attr_id)

                if random_segments is None:
                    k = random.random()
                else:
                    segment = random.randint(0, random_segments-1)
                    k = segment / (random_segments-1)

                attr_val = low + (hi - low) * k

                entry.append(str(attr_val))

            entry_line = ",".join(entry)
            outfile.write(entry_line)
            outfile.write("\n")


def create_mblab_chars_dir(individuals: IndividualsTable, attributes: AttributesTable, dirpath: str) -> None:

    import os
    import json

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    for individual_id in individuals.ids():
        attr_ids = attributes.attribute_ids()
        attr_vals = individuals.attribute_values(individual_id=individual_id)
        if len(attr_ids) != len(attr_vals):
            raise Exception("Number of attribute IDs should be the same of Attrobute values. Found {} {}"
                            .format(len(attr_ids), len(attr_vals)))

        attributes_dict = {}
        for attr_id, attr_val in zip(attr_ids, attr_vals):
            attr_name = attributes.attribute_name(attr_id=attr_id)
            attributes_dict[attr_name] = attr_val

        out_dict = {
            "materialproperties": {},
            "metaproperties": {},
            "manuellab_vers": [1, 6, 1],
            "structural": attributes_dict
        }

        with open(os.path.join(dirpath, "{}.json".format(individual_id)), 'w') as outfile:
            json.dump(obj=out_dict, fp=outfile, indent=2)


#
#
#
# Invoke register if started from editor
if __name__ == "__main__":

    print("Test attrs")

    import os

    print(os.getcwd())

    attributes_tab = AttributesTable("../../BlenderScenes/VS-1-testvarset1.csv")

    print(attributes_tab.attributes_count())
    print(attributes_tab.attribute_ids())
    print(attributes_tab.attribute_names())

    for a in attributes_tab.attribute_ids():
        print(attributes_tab.attribute_name(a))
        print(attributes_tab.attribute_range(a))
    print("")

    # create_random_individuals(attributes_table=attributes_tab, num_individuals=30, out_filename="individuals2.csv", random_segments=9)

    indiv_tab = IndividualsTable("../../BlenderScenes/individuals2-fake.csv")
    print(indiv_tab._table)

    create_mblab_chars_dir(individuals=indiv_tab, attributes=attributes_tab, dirpath="generated_indiv")

    print("end.")
