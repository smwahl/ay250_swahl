############################################################################################
CalCalc.py
############################################################################################

Sean Wahl, University of California Berkeley
swahl@berkeley.edu

Calculator module for AY-250 python class.
Evaluates any string passed to it, and can be used from either the command line. And return
a numerical answer.
Interacts with the Wolfram|Alpha API what when asked what it thinks is a  'difficult'.
question.

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
INSTALL
############################################################################################
Uncompress the tarbell and run the following:

python setup.py install

