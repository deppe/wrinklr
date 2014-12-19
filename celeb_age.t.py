import unittest
import celeb_age

class TestCelebAge(unittest.TestCase):
    def testAges(self):
        self.assertEqual((1974, 11, 15), celeb_age.getPersonInfo('chad kroeger'))
        self.assertEqual((1935,  1,  8), celeb_age.getPersonInfo('elvis'))
        self.assertEqual((1990,  4, 15), celeb_age.getPersonInfo('EMMA WATSON'))

if __name__ == '__main__':
    unittest.main()