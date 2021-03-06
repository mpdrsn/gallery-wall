import unittest
import server
import utilities
import doctest
import os
import seed_database as seed
import arrange as ar
from model import Picture, User, connect_to_db

# 
connect_to_db(server.app)


def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    # tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class UtilitiesParserFunctionsTestCase(unittest.TestCase):

    def test_to_clean_string_from_input(self):

        # Case for string already clean
        test_in = 'foo13ar'
        expect_out = 'foo13ar'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 100),
                         expect_out)

        # Case for string not clean
        test_in = 'fo*o13!ar; droptables'
        expect_out = 'foo13ardroptables'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 100),
                         expect_out)

        # Case for string only unclean
        test_in = '&*#%;+'
        self.assertIsNone(utilities.to_clean_string_from_input(test_in, 100))

        # Case for string empty
        test_in = ''
        self.assertIsNone(utilities.to_clean_string_from_input(test_in, 100))

        # Case for string unclean and too long
        test_in = 'fo*o13!ar; droptables'
        expect_out = 'foo'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 3),
                         expect_out)

    def test_to_float_from_input(self):

        # Case for spaces
        test_in = '  13 '
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for other characters arround
        test_in = 'foo13*ar'
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for decimals
        test_in = '13.14'
        expect_out = 13.14
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for zero pad
        test_in = '00013'
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for empty
        test_in = ''
        self.assertIsNone(utilities.to_float_from_input(test_in))

        # Case for all unclean
        test_in = 'juihiuhr&&*@'
        self.assertIsNone(utilities.to_float_from_input(test_in))

        # Case for negative
        test_in = '-13.0 '
        expect_out = -13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for fractional
        test_in = '0.13'
        expect_out = 0.13
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for zero
        test_in = '-0.0 '
        expect_out = 0.0
        self.assertAlmostEqual(utilities.to_float_from_input(test_in),
                               expect_out)


class NavigationServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = os.environ['FLASK_APP_SECRET_KEY']

    def test_navigation_logged_out(self):

        result = self.client.get('/navigation')
        self.assertIn('Galleries', result.data)
        self.assertIn('Walls', result.data)
        self.assertNotIn('Curate', result.data)
        self.assertNotIn('Upload', result.data)


class NavigationServerRoutesLoggedInTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = os.environ['FLASK_APP_SECRET_KEY']

        with self.client as c:
            with c.session_transaction() as se:
                se['user_id'] = 13
                se['username'] = 'foo'

    def test_navigation_logged_in(self):

        result = self.client.get('/navigation')
        self.assertIn('Galleries', result.data)
        self.assertIn('Walls', result.data)
        self.assertIn('Curate', result.data)
        self.assertIn('Upload', result.data)

    # tear down by logging out
    def tearDown(self):

        with self.client as c:
            with c.session_transaction() as se:
                se.pop('user_id')
                se.pop('username')


class LoginServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True

    def test_login_signup(self):
        result = self.client.get('/login')
        self.assertIn('Username', result.data)
        self.assertIn('Email', result.data)
        self.assertIn('Password', result.data)


class WorkspaceInitTestCase(unittest.TestCase):

    # Test Gallery (11)
    # 11 | 49, 42, 41
    # 41  |   1   |   4   |   4   |   love_4x4.jpg    |   love    |   @elsabirch  |   public
    # 42  |   1   |   6   |   6   |   banana_6x6.jpg  |   banana  |   @elsabirch  |   public
    # 49  |   1   |   10  |   8   |   wave_10x8.jpg   |   wave    |   @elsabirch  |   public

    def setUp(self):

        server.app.config['TESTING'] = True

        seed.clean_db()

        seed_files = {
            'users': "seed/seed_test_users.txt",
            'pictures': "seed/seed_test_pictures.txt",
            'galleries': "seed/seed_test_galleries.txt",
            'memberships': "seed/seed_test_memberships.txt",
            'walls': "seed/seed_test_walls.txt",
            'placements': "seed/seed_test_placements.txt",
        }

        seed.seed_all(seed_files)

    def test_init(self):

        wkspc = ar.Workspace(11)

        self.assertEqual(wkspc.gallery_id, 11)
        self.assertEqual(wkspc.len, 3)
        self.assertEqual(wkspc.margin, 2)

        self.assertIn(41, wkspc.pics)
        self.assertIn(42, wkspc.pics)
        self.assertIn(49, wkspc.pics)

        # All pics are instance of correct class
        for p in wkspc.pics:
            self.assertTrue(isinstance(wkspc.pics[p], ar.Pic))

        # Correct number of pics
        self.assertEqual(len(wkspc.pics), 3)


class WorkspaceRealignTestCase(unittest.TestCase):

    def setUp(self):

        server.app.config['TESTING'] = True
        seed.clean_db()

        seed_files = {
            'users': "seed/seed_test_users.txt",
            'pictures': "seed/seed_test_pictures.txt",
            'galleries': "seed/seed_test_galleries.txt",
            'memberships': "seed/seed_test_memberships.txt",
            'walls': "seed/seed_test_walls.txt",
            'placements': "seed/seed_test_placements.txt",
        }

        seed.seed_all(seed_files)

    def test_positive_quad(self):

        # Test Gallery (11)
        # 11 | 49, 42, 41
        # 41  |   1   |   4   |   4   |   love_4x4.jpg    |   love    |   @elsabirch  |   public
        # 42  |   1   |   6   |   6   |   banana_6x6.jpg  |   banana  |   @elsabirch  |   public
        # 49  |   1   |   10  |   8   |   wave_10x8.jpg   |   wave    |   @elsabirch  |   public

        wkspc = ar.Workspace(11)
        arngr = ar.Arranger(wkspc)

        wkspc.pics[41].x1 = 1
        wkspc.pics[41].y1 = 1
        wkspc.pics[41].x2 = wkspc.pics[41].x1 + wkspc.pics[41].w
        wkspc.pics[41].y2 = wkspc.pics[41].y1 + wkspc.pics[41].h

        wkspc.pics[42].x1 = 10
        wkspc.pics[42].y1 = 1
        wkspc.pics[42].x2 = wkspc.pics[42].x1 + wkspc.pics[42].w
        wkspc.pics[42].y2 = wkspc.pics[42].y1 + wkspc.pics[42].h

        wkspc.pics[49].x1 = 1
        wkspc.pics[49].y1 = 10
        wkspc.pics[49].x2 = wkspc.pics[49].x1 + wkspc.pics[49].w
        wkspc.pics[49].y2 = wkspc.pics[49].y1 + wkspc.pics[49].h

        arngr.realign_to_origin()

        self.assertEqual(wkspc.pics[41].x1, 0)
        self.assertEqual(wkspc.pics[41].y1, 0)
        self.assertEqual(wkspc.pics[41].x2, 6)
        self.assertEqual(wkspc.pics[41].y2, 6)

        self.assertEqual(wkspc.pics[42].x1, 9)
        self.assertEqual(wkspc.pics[42].y1, 0)
        self.assertEqual(wkspc.pics[42].x2, 17)
        self.assertEqual(wkspc.pics[42].y2, 8)

        self.assertEqual(wkspc.pics[49].x1, 0)
        self.assertEqual(wkspc.pics[49].y1, 9)
        self.assertEqual(wkspc.pics[49].x2, 12)
        self.assertEqual(wkspc.pics[49].y2, 19)

    def test_all_quad(self):

        # Test Gallery (11)
        # 11 | 49, 42, 41
        # 41  |   1   |   4   |   4   |   love_4x4.jpg    |   love    |   @elsabirch  |   public
        # 42  |   1   |   6   |   6   |   banana_6x6.jpg  |   banana  |   @elsabirch  |   public
        # 49  |   1   |   10  |   8   |   wave_10x8.jpg   |   wave    |   @elsabirch  |   public

        wkspc = ar.Workspace(11)
        arngr = ar.Arranger(wkspc)

        wkspc.pics[41].x1 = -4
        wkspc.pics[41].y1 = -4
        wkspc.pics[41].x2 = wkspc.pics[41].x1 + wkspc.pics[41].w
        wkspc.pics[41].y2 = wkspc.pics[41].y1 + wkspc.pics[41].h

        wkspc.pics[42].x1 = 5
        wkspc.pics[42].y1 = -4
        wkspc.pics[42].x2 = wkspc.pics[42].x1 + wkspc.pics[42].w
        wkspc.pics[42].y2 = wkspc.pics[42].y1 + wkspc.pics[42].h

        wkspc.pics[49].x1 = -4
        wkspc.pics[49].y1 = 5
        wkspc.pics[49].x2 = wkspc.pics[49].x1 + wkspc.pics[49].w
        wkspc.pics[49].y2 = wkspc.pics[49].y1 + wkspc.pics[49].h

        arngr.realign_to_origin()

        self.assertEqual(wkspc.pics[41].x1, 0)
        self.assertEqual(wkspc.pics[41].y1, 0)
        self.assertEqual(wkspc.pics[41].x2, 6)
        self.assertEqual(wkspc.pics[41].y2, 6)

        self.assertEqual(wkspc.pics[42].x1, 9)
        self.assertEqual(wkspc.pics[42].y1, 0)
        self.assertEqual(wkspc.pics[42].x2, 17)
        self.assertEqual(wkspc.pics[42].y2, 8)

        self.assertEqual(wkspc.pics[49].x1, 0)
        self.assertEqual(wkspc.pics[49].y1, 9)
        self.assertEqual(wkspc.pics[49].x2, 12)
        self.assertEqual(wkspc.pics[49].y2, 19)


class WorkspaceWallSizeTestCase(unittest.TestCase):

    def setUp(self):

        server.app.config['TESTING'] = True
        seed.clean_db()

        seed_files = {
            'users': "seed/seed_test_users.txt",
            'pictures': "seed/seed_test_pictures.txt",
            'galleries': "seed/seed_test_galleries.txt",
            'memberships': "seed/seed_test_memberships.txt",
            'walls': "seed/seed_test_walls.txt",
            'placements': "seed/seed_test_placements.txt",
        }

        seed.seed_all(seed_files)

    def test_wall_size(self):

        # Test Gallery (11)
        # 11 | 49, 42, 41
        # 41  |   1   |   4   |   4   |   love_4x4.jpg    |   love    |   @elsabirch  |   public
        # 42  |   1   |   6   |   6   |   banana_6x6.jpg  |   banana  |   @elsabirch  |   public
        # 49  |   1   |   10  |   8   |   wave_10x8.jpg   |   wave    |   @elsabirch  |   public

        wkspc = ar.Workspace(11)
        arngr = ar.Arranger(wkspc)

        wkspc.pics[41].x1 = 0
        wkspc.pics[41].y1 = 0
        wkspc.pics[41].x2 = wkspc.pics[41].x1 + wkspc.pics[41].w
        wkspc.pics[41].y2 = wkspc.pics[41].y1 + wkspc.pics[41].h

        wkspc.pics[42].x1 = 9
        wkspc.pics[42].y1 = 0
        wkspc.pics[42].x2 = wkspc.pics[42].x1 + wkspc.pics[42].w
        wkspc.pics[42].y2 = wkspc.pics[42].y1 + wkspc.pics[42].h

        wkspc.pics[49].x1 = 0
        wkspc.pics[49].y1 = 9
        wkspc.pics[49].x2 = wkspc.pics[49].x1 + wkspc.pics[49].w
        wkspc.pics[49].y2 = wkspc.pics[49].y1 + wkspc.pics[49].h

        arngr.get_wall_size()

        self.assertEqual(wkspc.height, 19)
        self.assertEqual(wkspc.width, 17)


class WorkspaceArrangerPopTestCase(unittest.TestCase):

    def setUp(self):

        server.app.config['TESTING'] = True
        seed.clean_db()

        seed_files = {
            'users': "seed/seed_test_users.txt",
            'pictures': "seed/seed_test_pictures.txt",
            'galleries': "seed/seed_test_galleries.txt",
            'memberships': "seed/seed_test_memberships.txt",
            'walls': "seed/seed_test_walls.txt",
            'placements': "seed/seed_test_placements.txt",
        }

        seed.seed_all(seed_files)

    def test_pop_any_n(self):

        # 1|2 | 8 | 10.5 |  |  |  |
        # 2|2 | 12 | 15 |  |  |  |
        # 3|2 | 7.5 | 9.5 |  |  |  |
        # 4|2 | 11 | 14 |  |  |  |
        # 5|2 | 8.5 | 6.5 |  |  |  |
        # 6|2 | 15 | 11 |  |  |  |
        # 7|2 | 19.5 | 16.5 |  |  |  |
        # 8|2 | 13 | 15.5 |  |  |  |

        for n in range(8):

            wkspc = ar.Workspace(1)
            arngr = ar.Arranger(wkspc)

            returned = arngr.pop_any_n(n)

            self.assertEqual(len(returned), n)

            for x in returned:
                self.assertIn(x, range(1, 9))
                self.assertNotIn(x, arngr.pics_remaining)

    def test_pop_tallest(self):

        wkspc = ar.Workspace(1)
        arngr = ar.Arranger(wkspc)

        returned = arngr.pop_tallest()
        self.assertEqual(returned, 7)
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_tallest()
        self.assertEqual(returned, 8)
        self.assertNotIn(returned, arngr.pics_remaining)

    def test_pop_widest(self):

        wkspc = ar.Workspace(1)
        arngr = ar.Arranger(wkspc)

        returned = arngr.pop_widest()
        self.assertEqual(returned, 7)
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_widest()
        self.assertEqual(returned, 6)
        self.assertNotIn(returned, arngr.pics_remaining)

    def test_pop_narrow(self):

        wkspc = ar.Workspace(1)
        arngr = ar.Arranger(wkspc)

        returned = arngr.pop_narrow()
        self.assertIn(returned, [1, 3])
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_narrow()
        self.assertIn(returned, [1, 3])
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_narrow()
        self.assertEqual(returned, 5)
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_narrow()
        self.assertEqual(returned, 4)
        self.assertNotIn(returned, arngr.pics_remaining)

    def test_pop_small(self):

        # Area assuming margin of 2
        # 1 = 130
        # 2 = 238
        # 3 = 120
        # 4 = 208
        # 5 = 99
        # 6 = 221
        # 7 = 418
        # 8 = 270

        wkspc = ar.Workspace(1)
        arngr = ar.Arranger(wkspc)

        returned = arngr.pop_small()
        self.assertIn(returned, [5, 3])
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_small()
        self.assertIn(returned, [5, 3])
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_small()
        self.assertEqual(returned, 1)
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_small()
        self.assertEqual(returned, 4)
        self.assertNotIn(returned, arngr.pics_remaining)

    def test_pop_large(self):

        # Area assuming margin of 2
        # 1 = 130
        # 2 = 238
        # 3 = 120
        # 4 = 208
        # 5 = 99
        # 6 = 221
        # 7 = 418
        # 8 = 270

        wkspc = ar.Workspace(1)
        arngr = ar.Arranger(wkspc)

        returned = arngr.pop_large()
        self.assertIn(returned, [7, 8])
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_large()
        self.assertIn(returned, [7, 8])
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_large()
        self.assertEqual(returned, 2)
        self.assertNotIn(returned, arngr.pics_remaining)

        returned = arngr.pop_large()
        self.assertEqual(returned, 6)
        self.assertNotIn(returned, arngr.pics_remaining)


class PicInitTestCase(unittest.TestCase):

    def setUp(self):

        server.app.config['TESTING'] = True

        seed.clean_db()
        User(user_id=4, username='foo', email='b@r', password='?')

    def test_init(self):

        # Dimensions need rounding
        picture = Picture(user_id=4, width=10.2, height=5.7)
        pic = ar.Pic(picture=picture, margin=1)
        self.assertEqual(pic.w, 12)
        self.assertEqual(pic.h, 7)
        self.assertIsNone(pic.x1)
        self.assertIsNone(pic.x2)
        self.assertIsNone(pic.y1)
        self.assertIsNone(pic.y2)

        # Only one dimension will be rounded
        picture = Picture(user_id=4, width=10, height=5.7)
        pic = ar.Pic(picture=picture, margin=1)
        self.assertEqual(pic.w, 11)
        self.assertEqual(pic.h, 7)
        self.assertIsNone(pic.x1)
        self.assertIsNone(pic.x2)
        self.assertIsNone(pic.y1)
        self.assertIsNone(pic.y2)

        # No margin
        picture = Picture(user_id=4, width=10, height=5.7)
        pic = ar.Pic(picture=picture, margin=0)
        self.assertEqual(pic.w, 10)
        self.assertEqual(pic.h, 6)
        self.assertIsNone(pic.x1)
        self.assertIsNone(pic.x2)
        self.assertIsNone(pic.y1)
        self.assertIsNone(pic.y2)

if __name__ == "__main__":
    unittest.main()
