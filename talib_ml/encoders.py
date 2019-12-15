from typing import List

import pandas as pd

import talib_ml as tml
from pandas_ml_utils.model.features_and_labels.target_encoder import TargetLabelEncoder

tml.__version__


class IntervalIndexEncoder(TargetLabelEncoder):

    def __init__(self, label_column: str, buckets: pd.IntervalIndex):
        self.label_column = label_column
        self.buckets = buckets

    @property
    def labels_source_columns(self) -> List[str]:
        return [self.label_column]

    @property
    def encoded_labels_columns(self) -> List[str]:
        return [f"{self.label_column}, {b}" for b in self.buckets]

    def encode(self, df: pd.DataFrame) -> pd.DataFrame:
        cat = df[self.label_column].ta_bucketize(self.buckets)
        one_hot_categories = cat.ta_one_hot_categories()
        one_hot_categories.columns = one_hot_categories.columns.to_flat_index()

        return one_hot_categories

    def decode(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.ta_one_hot_to_categories([self.buckets])

    def __len__(self):
        return len(self.buckets)