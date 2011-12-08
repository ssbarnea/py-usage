import unittest
import subprocess
import os
import sys


def execute(cmd):
    x = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE, shell=True)
    return x.communicate()[0].rstrip()

class DefaultWidgetSizeTestCase(unittest.TestCase):

    def setUp(self):
        if not os.path.isfile(os.path.abspath(__file__)):
            raise Exeption
	
        self.dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"b")


    def test1(self):
        cmd = "python b/c.py"
        ret = execute(cmd)
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

    def test2(self):
        cmd = "python c.py"
	os.chdir("b")
        ret = execute(cmd)
	os.chdir("..")
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

    def test3(self):
        if os.name == 'nt':
            cmd = "c.py"
        else:
            cmd = "./c.py"
	os.chdir("b")
        ret = execute(cmd)
	os.chdir("..")
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

    def test4(self):
        cmd = "python some.py"
        ret = execute(cmd)
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

    def test5(self):
        cmd = "python some2.py"
        ret = execute(cmd)
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

    def test6(self):
        cmd = "pythonw some.py |more"
        ret = execute(cmd)
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

    def test7(self):
        cmd = "python -c \"execfile('b/c.py')\""
        ret = execute(cmd)
        self.assertEqual(ret, self.dir, '`%s` output was `%s` instead of `%s`' % (cmd,ret,self.dir))

if __name__ == '__main__':
     unittest.main()






