import unittest
from mathos.research.millennium_followup_20261124 import run

class FollowupTest(unittest.TestCase):
    def test_all_tracks_and_no_promotion(self):
        r=run()
        self.assertEqual(r['globally_proved'],0)
        self.assertEqual(r['status'],'BOUNDED_RESEARCH_NOT_CERTIFIED')
        self.assertEqual(set(r)-{'status','globally_proved'},
                         {'rh','p_vs_np','navier_stokes','yang_mills','hodge','bsd','poincare'})

if __name__=='__main__':
    unittest.main()
