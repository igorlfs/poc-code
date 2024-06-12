from collections import defaultdict

from pandas import DataFrame


# Reducing the redundancy in the subgroups mined, by unifying the names of equal coverage subgroup descriptions
def remove_redundant_subgroups(subgroups_df: DataFrame) -> DataFrame:
    # Use defaultdict to store coverage sets by subgroup
    subgroup_coverages = defaultdict(set)

    # Iterate through DataFrame rows and update coverage sets
    for _, row in subgroups_df.iterrows():
        subgroup = row["subgroup"]
        covered = set(row["covered"])

        # Check if subgroup already exists
        for existing_subgroup, coverage in subgroup_coverages.items():
            if (covered & coverage) == coverage:
                subgroup_coverages[existing_subgroup].add(subgroup)
                break
        else:
            subgroup_coverages[subgroup].add(subgroup)

    # Create a map of duplicates to the first subgroup
    subgroup_map = {
        duplicate: original
        for original, duplicates in subgroup_coverages.items()
        for duplicate in duplicates
        if len(duplicates) > 1
    }

    # Replace duplicate subgroups with their originals
    subgroups_df["subgroup"] = subgroups_df["subgroup"].replace(subgroup_map)

    return subgroups_df
