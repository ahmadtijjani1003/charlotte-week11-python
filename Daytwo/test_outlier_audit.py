"""Unit tests for the Wine Chemistry Outlier Audit."""
import unittest
import pandas as pd

from outlier_audit import audit_data, REQUIRED


def sample_data():
    """Small valid dataset with enough variation for statistical checks."""
    return pd.DataFrame({
        "sample_id": [f"S{i}" for i in range(1, 9)],
        "alcohol": [12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7],
        "malic_acid": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
        "color_intensity": [4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7],
        "proline": [500, 510, 520, 530, 540, 550, 560, 570],
        "target": [0, 0, 0, 1, 1, 1, 2, 2],
    })


class TestOutlierAudit(unittest.TestCase):
    def test_missing_required_column_fails_clearly(self):
        data = sample_data().drop(columns=["target"])
        with self.assertRaisesRegex(ValueError, "target"):
            audit_data(data)

    def test_domain_invalid_rows_are_quarantined(self):
        data = sample_data()
        data.loc[0, "proline"] = 0
        data.loc[1, "malic_acid"] = -0.5
        data.loc[2, "malic_acid"] = float("nan")

        result = audit_data(data)
        self.assertEqual(len(result["quarantined"]), 3)
        self.assertEqual(len(result["retained"]), 5)
        self.assertTrue(result["quarantined"]["domain_invalid"].all())

    def test_statistical_outlier_is_flagged_but_not_automatically_quarantined(self):
        data = sample_data()
        data.loc[7, "proline"] = 5000

        result = audit_data(data)
        row = result["retained"].loc[result["retained"]["sample_id"] == "S8"].iloc[0]
        self.assertTrue(
            bool(row["proline_z_flag"] or row["proline_iqr_flag"])
        )
        self.assertFalse(bool(row["domain_invalid"]))
        self.assertEqual(len(result["quarantined"]), 0)

    def test_zero_variance_column_is_handled_safely(self):
        data = sample_data()
        data["malic_acid"] = 1.25

        result = audit_data(data)
        self.assertFalse(result["retained"]["malic_acid_z_flag"].any())
        self.assertFalse(result["retained"]["malic_acid_iqr_flag"].any())

    def test_original_measurements_and_sample_id_are_preserved(self):
        data = sample_data()
        result = audit_data(data)
        retained = result["retained"]

        self.assertEqual(retained["sample_id"].tolist(), data["sample_id"].tolist())
        pd.testing.assert_series_equal(
            retained["malic_acid"].reset_index(drop=True),
            data["malic_acid"].reset_index(drop=True),
            check_names=True,
        )
        self.assertEqual(
            result["summary"].loc[0, "total_input"], len(data)
        )
        self.assertEqual(
            result["summary"].loc[0, "retained"]
            + result["summary"].loc[0, "quarantined"],
            len(data),
        )


if __name__ == "__main__":
    unittest.main()
