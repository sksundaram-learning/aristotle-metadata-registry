from __future__ import unicode_literals, print_function

import sys, os, pip, re
import getopt
from subprocess import call

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

optional_modules = [
    ("Aristotle Glossary Extension","#!aristotle-glossary!"),
    ("Aristotle Dataset Extensions","#!aristotle-dse!")
    ("Aristotle DDI Downloaders","#!aristotle-ddi!")
]

def install(package):
    pip.main(['install', package])

def valid_input(prompt,match):
    for i in range(5):
        check = input(prompt)
        if re.match(match, check_name):
            return check
    raise Exception

def setup_mdr(name="",extensions=[]):
    name_regex = '^[a-z][a-z_]*$'
    if not re.match(name_regex, name):
        name = valid_input("Enter the system name for your registry (lowercase letters and underscores ONLY): ",name_regex)

    try:
        download_example_mdr()
    except:
        print ("Downloading of example settings failed, this script requires subversion to be installed and executable from the command line.")
        print ("Try running the script again, if this continues to fail, try:")
        print ("   1. manually downloading the folder to this directory and ALL its contents from github: https://github.com/aristotle-mdr/aristotle-metadata-registry/tree/master/example_mdr")
        print ("   2. creating a new project using the django-admin tools and manually setting up a project")
        raise

    os.rename('example_mdr',name)
    os.rename(os.path.join(name,'example_mdr'),os.path.join(name,name))

    yn = '^[YyNn]?$' # yes/no regex
    if not extensions:
        do_install = valid_input("Do you wish to install any additional Aristotle modules? (y/n): ", yn ).lower()
        if do_install is 'y':
            print("Select extensions to install (y/n)")        
            for display, ext_token in optional_modules:
                do_ext = valid_input("  %s: "%display, yn ).lower()
                if do_ext is 'y':
                    extensions.append(ext_token)
    if extensions:
        find_and_remove(name,extensions)
    print("You can now locally test your installed registry by running the command './manage.py runserver'")

def collect_static():
    call(["django-admin", 'collectstatic'])
    return call

def download_example_mdr():
    command = "export https://github.com/aristotle-mdr/aristotle-metadata-registry/trunk/example_mdr/"
    call(["svn", command])
    return call

def find_and_remove(mydir,extensions):
    """Really naive find and replace lovingly borrowed from stack overflow - http://stackoverflow.com/a/4205918/764357"""
    for dname, dirs, files in os.walk(mydir):
        for fname in files:
            if fname.endswith(('py','txt','rst')):
                fpath = os.path.join(dname, fname)
                with open(fpath) as f:
                    s = f.read()
                for ext in extensions:
                    s = s.replace(ext, '')
                with open(fpath, "w") as f:
                    f.write(s)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    return setup_mdr()
        
if __name__ == "__main__":
    sys.exit(main())