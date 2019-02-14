# https://www.blog.pythonlibrary.org/2016/07/07/python-3-testing-an-intro-to-unittest/

import unittest

class extract_sourcenote_metadata_Test(unittest.TestCase):

    sourcenote_examples = [
        {
            "content":'''[Repealed 2008, 322:12, I, eff. Aug. 31, 2008.]'''
            ,"source":'http://www.gencourt.state.nh.us/rsa/html/II/30/30-5.htm'
        },
        {
            "content":'''Source. 1987, 126:1, eff. July 6, 1987.'''
            ,"Source":'http://www.gencourt.state.nh.us/rsa/html/I/3-B/3-B-1.htm'
        },
        {
            "content":'''Source. GS 18:4. GL 19:4. PS 20:4. PL 19:5. RL 27:6.'''
            ,"source":'http://www.gencourt.state.nh.us/rsa/html/I/4/4-23.htm'
        },
        {
            "content":'''Source. 1903, 125:2. PL 15:7. RL 22:7. RSA 6:8. 1969, 245:1. 1973, 224:1. 1991, 268:3. 1999, 1:3. 2001, 2:1. 2008, 120:3. 2010, 7:1, eff. July 3, 2010. 2013, 97:1, eff. Aug. 19, 2013. 2015, 272:46, eff. Oct. 1, 2015. 2016, 230:12, eff. Aug. 8, 2016.'''
            ,"source":'http://www.gencourt.state.nh.us/rsa/html/I/6/6-8.htm'
        },
        {
            "content":""
            ,"source":'http://www.gencourt.state.nh.us/rsa/html/II/30/30-5.htm'
        },
        {
            "content":None
            ,"source":"Bad data load"
        }
    ]

    def test_blank(self):
        pass