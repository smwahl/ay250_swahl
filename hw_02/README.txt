############################################################################################
CalCalc.py
############################################################################################

Sean Wahl, University of California Berkeley
swahl@berkeley.edu

Calculator module for AY-250 python class.
Evaluates any string passed to it, and can be used from either the command line. And return
a numerical answer.
Interacts with the Wolfram|Alpha API what when asked what it thinks is a  'difficult'.
question. CalCalc then attempts to condense the result from wolfram alpha into a single 
numeric answer. It takes into account answers that include the words million,billion,etc.

############################################################################################
Command line Usage:
############################################################################################

positional arguments:
  string_to_eval1  String to be evaluate.

optional arguments:
  -h, --help       show this help message and exit
  -s               Force input to be evaluated with pythons eval()
  -w               Force input to be evaluated with wolfram alpha
  --version        show program's version number and exit

usage: CalCalc.py [-h] [-s] [-w] [--version] string_to_eval1

Examples:
$ python CalCalc.py -s '34*28'
$ 952

$ python CalCalc.py 'mass of the moon in kg'
$  7.3459e+22

############################################################################################
Script Usage:
############################################################################################

import CalCalc
CalCalc.calculate(''mass of the moon in kg')

############################################################################################
INSTALL
############################################################################################
Uncompress the tarbell and install using the following commands:

tar xzvf CalCalc-1.0.tar.gz
cd CalCalc-1.0
python setup.py install

