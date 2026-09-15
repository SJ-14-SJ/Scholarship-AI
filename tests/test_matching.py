import unittest
from pathlib import Path
import pandas as pd
from matching import find_scholarships, normalize_country, normalize_degree, field_match_type, funding_matches, deadline_score


def catalog():
    base = dict(provider='Example', country='USA', degree_level='Masters', field='Computer Science', min_cgpa_10=8, funding_tags='full,tuition', deadline='2030-02-01')
    return pd.DataFrame([dict(base, scholarship_name='Eligible'), dict(base, scholarship_name='Too high', min_cgpa_10=9), dict(base, scholarship_name='Expired', deadline='2029-12-31'), dict(base, scholarship_name='Unknown cutoff', min_cgpa_10='', deadline='Varies')])

class MatchingTests(unittest.TestCase):
    def search(self, data=None, **kwargs):
        return find_scholarships(catalog() if data is None else data, countries=['United States'], degree='postgraduate', field='computer science', cgpa=8, today='2030-01-01', **kwargs)

    def test_aliases(self):
        self.assertEqual(normalize_country(' U.S.A. '), 'usa')
        self.assertEqual(normalize_degree("Master's"), 'masters')

    def test_cgpa_boundary_and_expiry(self):
        rows, _ = self.search()
        self.assertEqual(set(rows.scholarship_name), {'Eligible', 'Unknown cutoff'})

    def test_expired_opt_in(self):
        rows, _ = self.search(include_expired=True)
        self.assertIn('Expired', set(rows.scholarship_name))

    def test_empty_results_schema(self):
        rows, _ = self.search(funding='Living Expenses')
        self.assertTrue(rows.empty)
        self.assertIn('match_score', rows.columns)

    def test_catalog_not_mutated(self):
        data = catalog(); before = data.copy(deep=True)
        self.search(data)
        pd.testing.assert_frame_equal(data, before)

    def test_blank_and_substring_collision(self):
        self.assertEqual(field_match_type('', 'computer science'), 'none')
        self.assertEqual(field_match_type('sustainable agriculture', 'AI'), 'none')

    def test_funding_tags_exact(self):
        self.assertTrue(funding_matches('full, tuition', 'Tuition'))
        self.assertFalse(funding_matches('partial', 'Full Funding'))

    def test_deadline_boundary(self):
        self.assertEqual(deadline_score(pd.Timestamp('2030-01-01'), today='2030-01-01'), 10)
        self.assertEqual(deadline_score(pd.Timestamp('2029-12-31'), today='2030-01-01'), 0)
        self.assertEqual(deadline_score(pd.NaT, today='2030-01-01'), 0)

    def test_bundled_catalog(self):
        data = pd.read_csv(Path(__file__).resolve().parents[1] / 'scholarships_database_v2.csv')
        rows, _ = self.search(data)
        self.assertIn('match_score', rows.columns)

if __name__ == '__main__':
    unittest.main()
