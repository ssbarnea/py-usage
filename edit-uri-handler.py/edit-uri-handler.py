import logging
import os
import re
import subprocess
import shutil
import shlex
import sys
import traceback
import ctypes

from _winreg import *
from ctypes import c_int, WINFUNCTYPE, windll, wintypes
from ctypes.wintypes import HWND, LPCSTR, UINT

prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", None), (1, "flags", 0)
MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)
# use flag=1 to make it Yes|No
# See http://msdn.microsoft.com/en-us/library/windows/desktop/ms645505(v=vs.85).aspx)
try:
    import win32api, win32security, win32con
except:
    MessageBox("Python Windows extensions are missing, install them from http://sourceforge.net/projects/pywin32/files/pywin32/")
    sys.exit(-1)


"""
   iexplore calls with full URL:	edit://some
   chrome calls with:			//some

"""

# possible locations for source code, it is used for matching the path from inside the URL with the local one
# order is important
roots = [
        "C:/Automation/",
        "C:/Python_workspace/trunk/",
        "C:/AutomationScripts/",
        "C:/_autoscripts/",
		"C:/dev/auto",
        '~/workspace', # ~ is your %HOME% dude ;)
        ]

def isAdmin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

def isVirtualized():
    """
    Tells if the current process is running into virtualized mode (see Windows Registry Virtualization)
    """
    ph = win32api.GetCurrentProcess()
    th = win32security.OpenProcessToken(ph,win32con.MAXIMUM_ALLOWED)
    virtualized = win32security.GetTokenInformation(th, win32security.TokenVirtualizationEnabled)
    print 'TokenVirtualizationEnabled:', virtualized
    return virtualized

print isVirtualized()
sys.exit(0)

"""
[DllImport("advapi32.dll", EntryPoint = "GetTokenInformation",
    SetLastError = true)]
static extern bool GetTokenInformationNative(
    IntPtr TokenHandle,
    int TokenInformationClass,
    ref int TokenInformation,
    int TokenInformationLength,
    out int ReturnLength);

public bool IsVirtualized(IntPtr token)
    {
    bool virtualized = false;
    int len = 4;
    int info = 0;
    if (!GetTokenInformationNative(token, 24, ref info, len, outlen)) // 24 = TokenVirtualizationEnabled
    {
        string s = "Win32 error " +         Marshal.GetLastWin32Error().ToString();
        throw new Exception(s);
    }
    if(info != 0)
        virtualized = true;
    return virtualized;
}
"""


def getJetBrainsPath():
    """
    Returns the path to the newest executable of the installed version of one of the JetBrains tools (PyCharm or IDEA).

    If nothing is found it will return None.
    """
    products = ['PyCharm','IntelliJ IDEA'] # made PyCharm first but it should be adter IDEA
    exes = ["\\bin\\pycharm.exe", "\\bin\\idea.exe"]

    for i in range(len(products)):
        try:
            key =  OpenKey(HKEY_CURRENT_USER, "Software\\JetBrains\\%s" % products[i])
            versions = []
            try:
                j = 0
                while True:
                    versions.append(EnumKey(key,j))
                    j+=1
            except:
                pass
            versions.sort(reverse=True)
            for ver in versions:
                key =  OpenKey(HKEY_CURRENT_USER, "Software\\JetBrains\\%s\\%s" % (products[i],ver))
                path = QueryValue(key, None)
                if path:
                    path = path + exes[i]
                    if os.path.isfile(path):
                        return path
        except Exception, e:
            #print e
            #traceback.print_exc()
            pass

    return None

def getNotepadPlusPlusPath():
    try:
        key =  OpenKey(HKEY_LOCAL_MACHINE, "Software\\Notepad++")
        path = QueryValue(key, None)
        if path:
            path = path + "\\notepad++.exe"
            if os.path.isfile(path):
                return path
    except Exception, e:
        print e
        traceback.print_exc()
        pass
    return None

def getEditor():
    """
    Returns the full path to a editor. It will pick one of:
    * PyCharm
    * IntelliJ IDEA
    * Eclipse
    * Notepad++
    * Notepad (bleah!)
    """
    # 1: JetBrains tools have priority because they are commercial tools (and better)
    jet = getJetBrainsPath()
    if jet:
        return jet

    # 2: Eclipse sucks big time, they don't even have an installer and impossible to properly detect it's location, let's guess
    editors = [ # don't play with the order, it will change the app being used to open the files
        "C:\\dev\\eclipse\\eclipse.exe",
        "${PROGRAMFILES}\\eclipse\\eclipse.exe",
        "C:\\eclipse\\eclipse.exe",
        "${PROGRAMFILES}\\eclipse37\\eclipse.exe",
        ]
    for i in range(len(editors)):
        editor = os.path.abspath(os.path.expanduser(os.path.expandvars(editors[i])))
        if os.path.isfile(editor):
            return editor + " --launcher.openFile"

    # 3: Notepad++
    editor = getNotepadPlusPlusPath()
    if editor:
        return editor

    # 4: fallback, the infamous `notepad`
    return 'notepad.exe'

def sanitize(filename):
    """
    Use this function to auto-correct bad paths.

    For example if you keep the code in another location than the server.
    """
    filename = os.path.abspath(filename)

    if not os.path.isfile(filename):
        for local_root in local_roots:
            for root in roots:
                if filename.find(root, 0)==0: # if the URL-path starts with our root
                    tmp = filename.replace(root, local_root)
                    if os.path.isfile(tmp):
                        return tmp
    return filename

if __name__ == '__main__':

    src = os.path.abspath(sys.argv[0])

    # initialize logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    hdlr = logging.FileHandler(src + '.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)

    try:

        # now we try to detect the Python path, being careful not to open a command line by mistake
        logging.debug("Python version: %s (0x%.8x)" % (sys.version_info, sys.hexversion))
        logging.debug("PATH=%s" % os.environ['PATH'])
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen('where pythonw.exe', stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si)
        output = p.communicate()[0]
        if not p.returncode==0:
            # getting python from the registry for the unlucky ones that do not have it in PATH
            logging.warn("Unable to detect Python in PATH, you should add it.")

            key = OpenKey(HKEY_CLASSES_ROOT, r"Python.File\shell\open\command")
            if key:
                python = QueryValue(key, None)
                python = shlex.split(python)[0]
                python = os.path.dirname(python) + "\\pythonw.exe" # we want to use pythonw.exe not python.exe
            if not key or not os.path.isfile(python):
                raise Exception("Unable to detect python, where returned %s (%s)" % (p.returncode, output))
        else:
            logging.debug(output.split("\r\n"))
            python = os.path.dirname(output.split()[0]) + "\\pythonw.exe"# first line

        prefix = "\"%s\"" % python
        #prefix = "pythonw"
        #prefix = ""
        #prefix = "cmd /C pythonw"
        # "pythonw" WORKED (@sorin) but will open a command window
        # "cmd /K pythonw" WORKED (with window)
        # "cmd /C pythonw" WORKED (with window)
        # "cmd pythonw" FAILED
        # strange: it seem that running just with "pythonw ..." fails on some computers even if pythonw is in path
        if prefix and prefix[-1]!=' ':
            prefix += ' '

        # now we build the list of local root paths, keeping only those that do exist locally
        local_roots = []
        for i in range(len(roots)):
            roots[i] = os.path.abspath(os.path.expanduser(roots[i]))
            if os.path.isdir(roots[i]):
                local_roots.append(roots[i])
        if not local_roots:
            raise Exception("Unable to detect any local root directory in `roots` list: \n\n%s" % ("\n".join(roots)))

        logging.info("Called with: " + " ".join(sys.argv))

        if len(sys.argv)<2:
            # Called without parameters, this will trigger the build-in installer

            dst = os.path.dirname(python) + "\\" + os.path.basename(sys.argv[0])

            if src != dst:
                # not it's clear that we are supposed to install, but we need admin privileges for this

                result = MessageBox(
                    text="Do you want me to install edit:// protocol handler script?" \
                         "\n\nInstall source: %s" \
                         "\nInstall destination: %s" % (src, dst),
                    caption=sys.argv[0],
                    flags = 1)
                if result == 1:
                    try:
                        #if not isAdmin():
                        #    raise Exception("You do not have Administrator priviledges so install will fail. Run me as admin.")

                        logging.info("Trying to install to %s", dst)
                        shutil.copyfile(src, dst)
                        # install protocol handler
                        key = CreateKey(HKEY_CLASSES_ROOT, "edit")
                        ret = SetValue(key, None,  REG_SZ, "URL:edit Protocol")
                        ret = SetValueEx(key, "URL Protocol", 0, REG_SZ, "")

                        key = CreateKey(HKEY_CLASSES_ROOT, "edit\\shell\\open\\command")
                        ret = SetValue(key, None, REG_SZ, prefix + '"%s" "%%1"' % dst)
                        key = CreateKey(HKEY_CLASSES_ROOT, "edit\\shell\\edit\\command")
                        ret = SetValue(key, None,  REG_SZ, prefix + '"%s" "%%1"' % dst)
                    except Exception, e:
                        logging.error(e)
                        if not isAdmin():
                            raise Exception(str(e) + "\n\nOne possible reason could be the lack of privileges, so please run me as Administrator in order to be able to install.")
                        raise e

                sys.exit(0)
            else:
                MessageBox(text="Called without filename parameter and the script is already installed.\n\nSo there is nothing to do!", caption=sys.argv[0])
                sys.exit(0)

        if sys.argv[1][:7] == "edit://":
            filename = sys.argv[1].split("edit://")[1].strip('/')
        else:
            raise(Exception("Parameter '%s' is not using edit:// syntax." % sys.argv[1]))

        filename = re.sub("^([a-zA-Z])/(.*)$", r"\1:/\2", filename)
        logging.debug("Local filename: %s" % filename)

        filename = os.path.abspath(filename)

        origFilename = filename
        filename = sanitize(filename)
        logging.debug("Sanitized filename: %s" % filename)

        if not os.path.isfile(filename):
                MessageBox(text="File not found: %s\n\nOriginal filename: %s" % (filename, origFilename), caption=sys.argv[0])
        else:
            try:
                os.startfile(filename, "edit")
            except WindowsError, e:
                if e.winerror == 1155: # file type has no associated 'edit' action.
                    cmd = getEditor() + " " + filename # this cannot fail, it will return notepad in the worst case
                    logging.info("Execute: %s" % cmd)
                    subprocess.call(cmd, shell=False)

    except Exception, e:
        msg = str(e) + "\n\n" + traceback.format_exc()
        logging.error(e)
        MessageBox(text=msg, caption=" ".join(sys.argv))
        sys.exit(-1)
