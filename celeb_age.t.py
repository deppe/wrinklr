import unittest
import celeb_age

class TestCelebAge(unittest.TestCase):
    def testAges(self):
        age = celeb_age.getPersonInfo
        self.assertEqual((1974, 11, 15), age('chad kroeger'))
        self.assertEqual((1935,  1,  8), age('elvis'))
        self.assertEqual((1990,  4, 15), age('EMMA WATSON'))
        self.assertEqual((-1728, 0,  0), age('hammurabi'))


        self.assertRaises(celeb_age.NoBirthdayException, celeb_age.getPersonInfo, 'tower of hanoi')

if __name__ == '__main__':
    unittest.main()