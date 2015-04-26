from __future__ import unicode_literals, print_function

import sys, os, pip, re
import getopt
from subprocess import call

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

optional_modules = [
    ("Aristotle Glossary Extension","#!aristotle_glossary!"),
    ("Aristotle Dataset Extensions","#!aristotle_dse!"),
    ("Aristotle DDI Downloaders","#!aristotle_ddi!")
]

def install(package):
    pip.main(['install', package])

def valid_input(prompt,match):
    try:
        input = raw_input
    except:
        pass
    for i in range(5):
        check = input(prompt)
        if re.match(match, check):
            return check
    raise Exception

def setup_mdr(name="",extensions=[],force_install=False,dry_install=False):
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
        if do_install == 'y':
            print("Select extensions to install (y/n)")        
            for display, ext_token in optional_modules:
                do_ext = valid_input("  %s: "%display, yn ).lower()
                if do_ext == 'y':
                    extensions.append(ext_token)
    if extensions:
        find_and_remove(name,extensions)

    if dry_install:
        print("Performing dry run, no requirements installed.")
        print("You can finish installing by running - pip install requirements.txt - from the %s directory"%name)
        return 0
    elif force_install:
        print("Installing from requirements.txt")
    else:
        valid_input("Ready to install requirements? (y/n): ", yn)

    if not dry_install:
        print("Running django command to fetch all required static files")
        collect_static(name)

        print("You can now locally test your installed registry by running the command './manage.py runserver'")

def collect_static(name):
    call(["./%s/manage.py"%name, 'collectstatic'])
    return call 

def download_example_mdr():
    print("Attempting to retrieve example registry")
    command = "export"
    arg = "https://github.com/legostormtroopr/aristotle-metadata-registry/branches/plato/example_mdr/"
    call(["svn", command, arg])
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
            opts, args = getopt.getopt(argv[1:], "hn:df", ["help","name=","dry","force"])
            opts = dict(opts)
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    kwargs = {}
    if '-n' in opts.keys() or '--name' in opts.keys():
        kwargs['name']=opts.get('-n',opts.get('--name'))
    if '-d' in args or '--dry' in args:
        kwargs['dry_install']=True
    if '-f' in args or '--force' in args:
        kwargs['force_install']=True

    return setup_mdr(**kwargs)
        
if __name__ == "__main__":
    sys.exit(main())