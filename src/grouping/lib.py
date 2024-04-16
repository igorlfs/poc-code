import numpy as np
import pysubgroup as ps


# Define a custom quality function for a bidirectional search over the model's errors
class BidirectionalQFNumeric(ps.StandardQFNumeric):
    @staticmethod
    def bidirectional_qf_numeric(a, mean_dataset, instances_subgroup, mean_sg):
        return instances_subgroup**a * abs(mean_sg - mean_dataset)

    def __init__(self, a: float):
        self.a = a
        self.dataset_statistics = None
        self.all_target_values = None
        self.tpl = BidirectionalQFNumeric.tpl
        self.has_constant_statistics = False
        self.required_stat_attrs = ("size_sg", "mean")
        self.agg = np.mean
        self.read_centroid = lambda x: x.mean
        self.estimator = ps.StandardQFNumeric.Summation_Estimator(self)

    def evaluate(self, subgroup, target, data, statistics=None):
        statistics = self.ensure_statistics(subgroup, target, data, statistics)
        assert statistics is not None
        dataset = self.dataset_statistics
        return BidirectionalQFNumeric.bidirectional_qf_numeric(
            self.a,
            self.read_centroid(dataset),
            statistics.size_sg,
            self.read_centroid(statistics),
        )
